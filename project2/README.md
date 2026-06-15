# FitFindr 🛍️

FitFindr is a multi-tool AI agent that helps you find secondhand clothing and figure out how to wear it. You type a natural-language request (like "vintage graphic tee under $30"), and the agent searches mock listings, suggests an outfit using your wardrobe, and writes a shareable caption for the find.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
```

Add your Groq API key to a `.env` file in this folder (free key at [console.groq.com](https://console.groq.com)):

```
GROQ_API_KEY=your_key_here
```

## How to run

```bash
python app.py            # launch the Gradio web app (open the URL it prints)
python agent.py          # run the agent from the terminal (happy path + no-results path)
python -m pytest tests/  # run the tool tests
```

## Tools

The agent uses three tools, each implemented in `tools.py`.

### 1. `search_listings(description, size, max_price)`
- **Purpose:** find listings that match the user's request.
- **Inputs:**
  - `description` (str): item keywords, e.g. "vintage graphic tee"
  - `size` (str | None): size to filter by, e.g. "M". `None` skips the filter
  - `max_price` (float | None): price ceiling. `None` skips the filter
- **Output:** `list[dict]` of matching listings, best match first. Each dict has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`. Returns `[]` if nothing matches (no LLM used — pure filtering + keyword scoring).

### 2. `suggest_outfit(new_item, wardrobe)`
- **Purpose:** suggest 1–2 outfits pairing the item with the user's wardrobe.
- **Inputs:**
  - `new_item` (dict): the listing chosen by `search_listings`
  - `wardrobe` (dict): the user's wardrobe (`items` key holds a list; may be empty)
- **Output:** a string with the outfit idea. Uses the Groq LLM (`llama-3.3-70b-versatile`).

### 3. `create_fit_card(outfit, new_item)`
- **Purpose:** write a short, shareable OOTD-style caption.
- **Inputs:**
  - `outfit` (str): the suggestion from `suggest_outfit`
  - `new_item` (dict): the chosen listing (for name, price, platform)
- **Output:** a 2–4 sentence caption string. Uses the LLM with a high temperature so it varies each run.

## Planning loop

The loop lives in `run_agent()` in `agent.py`. It decides what to do based on what each tool returns, not a fixed order:

1. Make a new `session` dict.
2. Parse the query into `description`, `size`, `max_price` (using the LLM — see below).
3. Call `search_listings`.
   - **If it returns `[]`:** set `session["error"]` with a helpful message and stop. The other tools are NOT called.
   - **If it returns results:** save the top one as `selected_item` and continue.
4. Call `suggest_outfit(selected_item, wardrobe)`.
5. Call `create_fit_card(outfit_suggestion, selected_item)`.
6. Return the session.

The key decision is the empty check on the search results — that's what makes the agent behave differently for a normal query vs. an impossible one.

**Query parsing choice:** I parse the query with the LLM (Groq, JSON mode, temperature 0), not regex. The LLM handles free-form phrasing that regex misses — it normalizes "size medium" to "M" and reads loose prices like "around 40 bucks". The trade-off is one extra LLM call per search. If the LLM call or JSON parsing fails, it falls back to using the raw query as the description with no filters, so parsing never crashes the agent.

## State management

I use one `session` dict for the whole run (created by `_new_session()`). Each tool writes its result into the session and the next tool reads it, so the user only types their query once. Fields: `query`, `parsed`, `search_results`, `selected_item`, `wardrobe`, `outfit_suggestion`, `fit_card`, `error`.

Data flows like this:

```
search_listings → selected_item → suggest_outfit → outfit_suggestion → create_fit_card → fit_card
```

At the end, `app.py` reads the session and maps `selected_item`, `outfit_suggestion`, and `fit_card` to the three UI panels (or shows `error` in the first panel).

## Error handling

| Tool | Failure mode | What happens |
|------|--------------|--------------|
| `search_listings` | No results match | Returns `[]`. The loop sets a helpful error and stops without calling the other tools. |
| `suggest_outfit` | Wardrobe is empty | Gives general styling advice for the item instead of crashing. LLM errors return a fallback string. |
| `create_fit_card` | Empty `outfit` input | Returns a descriptive error string instead of raising. LLM errors return a fallback string. |

**Concrete example (from testing):** running the impossible query `designer ballgown size XXS under $5` gives:

```
No listings matched 'designer ballgown' in size XXS under $5.
Try raising your price limit, removing the size filter, or using broader keywords.
```

and `session["fit_card"]` stays `None` — the agent does not call `suggest_outfit` or `create_fit_card` on empty input.

## Spec reflection

Writing `planning.md` first made the build much smoother — by the time I wrote code, each tool's inputs, outputs, and failure mode were already decided, so the functions almost wrote themselves. The biggest change from my original spec was query parsing: I started with regex, but testing showed it broke on phrasing like "size medium" (it would filter out everything), so I switched to LLM parsing and documented the trade-off. Testing each tool in isolation with `pytest` before wiring the loop also saved a lot of debugging time.

## AI usage

I used Claude (in Cursor) to help build this. Two specific instances:

1. **Implementing `search_listings`.** I gave Claude the Tool 1 spec block from `planning.md` (inputs, return fields, the "return `[]` on no match" failure mode) plus `utils/data_loader.py`. It produced a function that filters by price/size and scores listings by keyword overlap. I reviewed it to confirm it filtered by all three parameters, skipped filters when they were `None`, and returned an empty list (not an exception) on no match, then tested it with a normal query, a size query, and an impossible query.

2. **Switching query parsing from regex to the LLM.** I first had Claude write a regex parser, but when I tested inputs like "size medium" and "around 40 bucks" it failed. I asked Claude to rewrite `_parse_query` to call the LLM in JSON mode and normalize sizes, and to add a fallback if the call fails. I verified the new version on six different queries before keeping it, and I overrode the default by requiring the safe fallback so a bad LLM response can't crash the agent.
