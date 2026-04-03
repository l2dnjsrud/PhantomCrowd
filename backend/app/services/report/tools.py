"""ReportAgent tools for searching knowledge graph, actions, and interviewing agents."""

import json
from collections import Counter
from dataclasses import dataclass

from app.services.simulation_v2.engine import Action


@dataclass
class ToolResult:
    tool: str
    query: str
    result: str


def graph_search(graph_context: str, query: str) -> ToolResult:
    """Search the knowledge graph for relevant entities and relationships."""
    # In a full implementation, this would query LightRAG directly.
    # For now, we search within the pre-fetched graph context.
    query_lower = query.lower()
    lines = graph_context.split("\n")
    relevant = [l for l in lines if any(w in l.lower() for w in query_lower.split())]
    result = "\n".join(relevant[:20]) if relevant else "No relevant graph data found."
    return ToolResult(tool="graph_search", query=query, result=result)


def action_search(actions: list[Action], filters: dict) -> ToolResult:
    """Search simulation actions with filters.

    Filters:
        agent: str — filter by agent name
        action_type: str — post/reply/share/like/dislike
        sentiment: str — positive/negative/neutral/mixed
        round_min/round_max: int — round range
        has_content: bool — only actions with text content
    """
    filtered = actions

    if "agent" in filters:
        filtered = [a for a in filtered if filters["agent"].lower() in a.agent_name.lower()]
    if "action_type" in filters:
        filtered = [a for a in filtered if a.action_type == filters["action_type"]]
    if "sentiment" in filters:
        filtered = [a for a in filtered if a.sentiment == filters["sentiment"]]
    if "round_min" in filters:
        filtered = [a for a in filtered if a.round_num >= filters["round_min"]]
    if "round_max" in filters:
        filtered = [a for a in filtered if a.round_num <= filters["round_max"]]
    if filters.get("has_content"):
        filtered = [a for a in filtered if a.content and len(a.content) > 5]

    # Format results
    lines = []
    for a in filtered[:30]:
        line = f"[R{a.round_num}] @{a.agent_name} ({a.action_type}, {a.sentiment} {a.sentiment_score})"
        if a.content:
            line += f": {a.content[:120]}"
        if a.target_agent:
            line += f" → @{a.target_agent}"
        lines.append(line)

    summary = f"Found {len(filtered)} actions matching filters."
    if filtered:
        sentiments = Counter(a.sentiment for a in filtered)
        types = Counter(a.action_type for a in filtered)
        summary += f" Sentiments: {dict(sentiments)}. Types: {dict(types)}."

    result = summary + "\n\n" + "\n".join(lines)
    return ToolResult(tool="action_search", query=json.dumps(filters), result=result)


def sentiment_aggregate(actions: list[Action], segment: dict | None = None) -> ToolResult:
    """Compute sentiment statistics, optionally segmented by demographic.

    Segment filters:
        age_min/age_max: int
        gender: str
        occupation: str (partial match)
    """
    filtered = actions

    if segment:
        def matches(a: Action) -> bool:
            profile = a.agent_profile or {}
            if "age_min" in segment and profile.get("age", 0) < segment["age_min"]:
                return False
            if "age_max" in segment and profile.get("age", 99) > segment["age_max"]:
                return False
            if "gender" in segment and profile.get("gender", "") != segment["gender"]:
                return False
            if "occupation" in segment:
                occ = profile.get("occupation", "").lower()
                if segment["occupation"].lower() not in occ:
                    return False
            return True
        filtered = [a for a in filtered if matches(a)]

    if not filtered:
        return ToolResult(
            tool="sentiment_aggregate",
            query=json.dumps(segment or {}),
            result="No actions match the segment filter.",
        )

    scores = [a.sentiment_score for a in filtered if a.sentiment_score is not None]
    sentiments = Counter(a.sentiment for a in filtered if a.sentiment)
    engagements = Counter(a.action_type for a in filtered)

    avg_score = sum(scores) / len(scores) if scores else 0
    positive_pct = sentiments.get("positive", 0) / len(filtered) * 100
    negative_pct = sentiments.get("negative", 0) / len(filtered) * 100
    share_rate = engagements.get("share", 0) / len(filtered) * 100
    reply_rate = engagements.get("reply", 0) / len(filtered) * 100

    result = (
        f"Segment: {json.dumps(segment or 'all')}\n"
        f"Total actions: {len(filtered)}\n"
        f"Avg sentiment score: {avg_score:.3f}\n"
        f"Positive: {positive_pct:.1f}%, Negative: {negative_pct:.1f}%\n"
        f"Sentiment distribution: {dict(sentiments)}\n"
        f"Engagement distribution: {dict(engagements)}\n"
        f"Share rate: {share_rate:.1f}%, Reply rate: {reply_rate:.1f}%\n"
    )

    # Per-round trend
    rounds = sorted(set(a.round_num for a in filtered))
    if len(rounds) > 1:
        result += "\nTrend by round:\n"
        for r in rounds:
            r_actions = [a for a in filtered if a.round_num == r]
            r_scores = [a.sentiment_score for a in r_actions if a.sentiment_score is not None]
            r_avg = sum(r_scores) / len(r_scores) if r_scores else 0
            r_sent = Counter(a.sentiment for a in r_actions)
            result += f"  Round {r}: avg={r_avg:.2f}, {dict(r_sent)}\n"

    return ToolResult(tool="sentiment_aggregate", query=json.dumps(segment or {}), result=result)


def identify_influencers(actions: list[Action], top_n: int = 5) -> ToolResult:
    """Identify top influencer agents based on engagement they generated."""
    # Count how many times each agent was replied to or shared
    influence_score: dict[str, float] = {}

    for a in actions:
        if a.target_agent:
            influence_score[a.target_agent] = influence_score.get(a.target_agent, 0)
            if a.action_type == "share":
                influence_score[a.target_agent] += 3
            elif a.action_type == "reply":
                influence_score[a.target_agent] += 2
            elif a.action_type == "like":
                influence_score[a.target_agent] += 1

    # Also count post volume
    post_counts = Counter(a.agent_name for a in actions if a.action_type == "post")
    for agent, count in post_counts.items():
        influence_score[agent] = influence_score.get(agent, 0) + count * 0.5

    sorted_agents = sorted(influence_score.items(), key=lambda x: x[1], reverse=True)[:top_n]

    lines = []
    for agent, score in sorted_agents:
        agent_actions = [a for a in actions if a.agent_name == agent]
        profile = agent_actions[0].agent_profile if agent_actions else {}
        sentiments = Counter(a.sentiment for a in agent_actions)
        lines.append(
            f"@{agent} (score: {score:.1f}) — {profile.get('age', '?')}y, "
            f"{profile.get('occupation', '?')}, sentiments: {dict(sentiments)}"
        )

    result = f"Top {top_n} influencers:\n" + "\n".join(lines)
    return ToolResult(tool="identify_influencers", query=str(top_n), result=result)
