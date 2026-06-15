# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
Searches the mock listings for items that match the description. It can also filter by size and max price.

**Input parameters:**
- `description` (str): keywords for what the user wants, like "vintage graphic tee". Used to score how well each listing matches.
- `size` (str | None): size to filter by, like "M". Case-insensitive. If None, skip the size filter.
- `max_price` (float | None): max price. Drop anything more expensive. If None, skip the price filter.

**What it returns:**
A list of listing dicts, best match first. Each dict has: id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand, platform. Returns an empty list `[]` if nothing matches (no error).

**What happens if it fails or returns nothing:**
It returns `[]`, not an error. Then the agent sets an error message ("No listings matched. Try a higher price or different keywords.") and stops. It does not call suggest_outfit.

---

### Tool 2: suggest_outfit

**What it does:**
Takes one item and the user's wardrobe and asks the LLM (Groq) for 1-2 outfit ideas. If the wardrobe has items, it uses them. If it's empty, it gives general styling tips for the item.

**Input parameters:**
- `new_item` (dict): the item picked by search_listings.
- `wardrobe` (dict): the user's wardrobe. Has an `items` key with a list of items. Can be empty.

**What it returns:**
A string with the outfit idea, like "pair this tee with your baggy jeans and chunky sneakers".

**What happens if it fails or returns nothing:**
If the wardrobe is empty, it doesn't fail. It just gives general styling tips instead. If the LLM call fails, it returns a simple fallback string so the agent keeps going.

---

### Tool 3: create_fit_card

**What it does:**
Makes a short caption for the outfit, like something you'd post on Instagram. I use a higher temperature so it sounds different each time.

**Input parameters:**
- `outfit` (str): the outfit idea from suggest_outfit.
- `new_item` (dict): the picked item, so the caption can mention its name, price, and platform.

**What it returns:**
A short 2-4 sentence string, casual like a real post.

**What happens if it fails or returns nothing:**
If `outfit` is empty, it returns an error string instead of crashing. If the LLM call fails, it returns a fallback string.

---

## Planning Loop

**How does your agent decide which tool to call next?**

The agent decides based on what each tool returns, not a fixed order. Here are the steps:

1. Make a new session with `_new_session(query, wardrobe)`.
2. Parse the query into `description`, `size`, `max_price`. Save it in `session["parsed"]`.
   - **Parsing choice: I use the LLM (Groq), not regex.** I ask the model to return a JSON object with `description`, `size`, and `max_price` (temperature 0, JSON mode). I picked the LLM because it handles free-form phrasing that regex misses — e.g. it normalizes "size medium" to "M" and reads loose prices like "around 40 bucks". Trade-off: it adds one more LLM call per search (so 3 total: parse + outfit + fit card) and is a bit slower than regex. If the LLM call or JSON parsing fails, it falls back to using the raw query as the description with no filters, so the agent never crashes on parsing.
3. Call `search_listings(description, size, max_price)`. Save the result in `session["search_results"]`.
   - If the result is empty: set `session["error"]` and return right away. Don't call the other tools.
   - If there are results: set `session["selected_item"] = search_results[0]` (the top one) and keep going.
4. Call `suggest_outfit(selected_item, wardrobe)`. Save it in `session["outfit_suggestion"]`.
5. Call `create_fit_card(outfit_suggestion, selected_item)`. Save it in `session["fit_card"]`.
6. Return the session.

The loop stops either at step 3 (no results) or after step 5. The main decision is the empty check on `search_results`.

---

## State Management

**How does information from one tool get passed to the next?**

I use one `session` dict (from `_new_session()`) for the whole run. Each tool writes its result into the session, and the next tool reads it. So the user only types their query once. The fields are:

- `query` (str): the user's input.
- `parsed` (dict): the `description` / `size` / `max_price` I pulled out.
- `search_results` (list): what search_listings returned.
- `selected_item` (dict | None): the top result, used by suggest_outfit and create_fit_card.
- `wardrobe` (dict): the user's wardrobe, used by suggest_outfit.
- `outfit_suggestion` (str | None): what suggest_outfit returned, used by create_fit_card.
- `fit_card` (str | None): what create_fit_card returned, shown to the user.
- `error` (str | None): set if something fails. The UI checks this first.

