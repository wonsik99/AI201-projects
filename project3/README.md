# TakeMeter: r/soccer Discourse Classifier

TakeMeter is a fine-tuned text classifier for `r/soccer` comments. It classifies football discourse into four mutually exclusive modes: `analysis`, `hot_take`, `reaction`, and `banter`.

## Community Choice

I chose `r/soccer` because it mixes several distinct comment styles in one community: tactical discussion, unsupported player takes, live match reactions, and rivalry banter. Those modes are familiar to regular readers but hard to separate automatically, which makes the task a good fit for a discourse classifier.

Detailed design notes and annotation rules live in [`planning.md`](planning.md).

## Label Taxonomy

| Label | Definition | Example 1 | Example 2 |
|-------|------------|-----------|-----------|
| `analysis` | The comment makes a football-related argument using specific tactical, statistical, historical, or contextual reasoning. | "The substitution made sense because City were losing second balls in midfield, so adding another central midfielder let them control the tempo again." | "Sweden also had that sort of asymmetric transition between defense and attack for many years, going from a straight 4-4-2 in defense to more of a 3-4-3 in possession." |
| `hot_take` | The comment makes a strong evaluation or prediction but gives little, weak, or mostly rhetorical support. | "De Gea in general is overrated" | "KDB looks a tad washed." |
| `reaction` | The comment is mainly an immediate emotional response to a match event, result, mistake, referee call, or news item. | "What a save! Fucking hell" | "I CANT BELIEVE WE AREE HOLY FUCKKKK" |
| `banter` | The comment is mainly a joke, meme, rivalry jab, sarcasm, or fan-culture reference rather than a serious claim. | "Most normal Spurs ending." | "jamie vardy is football heritage" |

## Data

The labeled dataset lives at:

```text
project3/data/takemeter_dataset.csv
```

| Column | Meaning |
|--------|---------|
| `text` | The Reddit comment text |
| `label` | One of `analysis`, `hot_take`, `reaction`, `banter` |
| `notes` | Optional annotation notes, especially for difficult examples |
| `source_url` | Original Reddit permalink for the comment |

**Source:** public `r/soccer` comments collected through the PullPush Reddit comment search API. Each row includes the original Reddit permalink in `source_url`.

**Labeling process:** I searched public threads by label type (match threads for `reaction`/`banter`, transfer/news threads for `hot_take`, tactical threads for `analysis`), applied the taxonomy in `planning.md`, and recorded difficult edge cases in the `notes` column when the boundary was unclear.

**Size and distribution:** 200 labeled examples, balanced at 50 per label.

| Label | Count |
|-------|-------|
| `analysis` | 50 |
| `hot_take` | 50 |
| `reaction` | 50 |
| `banter` | 50 |

The notebook splits this CSV into train / validation / test sets (70% / 15% / 15%, stratified, `random_state=42`).

### Difficult Annotation Examples

| Comment | Final Label | Why |
|---------|-------------|-----|
| "Yea Partey is properly washed..." | `analysis` | The opening sounds like a hot take, but the rest gives specific reasons about midfield defense, ball progression, passing, and pressing. |
| "De Gea in general is overrated" | `hot_take` | It is a direct unsupported player evaluation, not a live emotional response to an event. |
| "Most normal reaction of any Inter fan last night after the winner hahaha" | `banter` | It refers to a reaction, but the meme phrasing is the main point. |

## Fine-Tuning Approach

| Setting | Value | Rationale |
|---------|-------|-----------|
| Base model | `distilbert-base-uncased` | Course default; fast enough for Colab and strong on short text classification |
| Environment | Google Colab, T4 GPU | Required GPU runtime for practical training time |
| Epochs | 3 | Starter default for ~200-example datasets |
| Learning rate | `2e-5` | Standard BERT-family fine-tuning starting point |
| Batch size | 16 | Fits T4 memory; reduced only if OOM |
| Max length | 256 tokens | Covers most Reddit comments without excessive padding |

Training notebook: [`takemeter.ipynb`](takemeter.ipynb)

## Baseline

**Model:** Groq `llama-3.3-70b-versatile`  
**Temperature:** 0  
**Evaluation set:** same 30-example test split as the fine-tuned model

The zero-shot prompt names `r/soccer`, defines all four labels with one example each, and instructs the model to return only the label name. Full prompt:

