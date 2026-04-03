import os
import asyncio
import numpy as np
import networkx as nx

from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete
from lightrag.utils import EmbeddingFunc

from app.core.config import settings

# Use sync ollama for embedding (avoids async issues)
try:
    import ollama as ollama_client
except ImportError:
    ollama_client = None

GRAPH_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "graphs")


async def _custom_embed(texts: list[str]) -> np.ndarray:
    """Custom embedding using nomic-embed-text via Ollama."""
    if ollama_client is None:
        raise RuntimeError("ollama package not installed")
    response = ollama_client.embed(model="nomic-embed-text", input=texts)
    return np.array(response["embeddings"])


class GraphBuilder:
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.working_dir = os.path.join(GRAPH_BASE_DIR, campaign_id)
        os.makedirs(self.working_dir, exist_ok=True)
        self.rag = None

    async def initialize(self):
        """Initialize LightRAG instance."""
        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=ollama_model_complete,
            llm_model_name=settings.llm_model,
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=_custom_embed,
            ),
        )
        await self.rag.initialize_storages()

    async def build_graph(self, content: str, context_text: str | None = None) -> dict:
        """Build knowledge graph from content + context."""
        if not self.rag:
            await self.initialize()

        # Combine content and context
        full_text = content
        if context_text:
            full_text += "\n\n--- ADDITIONAL CONTEXT ---\n\n" + context_text

        # Insert into LightRAG (triggers entity extraction)
        await self.rag.ainsert(full_text)

        # Read the generated graph
        graph_data = self._read_graph()
        return graph_data

    def _read_graph(self) -> dict:
        """Read the NetworkX graph from LightRAG storage."""
        graph_file = os.path.join(self.working_dir, "graph_chunk_entity_relation.graphml")
        if not os.path.exists(graph_file):
            return {"nodes": [], "edges": [], "stats": {"nodes": 0, "edges": 0}}

        g = nx.read_graphml(graph_file)

        nodes = []
        for node_id, data in g.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": node_id,
                "type": data.get("entity_type", "unknown"),
                "description": data.get("description", ""),
            })

        edges = []
        for u, v, data in g.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "label": data.get("description", data.get("label", "related_to"))[:60],
                "weight": float(data.get("weight", 1.0)),
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {"nodes": len(nodes), "edges": len(edges)},
        }

    async def query(self, question: str, mode: str = "hybrid") -> str:
        """Query the knowledge graph."""
        if not self.rag:
            await self.initialize()
        result = await self.rag.aquery(question, param=QueryParam(mode=mode))
        return result or ""

    def get_entities(self) -> list[dict]:
        """Get all entities from the graph."""
        graph_data = self._read_graph()
        return graph_data["nodes"]

    def get_graph_data(self) -> dict:
        """Get full graph data for visualization."""
        return self._read_graph()
