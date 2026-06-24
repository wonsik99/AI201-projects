# TakeMeter — planning.md

> Complete this document before collecting the full labeled dataset.
> Update it if the label taxonomy changes or before starting any stretch feature.

---

## Community

I will build TakeMeter for `r/soccer`, a large public Reddit community where people discuss live matches, transfer news, tactics, referee decisions, managers, players, and club rivalries. This community is a good fit for a discourse-quality classifier because the comments are text-heavy and vary a lot: some users give tactical or statistical reasoning, some make strong unsupported claims, some react emotionally in the moment, and some mainly post jokes or fan banter.

These distinctions matter in `r/soccer` because regular readers often separate serious football discussion from match-thread reactions, hot takes, and rivalry jokes. A classifier that can identify those modes would be useful for filtering discussion, comparing match threads to analysis threads, or studying how discourse changes around major events.

## Label Taxonomy

The dataset will use four mutually exclusive labels:

| Label | Definition |
|-------|------------|
| `analysis` | The comment makes a football-related argument using specific tactical, statistical, historical, or contextual reasoning. |
| `hot_take` | The comment makes a strong evaluation or prediction but gives little, weak, or mostly rhetorical support. |
| `reaction` | The comment is mainly an immediate emotional response to a match event, result, mistake, referee call, or news item. |
| `banter` | The comment is mainly a joke, meme, rivalry jab, sarcasm, or fan-culture reference rather than a serious claim. |

### `analysis`

Clear examples:

- "Arsenal are struggling because the left winger keeps receiving the ball with two defenders already set, and the fullback is not overlapping enough to create a 2v1."
- "The substitution made sense because City were losing second balls in midfield, so adding another central midfielder let them control the tempo again."

Boundary note:

- A comment can be negative and still be `analysis` if the reasoning is specific enough to stand on its own.

### `hot_take`

Clear examples:

- "This manager is completely clueless and will never win anything important."
- "That striker is finished. One purple patch fooled everyone."

Boundary note:

- If a comment includes one statistic but mainly uses it as a weapon for a broad unsupported claim, I will usually label it `hot_take` rather than `analysis`.

### `reaction`

Clear examples:

- "WHAT A SAVE."
- "I cannot believe he missed that from there."

Boundary note:

- Match-thread comments that are short, emotional, and tied to a specific moment will be `reaction`, even if they imply an opinion about a player or team.

### `banter`

Clear examples:

- "Most normal Spurs ending."
- "Least chaotic CONCACAF match."

Boundary note:

- If the main purpose is humor, meme reference, rivalry teasing, or sarcasm, I will label it `banter` even if it also implies criticism.

## Hard Edge Cases

The hardest boundary will likely be between `analysis` and `hot_take`. For example:

> "United are terrible because their midfield gets bypassed every week."

This has a football explanation, but it is still broad and underdeveloped. My rule: if the comment identifies a specific mechanism, pattern, statistic, tactical issue, or contextual reason clearly enough that another fan could evaluate the argument, label it `analysis`. If it mostly asserts a conclusion with vague football language, label it `hot_take`.

Another hard boundary will be between `reaction` and `banter`. For example:

> "Of course Chelsea concede like that."

This could be a live emotional response or a joke about a team reputation. My rule: if the comment is primarily reacting to a specific event with emotion, label it `reaction`; if the wording depends on a recurring meme, rivalry trope, or sarcastic fan-culture reference, label it `banter`.

During annotation, I will keep at least three difficult examples in the notes column and document the final decision here after labeling.

Annotation update:

| Comment | Possible Labels | Final Label | Decision |
|---------|-----------------|-------------|----------|
| "Yea Partey is properly washed..." | `analysis`, `hot_take` | `analysis` | The opening is a hot-take phrase, but the comment gives specific football reasons about midfield defense, ball progression, passing, and dealing with Newcastle's press. |
| "De Gea in general is overrated" | `hot_take`, `reaction` | `hot_take` | It is short, but it is a direct unsupported player evaluation rather than a live emotional response to an event. |
| "Most normal reaction of any Inter fan last night after the winner hahaha" | `reaction`, `banter` | `banter` | It refers to a reaction, but the main signal is the meme phrasing "Most normal..." and the joke structure. |

## Data Collection Plan

I will collect at least 200 public comments from `r/soccer`. I will use public Reddit threads only, focusing on a mix of:

- Match threads and post-match threads for `reaction` and `banter`
- News or transfer threads for `hot_take`
- Tactical discussion, serious post-match discussion, and longer comment chains for `analysis`

The target distribution is roughly balanced:

| Label | Target Count |
|-------|--------------|
| `analysis` | 50 |
| `hot_take` | 50 |
| `reaction` | 50 |
| `banter` | 50 |

If one label is underrepresented after collecting 200 examples, I will collect more examples from thread types where that label is common. If one label exceeds 70% of the dataset, I will not move to training until I add more examples from the other labels.

The dataset is saved as `project3/data/takemeter_dataset.csv` with these columns:

| Column | Meaning |
|--------|---------|
| `text` | The Reddit comment text |
| `label` | One of `analysis`, `hot_take`, `reaction`, `banter` |
| `notes` | Optional annotation notes, especially for difficult cases |
| `source_url` | Original Reddit permalink for the comment |

Current dataset distribution:

| Label | Count |
|-------|-------|
| `analysis` | 50 |
| `hot_take` | 50 |
| `reaction` | 50 |
| `banter` | 50 |

The comments were collected from public `r/soccer` comments using the PullPush Reddit comment search API, with original Reddit permalinks preserved in `source_url`.

## Evaluation Metrics

I will report overall accuracy for both the fine-tuned model and the zero-shot Groq baseline, but accuracy alone is not enough because the labels may be unevenly distributed and some label boundaries are harder than others.

I will also report per-class precision, recall, and F1. Per-class F1 is especially important because a model could look accurate overall while failing on a smaller class like `analysis` or `banter`. I will include a confusion matrix for the fine-tuned model to see which labels are confused most often, especially `analysis` vs. `hot_take` and `reaction` vs. `banter`.

## Definition of Success

For this project, a useful classifier should do more than beat random guessing on a four-class task. My target is:

- Fine-tuned model overall accuracy of at least 70% on the test set
- Fine-tuned model macro F1 of at least 0.65
- Fine-tuned model performs better than the zero-shot Groq baseline on either overall accuracy or macro F1
- No class has an F1 score near 0, because that would mean the model failed to learn one of the discourse modes

For a real community moderation or filtering tool, I would want stronger performance, especially high recall for `analysis` if the goal is to surface higher-effort comments. For this class project, "good enough" means the model learns meaningful distinctions and its errors are explainable.

## AI Tool Plan

### Label Stress-Testing

I will ask an AI tool to generate 5-10 short `r/soccer`-style comments that sit near the boundary between `analysis` and `hot_take`, and another 5-10 near the boundary between `reaction` and `banter`. I will classify those examples using my label rules. If I cannot classify them consistently, I will revise the definitions before labeling the full dataset.

### Annotation Assistance

I may use AI tools to check label consistency on difficult examples, but final labels should match the taxonomy and be reviewed before submission.

### Failure Analysis

After fine-tuning, I will give the wrong predictions to an AI tool and ask it to identify possible patterns, such as sarcasm, short comments, topic leakage, or repeated confusion between two labels. I will verify any suggested pattern by rereading the examples before including it in the evaluation report.

## Colab Notebook

I will use the course starter Colab notebook for baseline evaluation and fine-tuning. I will use Colab Secrets for `GROQ_API_KEY`; the key must not be committed to GitHub or pasted into project files.
