"""Simple, explainable ticket matching using Python basics only.

This is deliberately not an AI model. It compares important words so an agent
can see why a past ticket was suggested. It is a good small prototype and can
later be replaced by embeddings or a trained model.
"""

import re
from typing import Any

# Very common words do not help us tell one support issue from another.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "can", "customer", "did", "do", "does", "for", "from", "get", "got",
    "has", "have", "he", "her", "here", "i", "in", "into", "is", "it",
    "its", "me", "my", "of", "on", "or", "our", "please", "says", "she",
    "so", "that", "the", "their", "them", "there", "they", "this", "to",
    "us", "was", "we", "were", "when", "with", "would", "you", "your",
}


def important_words(text: str) -> set[str]:
    """Turn text into a set of lowercase words, removing common filler words."""
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {word for word in words if len(word) > 1 and word not in STOP_WORDS}


def ticket_words(ticket: dict[str, Any]) -> set[str]:
    """Collect words from the fields that describe the issue."""
    tags = ticket.get("tags", [])
    if isinstance(tags, list):
        tags_text = " ".join(str(tag) for tag in tags)
    else:
        tags_text = str(tags or "")

    text = " ".join(
        [
            str(ticket.get("subject", "")),
            str(ticket.get("description", "")),
            str(ticket.get("category", "")),
            tags_text,
        ]
    )
    return important_words(text)


def find_similar_tickets(
    new_ticket: dict[str, Any],
    historical_tickets: list[dict[str, Any]],
    limit: int = 3,
    threshold: float = 0.08,
) -> dict[str, Any]:
    """Return the best matches, or clearly say that no good match was found.

    Score = shared important words / all unique important words in either ticket.
    This is called Jaccard similarity. It is easy to explain and scores 0 to 1.
    """
    new_words = ticket_words(new_ticket)
    scored_matches = []

    for old_ticket in historical_tickets:
        # Do not match a ticket to itself if the same ID is supplied.
        if new_ticket.get("ticket_id") == old_ticket.get("ticket_id"):
            continue

        old_words = ticket_words(old_ticket)
        shared_words = new_words.intersection(old_words)
        all_words = new_words.union(old_words)

        if not all_words:
            score = 0.0
        else:
            score = len(shared_words) / len(all_words)

        # Only return matches that pass our minimum relevance threshold.
        if score >= threshold:
            result = dict(old_ticket)
            result["similarity_score"] = round(score, 3)
            result["shared_terms"] = sorted(shared_words)
            scored_matches.append(result)

    # Highest score first. Ticket ID makes ties predictable for demos and tests.
    scored_matches.sort(
        key=lambda item: (-item["similarity_score"], item.get("ticket_id", ""))
    )
    matches = scored_matches[:limit]

    return {
        "match_found": len(matches) > 0,
        "message": (
            "Similar historical tickets found. Review their resolutions before replying."
            if matches
            else "No strong historical match found. Follow the normal support investigation process."
        ),
        "matches": matches,
    }