So the data flows like this: search_listings → selected_item → suggest_outfit → outfit_suggestion → create_fit_card → fit_card. At the end, `app.py` reads the session and puts each field into one of the three panels.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns `[]`. The agent sets an error like "No listings matched. Try a higher price or different keywords." and stops. The UI shows this in the first panel and leaves the other two empty. suggest_outfit is never called. |
| suggest_outfit | Wardrobe is empty | Doesn't error. It checks if the wardrobe is empty and gives general styling tips for the item instead. If the LLM call fails, it returns a fallback string so the agent keeps going. |
| create_fit_card | Outfit input is missing or incomplete | If `outfit` is empty, it returns an error string like "Can't write a fit card without an outfit." instead of crashing. If the LLM call fails, it returns a fallback caption. |

---

## Architecture

```
User query + wardrobe choice  (app.py: handle_query)
        │
        ▼
Planning Loop  (agent.py: run_agent) ──────────────────────────────┐
        │                                                          │
        │  parse query → session["parsed"] = {description, size, max_price}
        │                                                          │
        ├─► search_listings(description, size, max_price)          │
        │       │ results == []                                    │
        │       ├──► [ERROR] session["error"] = "No listings..." ──┤
        │       │                                                  │
        │       │ results == [item, ...]                           │
        │       ▼                                                  │
        │   Session: selected_item = results[0]                    │
        │       │                                                  │
        ├─► suggest_outfit(selected_item, wardrobe)                │
        │       │   (empty wardrobe → general styling advice)      │
        │       ▼                                                  │
        │   Session: outfit_suggestion = "..."                     │
        │       │                                                  │
        └─► create_fit_card(outfit_suggestion, selected_item)      │
                │                                                  │
            Session: fit_card = "..."                              │
                │                                  error path returns here
                ▼                                                  │
        Return session  ◄──────────────────────────────────────────┘
                │
                ▼
   app.py maps session → 3 UI panels:
     listing panel ← selected_item   |   outfit panel ← outfit_suggestion   |   fit-card panel ← fit_card
     (on error: error message → listing panel, other panels empty)

   Session State (shared across all steps):
     query · parsed · search_results · selected_item · wardrobe · outfit_suggestion · fit_card · error
```

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
I'll use Claude, one tool at a time.
- `search_listings`: I'll give it the Tool 1 block and `utils/data_loader.py`, and ask it to write the function using `load_listings()` (no LLM, just filtering and keyword scoring). I'll check it filters by all 3 params, skips filters when they're None, and returns `[]` when nothing matches. Then I'll test 3 queries: a normal one, a size one, and a no-results one.
- `suggest_outfit`: I'll give it the Tool 2 block and the `_get_groq_client()` helper, and ask for a prompt that works for both a full and an empty wardrobe. I'll test it with `get_example_wardrobe()` and `get_empty_wardrobe()` and make sure both return a non-empty string.
- `create_fit_card`: I'll give it the Tool 3 block and ask for a higher-temperature prompt. I'll check it handles empty `outfit` and gives a different caption each run.

**Milestone 4 — Planning loop and state management:**
I'll give Claude the Planning Loop section, the State Management fields, and the diagram, and ask it to write `run_agent()` in `agent.py` following the same steps (especially the early return when search is empty). I'll test the happy path and the no-results path using the `__main__` block already in `agent.py`. For `app.py`, I'll ask it to fill in `handle_query` so the session fields go into the 3 panels and the error shows in the first one.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
First I parse the query into: description="vintage graphic tee", max_price=30.0, size=None (no size given). Then I call `search_listings("vintage graphic tee", size=None, max_price=30.0)`. It returns matching tees (like the Y2K Baby Tee at $18 and the 2003 Tour Bootleg Tee at $24). I take the top one and save it as the selected item.

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
I pass the selected item from Step 1 into `suggest_outfit(new_item=<the tee>, wardrobe=<user's wardrobe>)`. The wardrobe has the baggy jeans and chunky sneakers. It returns an outfit idea like "pair this tee with your baggy jeans and chunky sneakers for a 90s grunge look".

**Step 3:**
<!-- Continue until the full interaction is complete -->
I call `create_fit_card(outfit=<Step 2 idea>, new_item=<the tee>)`. It uses both the outfit from Step 2 and the item from Step 1, and returns a short caption like "thrifted this faded tee off depop for $24 and it was made for my baggy jeans 🖤".

**Final output to user:**
<!-- What does the user actually see at the end? -->
The user sees all 3 results at once in the 3 panels: (1) 🛍️ the listing from Step 1, (2) 👗 the outfit idea from Step 2, and (3) ✨ the fit card from Step 3. Not just Step 3 — each one goes in its own panel. If Step 1 finds nothing, it stops and shows an error in the first panel instead.