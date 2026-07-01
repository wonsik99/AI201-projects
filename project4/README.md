# Provenance Guard

Provenance Guard is a Flask backend service for creative platforms. It classifies submitted text as likely AI-generated, likely human-written, or uncertain, then returns a transparency label, confidence score, appeal flow, and structured audit log.

Design notes and thresholds live in [`planning.md`](planning.md).

## What This Project Does

When a creator submits writing, the API:

1. Runs **two detection signals** (Groq LLM + stylometric heuristics)
2. Combines them into an **AI-likelihood confidence score** (0.0 = human-like, 1.0 = AI-like)
3. Maps the score to one of **three attribution labels** using asymmetric thresholds
4. Returns the exact **transparency label text** a platform would show readers
5. Writes a structured entry to the **audit log**
6. Accepts **appeals** that move a submission to `under_review`

This is a backend API only. There is no browser homepage — clients call the JSON endpoints directly.

## Architecture Overview

```text
POST /submit
  -> validate JSON { text, creator_id }
  -> Signal 1: Groq llama-3.3-70b-versatile -> llm_score
  -> Signal 2: stylometric heuristics -> heuristic_score
  -> combine scores -> confidence
  -> map confidence -> attribution + label text
  -> write audit log entry
  -> return JSON response

POST /appeal
  -> lookup content_id
  -> set status = under_review
  -> append appeal_reasoning to audit log

GET /log
  -> return all audit log entries
```

Full diagrams and API contracts are in [`planning.md`](planning.md).

## Setup

```bash
cd project4
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `project4/.env`:

```text
GROQ_API_KEY=your_key_here
```

Run the server from `src/`:

```bash
cd src
python app.py
```

The app listens on `http://127.0.0.1:5000`.

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/submit` | **POST** | Classify submitted text |
| `/appeal` | **POST** | Contest a prior classification |
| `/log` | GET | View audit log entries |

### Why browser visits show 404 / 405

If you open `http://127.0.0.1:5000/` in a browser, you get **404** because there is no root route — this API does not serve a homepage.

If you open `http://127.0.0.1:5000/submit` in the address bar, you get **405 Method Not Allowed** because the browser sends **GET**, but `/submit` only accepts **POST** with a JSON body.

Use `curl`, Postman, or another HTTP client instead:

```bash
curl -s http://127.0.0.1:5000/health

curl -s -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "ok so i finally tried that new ramen place downtown and honestly? underwhelming.", "creator_id": "test-user-1"}'

curl -s http://127.0.0.1:5000/log
```

Appeal example (replace `CONTENT_ID` with a value from `/submit`):

```bash
curl -s -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "CONTENT_ID", "creator_reasoning": "I wrote this myself from personal experience."}'
```

## Detection Signals

### Signal 1: Groq LLM classification

- **Measures:** semantic tone, generic phrasing, template transitions, overall “AI voice” vs casual human voice
- **Output:** `llm_score` in `[0.0, 1.0]` (higher = more AI-like)
- **Why chosen:** catches holistic patterns heuristics miss
- **Misses:** formal human academic writing, non-native formal English, lightly edited AI drafts

### Signal 2: Stylometric heuristics

Pure Python metrics combined into `heuristic_score`:

- sentence-length coefficient of variation
- type-token ratio (lexical diversity)
- transition-phrase density (`furthermore`, `in conclusion`, etc.)

- **Why chosen:** cheap, deterministic, structurally independent from the LLM
- **Misses:** poetry with repetition, minimalist human writing, very short fragments

## Confidence Scoring

Both signals output AI-likelihood scores. The combined score is:

```text
confidence = 0.65 * llm_score + 0.35 * heuristic_score
```

For very short text (< 2 sentences), heuristic weight drops to `0.15`.

If the signals disagree by more than `0.35`, the score is pulled toward the uncertain middle:

```text
confidence = 0.5 * confidence + 0.25
```

### Thresholds (asymmetric on purpose)

False positives (accusing a human of using AI) are treated as worse than false negatives.

| Attribution | Condition |
|-------------|-----------|
| `likely_human` | `confidence <= 0.30` |
| `uncertain` | `0.30 < confidence < 0.75` |
| `likely_ai` | `confidence >= 0.75` |

### Example submissions with different scores

**High-confidence human case**

- Text: casual ramen review with lowercase phrasing
- `llm_score`: 0.20
- `heuristic_score`: 0.00
- `confidence`: 0.13
- `attribution`: `likely_human`

**Lower-confidence / uncertain case**

- Text: polished AI-style essay with transition phrases
- `llm_score`: 0.80
- `heuristic_score`: 0.47
- `confidence`: 0.69
- `attribution`: `uncertain`

