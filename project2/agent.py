"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import json

from tools import search_listings, suggest_outfit, create_fit_card, _get_groq_client, MODEL


# ── query parsing ─────────────────────────────────────────────────────────────

_PARSE_PROMPT = (
    "You extract search parameters from a secondhand-clothing search query.\n"
    "Return ONLY a JSON object with exactly these keys:\n"
    '  "description": string — the item keywords only (no price/size words)\n'
    '  "size": string or null — e.g. "M", "8", "XXS" (normalize "medium"->"M", '
    '"large"->"L", "small"->"S")\n'
    '  "max_price": number or null — the price ceiling as a plain number\n\n'
    "Examples:\n"
    'Query: "vintage graphic tee under $30" -> '
    '{"description": "vintage graphic tee", "size": null, "max_price": 30}\n'
    'Query: "90s track jacket in size medium" -> '
    '{"description": "90s track jacket", "size": "M", "max_price": null}\n'
    'Query: "cheap black combat boots size 8" -> '
    '{"description": "black combat boots", "size": "8", "max_price": null}\n\n'
    "Query: "
)


def _parse_query(query: str) -> dict:
    """
    Use the LLM to pull search parameters out of a natural-language query.

    Returns a dict with:
        description (str):        the item keywords
        size (str | None):        e.g. "M" or "8"
        max_price (float | None): e.g. 30.0

    Falls back to using the raw query as the description (no filters) if the
    LLM call or JSON parsing fails, so the agent never crashes on parsing.
    """
    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": _PARSE_PROMPT + f'"{query}"'}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)

        description = (data.get("description") or query).strip()
        size = data.get("size")
        size = str(size).strip() if size else None
        max_price = data.get("max_price")
        max_price = float(max_price) if max_price is not None else None

        return {"description": description, "size": size, "max_price": max_price}
    except Exception:
        # Safe fallback: search on the raw query with no filters.
        return {"description": query.strip(), "size": None, "max_price": None}


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.
    """
    # Step 1: fresh session.
    session = _new_session(query, wardrobe)

    # Step 2: parse the query into search parameters.
    session["parsed"] = _parse_query(query)
    parsed = session["parsed"]

    # Step 3: search.
    session["search_results"] = search_listings(
        parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )

    # Branch: no results → set error and stop. Do NOT call the other tools.
    if not session["search_results"]:
        price = parsed["max_price"]
        price_str = f" under ${price:g}" if price is not None else ""
        size_str = f" in size {parsed['size']}" if parsed["size"] else ""
        session["error"] = (
            f"No listings matched '{parsed['description']}'{size_str}{price_str}. "
            "Try raising your price limit, removing the size filter, or using broader keywords."
        )
        return session

    # Step 4: select the top result.
    session["selected_item"] = session["search_results"][0]

    # Step 5: suggest an outfit using the selected item + wardrobe.
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    # Step 6: create a shareable fit card from the outfit + item.
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    # Step 7: done.
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