```text
You are classifying Reddit comments from r/soccer.
Assign each comment to exactly one of the following categories.

analysis: The comment makes a football-related argument using specific tactical,
statistical, historical, or contextual reasoning.
Example: "The substitution made sense because City were losing second balls in
midfield, so adding another central midfielder let them control the tempo again."

hot_take: The comment makes a strong evaluation or prediction but gives little,
weak, or mostly rhetorical support.
Example: "De Gea in general is overrated"

reaction: The comment is mainly an immediate emotional response to a match event,
result, mistake, referee call, or news item.
Example: "What a save! Fucking hell"

banter: The comment is mainly a joke, meme, rivalry jab, sarcasm, or fan-culture
reference rather than a serious claim.
Example: "Most normal Spurs ending."

Respond with ONLY the label name.
Do not explain your reasoning.

Valid labels:
analysis
hot_take
reaction
banter
```

Results were collected by running the baseline loop in `takemeter.ipynb` over the locked test set with a 0.1s delay between API calls.

## Evaluation Report

Results file: [`outputs/evaluation_results.json`](outputs/evaluation_results.json)  
Confusion matrix image: [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png)

### Overall Accuracy

| Model | Accuracy | Test set size |
|-------|----------|---------------|
| Zero-shot baseline (Groq) | **0.867** | 30 |
| Fine-tuned DistilBERT | **0.733** | 30 |

The fine-tuned model met the 70% accuracy target but underperformed the Groq baseline by 0.133 on this small test split.

### Per-Class Metrics — Fine-Tuned DistilBERT

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| analysis | 0.80 | 1.00 | 0.89 | 8 |
| hot_take | 0.50 | 0.57 | 0.53 | 7 |
| reaction | 1.00 | 0.62 | 0.77 | 8 |
| banter | 0.71 | 0.71 | 0.71 | 7 |
| **Macro avg** | 0.75 | 0.73 | 0.73 | 30 |
| **Weighted avg** | 0.76 | 0.73 | 0.73 | 30 |

### Per-Class Metrics — Groq Baseline

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| analysis | 0.88 | 0.88 | 0.88 | 8 |
| hot_take | 0.86 | 0.86 | 0.86 | 7 |
| reaction | 0.80 | 1.00 | 0.89 | 8 |
| banter | 1.00 | 0.71 | 0.83 | 7 |
| **Macro avg** | 0.88 | 0.86 | 0.86 | 30 |
| **Weighted avg** | 0.88 | 0.87 | 0.86 | 30 |

### Confusion Matrix — Fine-Tuned Model (Test Set)

Rows = true label, columns = predicted label.

| True ↓ / Pred → | analysis | hot_take | reaction | banter |
|-----------------|----------|----------|----------|--------|
| analysis | **8** | 0 | 0 | 0 |
| hot_take | 2 | **4** | 0 | 1 |
| reaction | 0 | 2 | **5** | 1 |
| banter | 0 | 2 | 0 | **5** |

**Main error pattern:** most mistakes involve `hot_take` as either the true label or the predicted label. The model learned `analysis` well (8/8 correct) but struggled on shorter or meme-like comments at the `hot_take` / `reaction` / `banter` boundaries.

### Wrong Predictions — Analysis

#### 1. `reaction` → `hot_take` — "No way they are overturning that" (confidence: 0.26)

**Confusion:** `reaction` predicted as `hot_take`.

**Why it failed:** The comment is short and opinion-like. "No way..." reads like a take on a referee decision rather than pure emotional reaction language such as "WHAT A SAVE."

**Labeling vs. model:** My label is defensible because it reacts to a specific in-match event, but the wording is close to a skeptical hot take. This is a boundary issue in the data, not random noise.

**Fix:** Add more short reactive VAR/referee comments that do not use "hot take" phrasing.

#### 2. `hot_take` → `analysis` — `"Underrated", "Overrated" and "Bottlejob" are probably the three most misused words in modern football."` (confidence: 0.26)

**Confusion:** `hot_take` predicted as `analysis`.

**Why it failed:** The comment makes a meta-argument about football discourse vocabulary. It sounds analytical because it discusses language patterns, but my label treats it as an unsupported broad claim about fan culture.

**Labeling vs. model:** Annotation is consistent with my rules, but the surface form overlaps with `analysis`. The model likely over-weighted topic words like "misused words" and under-weighted the lack of tactical evidence.

**Fix:** More examples where meta-commentary is still labeled `hot_take`.

#### 3. `banter` → `hot_take` — "the most spursy thing to do would be to not break their trophy drought while everyone else does" (confidence: 0.26)

**Confusion:** `banter` predicted as `hot_take`.

**Why it failed:** The comment contains a substantive claim about Spurs, but the "spursy" meme frame is the main signal for `banter`. DistilBERT likely latched onto the predictive clause instead of the meme template.

**Labeling vs. model:** Labeling is consistent. The issue is that rivalry meme language often embeds claims that look like takes.

**Fix:** More `banter` examples that include full sentences, not just one-liners.

#### 4. `reaction` → `banter` — "What a goal. Is there a Puskas for U15s?" (confidence: 0.26)

