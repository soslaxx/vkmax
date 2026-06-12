from __future__ import annotations

REACTION_ALIASES: dict[str, str] = {
    "like": "\U0001f44d", "thumbsup": "\U0001f44d", "thumbs_up": "\U0001f44d",
    "dislike": "\U0001f44e", "thumbsdown": "\U0001f44e",
    "fire": "\U0001f525", "heart": "\u2764\ufe0f", "laugh": "\U0001f923",
    "cry": "\U0001f62d", "party": "\U0001f389", "tada": "\U0001f389",
    "ok": "\U0001f44c", "clap": "\U0001f44f", "100": "\U0001f4af",
    "skull": "\U0001f480", "rocket": "\U0001f680", "poop": "\U0001f4a9",
    "angry": "\U0001f621", "think": "\U0001f914", "thinking": "\U0001f914",
    "cool": "\U0001f60e", "kiss": "\U0001f618", "love": "\U0001f970",
    "pray": "\U0001f64f", "eyes": "\U0001f440", "strong": "\U0001f4aa",
    "muscle": "\U0001f4aa", "wave": "\U0001f44b", "hello": "\U0001f44b",
    "crown": "\U0001f451", "check": "\u2705", "star": "\U0001f929",
    "devil": "\U0001f608", "angel": "\U0001f607", "wink": "\U0001f609",
    "scream": "\U0001f631", "clown": "\U0001f921", "lightning": "\u26a1\ufe0f",
    "vomit": "\U0001f92e", "explode": "\U0001f92f", "shock": "\U0001f62e",
    "sad": "\u2639\ufe0f", "smile": "\U0001f642", "joy": "\U0001f602",
}


def resolve_reaction(reaction: str) -> str:
    if not reaction:
        raise ValueError("reaction is empty")
    return REACTION_ALIASES.get(reaction.lower(), reaction)
