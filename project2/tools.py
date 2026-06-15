"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()

# Free Groq model recommended for this project.
MODEL = "llama-3.3-70b-versatile"


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform
    """
    listings = load_listings()

    # Break the description into lowercase keywords for relevance scoring.
    keywords = [w for w in description.lower().split() if w]

    scored: list[tuple[int, dict]] = []
    for listing in listings:
        # Price filter (inclusive). Skip if max_price is None.
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter (case-insensitive substring). Skip if size is None.
        if size is not None and size.lower() not in listing["size"].lower():
            continue

        # Build one searchable text blob from the relevant fields.
        haystack = " ".join([
            listing["title"],
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
        ]).lower()

        # Score = how many query keywords appear in the listing text.
        score = sum(1 for kw in keywords if kw in haystack)
        if score > 0:
            scored.append((score, listing))

    # Highest score first.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.
    """
    item_desc = (
        f"{new_item.get('title', 'an item')} "
        f"(category: {new_item.get('category', 'unknown')}, "
        f"colors: {', '.join(new_item.get('colors', []))}, "
        f"style: {', '.join(new_item.get('style_tags', []))})"
    )

    items = wardrobe.get("items", [])

    if not items:
        # Empty wardrobe → general styling advice, not a crash.
        prompt = (
            f"A user is considering buying this secondhand item: {item_desc}.\n"
            "They have not entered any wardrobe yet. Suggest 1-2 complete outfit "
            "ideas built around this item using common wardrobe staples. Mention "
            "what kinds of pieces pair well and what vibe the look gives. "
            "Keep it short and practical."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {w.get('name', 'item')} "
            f"({w.get('category', '')}; {', '.join(w.get('colors', []))})"
            for w in items
        )
        prompt = (
            f"A user is considering buying this secondhand item: {item_desc}.\n\n"
            f"Here is their current wardrobe:\n{wardrobe_lines}\n\n"
            "Suggest 1-2 complete outfit combinations that pair the new item with "
            "specific named pieces from their wardrobe. Refer to the wardrobe pieces "
            "by name. Keep it short, concrete, and practical."
        )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        # Don't crash the agent if the API call fails.
        return f"Couldn't generate an outfit suggestion right now ({exc}). Try again in a moment."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)
    """
    # Guard: no usable outfit → return an error string, never raise.
    if not outfit or not outfit.strip():
        return "Can't write a fit card without an outfit suggestion — try a different search."

    title = new_item.get("title", "this piece")
    price = new_item.get("price", "?")
    platform = new_item.get("platform", "online")

    prompt = (
        "Write a short, casual social media caption (2-4 sentences) for a thrifted "
        "outfit, like a real OOTD post — not a product description.\n\n"
        f"Item: {title}\n"
        f"Price: ${price}\n"
        f"Platform: {platform}\n"
        f"Outfit: {outfit}\n\n"
        "Mention the item name, price, and platform naturally (once each). "
        "Capture the vibe of the outfit. Sound authentic and a little excited."
    )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,  # higher temp → varied captions each run
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"Couldn't write a fit card right now ({exc}). Try again in a moment."