**Confusion:** `reaction` predicted as `banter`.

**Why it failed:** The second sentence adds a joking aside, which blurs reaction and banter. The first sentence is clearly reactive; the second introduces humor.

**Labeling vs. model:** This is a genuinely ambiguous post. I labeled the dominant live-event reaction, but the model may have weighted the joke half more heavily.

**Fix:** Tighter rule in `planning.md` for mixed reaction + joke comments, plus more explicit examples.

### AI-Assisted Error Pattern Review

I pasted the eight wrong predictions into an LLM and asked for common failure themes. It suggested: (1) short low-information posts, (2) meme templates like "spursy" / "Most normal...", (3) `hot_take` vs. `analysis` confusion on meta-football claims, and (4) `reaction` vs. `hot_take` confusion on skeptical phrasing.

I accepted themes (1), (2), and (3) after re-reading the examples. I partially rejected theme (4) as a standalone explanation because some skeptical reactions are still correctly labeled `reaction` in the dataset; the bigger issue is shared short-opinion syntax across labels.

### Sample Classifications — Fine-Tuned Model

Outputs below are from the locked test-set inference run in `takemeter.ipynb` (Cells 15–17).

| Text | True label | Predicted | Confidence | Correct? |
|------|------------|-----------|------------|----------|
| "Yea Partey is properly washed. I was so confused seeing people say he should be renewed. All he did was give us a little bit more defence in midfield..." | analysis | analysis | (correct on test set) | Yes |
| "What a save! Fucking hell" | reaction | reaction | (correct on test set) | Yes |
| "No way they are overturning that" | reaction | hot_take | 0.26 | No |
| "the most spursy thing to do would be to not break their trophy drought while everyone else does" | banter | hot_take | 0.26 | No |
| `"Underrated", "Overrated" and "Bottlejob" are probably the three most misused words in modern football."` | hot_take | analysis | 0.26 | No |

**Why the Partey comment is a reasonable correct prediction:** The comment gives multiple specific football mechanisms (press resistance, passing limits, midfield role) rather than a single unsupported verdict, which matches the `analysis` definition even though the opening line sounds negative and hot-take-like.

Wrong predictions on the test set had low confidence scores (~0.26), which suggests the model often spreads probability mass across several labels instead of making sharp decisions.

### Reflection — What the Model Learned vs. What I Intended

I intended the model to learn four discourse modes based on reasoning depth, emotional immediacy, and meme/fandom framing. In practice, the decision boundary it learned is narrower:

- **Captured well:** longer, mechanism-heavy comments classified as `analysis` (perfect recall on the test split).
- **Missed or blurred:** short opinion-like wording, meme templates, and meta-football commentary that share surface features with `hot_take`.
- **Likely shortcut:** words such as "overrated," "spursy," and "No way..." became strong cues for `hot_take`, even when annotation rules placed those comments in `reaction` or `banter`.

The gap between my taxonomy and the model's behavior suggests the labels are conceptually distinct but not always separable by bag-of-words-style features alone, especially with only 200 training examples and a 30-example test set.

## Spec Reflection

**How the spec helped:** The project structure pushed me to define label boundaries before collecting data, run a zero-shot baseline on the same test split, and report failures with a confusion matrix instead of stopping at accuracy alone.

**Where implementation diverged:** The spec's success criteria hoped the fine-tuned model would beat the baseline on accuracy or macro F1. Mine did not—Groq `llama-3.3-70b-versatile` reached 0.867 accuracy vs. 0.733 for DistilBERT. I kept the default DistilBERT hyperparameters rather than tuning further because the primary goal here was honest evaluation and diagnosis, not leaderboard optimization.

## AI Usage

1. **Project setup and taxonomy drafting:** I asked Codex to scaffold the `project3` folder, draft the initial `r/soccer` label definitions, and configure the Colab notebook paths. I revised several definitions in `planning.md` after stress-testing edge cases manually.

2. **Failure-pattern review:** I pasted misclassified test examples into an LLM and asked for recurring themes. I accepted patterns about meme templates and short-post ambiguity, but rejected the suggestion that most errors were simply "labeling inconsistency" because manual review showed consistent rules applied to genuinely ambiguous comments.

3. **Annotation assistance:** I did not auto-label the final dataset with AI. All 200 labels were assigned manually using the rules in `planning.md`.

## Project Status

Completed:

- Community choice, taxonomy, and data collection
- 200-example balanced labeled CSV with source URLs
- Groq zero-shot baseline on the locked test set
- DistilBERT fine-tuning in Colab
- Evaluation report, confusion matrix, and exported results in `outputs/`

Remaining for submission:

- Record the 3–5 minute demo video
