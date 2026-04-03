"""Update knowledge graph with simulation results (feedback loop)."""

import os
import networkx as nx
from app.services.simulation_v2.engine import Action


def update_graph_with_actions(graph_dir: str, actions: list[Action]):
    """Add simulation interaction data back into the knowledge graph.

    This creates a feedback loop: content → graph → simulation → graph update.
    New nodes for active agents and edges for their interactions are added.
    """
    graph_file = os.path.join(graph_dir, "graph_chunk_entity_relation.graphml")
    if not os.path.exists(graph_file):
        return

    g = nx.read_graphml(graph_file)

    # Track agent interactions
    agent_interactions: dict[str, dict] = {}  # agent -> {action_count, sentiment_sum, targets}

    for action in actions:
        name = action.agent_name
        if name not in agent_interactions:
            agent_interactions[name] = {
                "action_count": 0,
                "sentiment_sum": 0.0,
                "targets": set(),
                "action_types": [],
                "profile": action.agent_profile,
            }
        info = agent_interactions[name]
        info["action_count"] += 1
        info["sentiment_sum"] += action.sentiment_score or 0
        info["action_types"].append(action.action_type)
        if action.target_agent:
            info["targets"].add(action.target_agent)

    # Add top influencer agents as nodes
    sorted_agents = sorted(
        agent_interactions.items(),
        key=lambda x: x[1]["action_count"],
        reverse=True,
    )

    for agent_name, info in sorted_agents[:20]:
        node_id = f"SimAgent:{agent_name}"
        if node_id not in g.nodes:
            avg_sentiment = info["sentiment_sum"] / max(info["action_count"], 1)
            g.add_node(
                node_id,
                entity_type="SimulatedAgent",
                description=f"Simulated agent with {info['action_count']} actions, avg sentiment {avg_sentiment:.2f}",
                action_count=str(info["action_count"]),
                avg_sentiment=str(round(avg_sentiment, 2)),
            )

        # Add INTERACTED_WITH edges
        for target in info["targets"]:
            target_id = f"SimAgent:{target}"
            edge_key = f"{node_id}->{target_id}"
            if not g.has_edge(node_id, target_id):
                g.add_edge(
                    node_id, target_id,
                    description="interacted_with",
                    label="INTERACTED_WITH",
                    weight="1.0",
                )

    # Add DISCUSSED edges from agents to content entities
    content_nodes = [n for n in g.nodes if not n.startswith("SimAgent:")]
    for agent_name, info in sorted_agents[:10]:
        agent_node = f"SimAgent:{agent_name}"
        if agent_node in g.nodes and content_nodes:
            # Connect to most relevant content node (first one as proxy)
            for cn in content_nodes[:3]:
                if not g.has_edge(agent_node, cn):
                    g.add_edge(
                        agent_node, cn,
                        description="discussed_about",
                        label="DISCUSSED",
                        weight="0.5",
                    )

    # Save updated graph
    nx.write_graphml(g, graph_file)

    return {
        "agents_added": min(len(sorted_agents), 20),
        "total_nodes": g.number_of_nodes(),
        "total_edges": g.number_of_edges(),
    }
