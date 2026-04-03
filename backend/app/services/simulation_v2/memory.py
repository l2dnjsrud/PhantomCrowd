"""Agent memory system: conversation history, relationships, sentiment tracking."""

from dataclasses import dataclass, field


@dataclass
class RelationshipMemory:
    """Track an agent's relationship with another agent."""
    agent_name: str
    interactions: int = 0
    sentiment_toward: float = 0.0  # -1.0 to 1.0
    last_action: str = ""  # What they last did to/about this agent


@dataclass
class AgentMemory:
    """Persistent memory for a single agent across simulation rounds."""

    # Conversation history (what I said and saw)
    my_posts: list[str] = field(default_factory=list)
    seen_posts: list[dict] = field(default_factory=list)  # {"agent": name, "content": text, "round": N}

    # Relationships with other agents
    relationships: dict[str, RelationshipMemory] = field(default_factory=dict)

    # Sentiment journey
    sentiment_history: list[dict] = field(default_factory=list)  # {"round": N, "sentiment": str, "score": float}

    # Accumulated knowledge/opinions
    opinions: list[str] = field(default_factory=list)  # Key opinions formed during simulation

    def record_my_action(self, round_num: int, action_type: str, content: str,
                         target_agent: str = "", sentiment: str = "neutral", score: float = 0.0):
        """Record an action I took."""
        if action_type == "post" and content:
            self.my_posts.append(content[:200])

        if target_agent:
            rel = self.relationships.get(target_agent)
            if not rel:
                rel = RelationshipMemory(agent_name=target_agent)
                self.relationships[target_agent] = rel
            rel.interactions += 1
            rel.last_action = action_type
            # Adjust sentiment toward target based on my action
            if action_type in ("like", "share", "reply"):
                rel.sentiment_toward = min(1.0, rel.sentiment_toward + 0.2)
            elif action_type == "dislike":
                rel.sentiment_toward = max(-1.0, rel.sentiment_toward - 0.3)

        self.sentiment_history.append({
            "round": round_num,
            "sentiment": sentiment,
            "score": score,
        })

    def record_seen_post(self, agent_name: str, content: str, round_num: int):
        """Record a post I saw in my feed."""
        self.seen_posts.append({
            "agent": agent_name,
            "content": content[:200],
            "round": round_num,
        })
        # Keep last 20
        if len(self.seen_posts) > 20:
            self.seen_posts = self.seen_posts[-20:]

    def add_opinion(self, opinion: str):
        """Record an opinion formed during simulation."""
        self.opinions.append(opinion)
        if len(self.opinions) > 10:
            self.opinions = self.opinions[-10:]

    def get_context_prompt(self) -> str:
        """Generate a memory context string for the agent's LLM prompt."""
        parts = []

        # My recent posts
        if self.my_posts:
            parts.append("MY PREVIOUS POSTS:")
            for p in self.my_posts[-5:]:
                parts.append(f"  - \"{p}\"")

        # Relationships
        if self.relationships:
            parts.append("\nMY RELATIONSHIPS WITH OTHER USERS:")
            for name, rel in sorted(self.relationships.items(), key=lambda x: -abs(x[1].sentiment_toward))[:8]:
                feeling = "positive" if rel.sentiment_toward > 0.2 else "negative" if rel.sentiment_toward < -0.2 else "neutral"
                parts.append(f"  - @{name}: {feeling} ({rel.interactions} interactions, last: {rel.last_action})")

        # Sentiment journey
        if len(self.sentiment_history) > 1:
            parts.append("\nMY SENTIMENT OVER TIME:")
            for sh in self.sentiment_history[-5:]:
                parts.append(f"  Round {sh['round']}: {sh['sentiment']} ({sh['score']})")

        # Opinions
        if self.opinions:
            parts.append("\nMY FORMED OPINIONS:")
            for o in self.opinions[-5:]:
                parts.append(f"  - {o}")

        # Recent feed
        if self.seen_posts:
            parts.append("\nRECENT POSTS I SAW:")
            for sp in self.seen_posts[-5:]:
                parts.append(f"  @{sp['agent']}: \"{sp['content'][:80]}\"")

        return "\n".join(parts) if parts else "No memory yet — this is my first interaction."

    def get_sentiment_trend(self) -> str:
        """Get a summary of sentiment change over time."""
        if len(self.sentiment_history) < 2:
            return "stable"
        first = self.sentiment_history[0]["score"]
        last = self.sentiment_history[-1]["score"]
        diff = last - first
        if diff > 0.3:
            return "increasingly positive"
        elif diff < -0.3:
            return "increasingly negative"
        return "stable"