These examples show the system does not treat all inputs the same: casual human writing scores much lower than polished template-heavy prose, and the uncertain band prevents a strong AI accusation unless confidence reaches `0.75`.

## Transparency Labels

Exact user-facing strings returned in the API `label` field:

### High-confidence AI (`likely_ai`)

```text
Likely AI-generated (high confidence). Our analysis found strong signals associated with generated writing. If you wrote this yourself, you can appeal this result.
```

### High-confidence human (`likely_human`)

```text
Likely human-written (high confidence). We did not find strong AI-generation signals in this submission.
```

### Uncertain

```text
Origin uncertain. Our checks found mixed signals, so we are not making a strong attribution claim. You can still appeal if you want a human review.
```

## Rate Limiting

`POST /submit` is limited to:

```text
10 per minute; 100 per day
```

per remote IP using Flask-Limiter with `storage_uri="memory://"`.

**Reasoning:** a real creator may submit drafts several times in one session, so `10/minute` allows normal revision without blocking legitimate use. `100/day` reduces scripted flooding or brute-force probing while still allowing heavy same-day editing. Appeals are not aggressively rate-limited because they should be rare.

To verify rate limiting:

```bash
for i in $(seq 1 12); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:5000/submit \
    -H "Content-Type: application/json" \
    -d '{"text": "Rate limit test submission.", "creator_id": "ratelimit-test"}'
done
```

Expected: `200` for the first 10 requests, then `429`.

## Audit Log

Stored at `data/audit_log.json`. Every submission records:

- `content_id`, `creator_id`, `timestamp`, `text_hash`
- `attribution`, `confidence`, `label`
- `llm_score`, `heuristic_score`, `status`
- appeal fields when present

Sample entries from local testing:

```json
{
  "content_id": "37d62737-564f-4db0-ba42-d7bc591b8ce8",
  "creator_id": "test-user-1",
  "timestamp": "2026-07-01T06:07:19.689159Z",
  "attribution": "likely_human",
  "confidence": 0.13,
  "llm_score": 0.2,
  "heuristic_score": 0.0,
  "status": "under_review",
  "appeal_reasoning": "I wrote this myself after visiting the restaurant.",
  "appeal_timestamp": "2026-07-01T06:07:26.436411Z"
}
```

```json
{
  "content_id": "7b409e9a-444e-430d-b2ff-169346e87fe2",
  "creator_id": "test-user-2",
  "timestamp": "2026-07-01T06:07:20.018314Z",
  "attribution": "uncertain",
  "confidence": 0.6853,
  "llm_score": 0.8,
  "heuristic_score": 0.4724,
  "status": "classified"
}
```

View live entries with `GET /log`.

## Known Limitations

**Formal human academic writing** is the main failure mode for this version. A human-written policy memo or literature review can use balanced structure and transition phrases that raise both the LLM score and heuristic score. The system is designed to land many of these cases in the **uncertain** band rather than issuing a high-confidence AI accusation, but it can still mislead readers if the platform treats “uncertain” as suspicious.

Perfect AI detection is not achievable with two lightweight signals and a small rule set. The engineering goal here is honest uncertainty plus appeals, not flawless attribution.

## Spec Reflection

**How the spec helped:** the required-feature structure pushed me to separate detection, scoring, labeling, appeals, rate limiting, and audit logging instead of collapsing everything into one endpoint response.

**Where implementation diverged:** the spec’s example pairing suggested beating random guessing and showing meaningful variation, but real Groq scores on polished AI essays sometimes stopped in the uncertain band (`0.69`) rather than crossing the conservative `0.75` AI threshold. I kept that asymmetry on purpose so the system avoids false accusations even when one signal is fairly high.

## AI Usage

1. **Planning and architecture:** I used Codex to draft the initial `planning.md` structure, detection-signal definitions, threshold table, and label text, then edited the thresholds and appeal workflow before implementation.

2. **Implementation assistance:** I used Codex to generate the Flask app skeleton, Groq signal function, stylometric heuristics, audit-log helper, and rate-limit wiring from `planning.md`. I reviewed the generated scoring logic against the documented thresholds and adjusted the short-text heuristic weighting to match the edge-case rule in the spec.

3. **Annotation assistance:** not used. This project classifies incoming text at submission time; there is no labeled training dataset.

## Project Files

| File | Purpose |
|------|---------|
| [`planning.md`](./planning.md) | Architecture, thresholds, label text, edge cases |
| [`src/app.py`](./src/app.py) | Flask routes and rate limiting |
| [`src/detection.py`](./src/detection.py) | Groq + heuristics + scoring |
| [`src/labels.py`](./src/labels.py) | Label strings and threshold mapping |
| [`src/audit_log.py`](./src/audit_log.py) | JSON audit log storage |
| [`requirements.txt`](./requirements.txt) | Python dependencies |
