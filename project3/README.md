# TakeMeter: r/soccer Discourse Classifier

TakeMeter is a fine-tuned text classifier for `r/soccer` comments. The goal is to classify football discourse into four mutually exclusive modes: `analysis`, `hot_take`, `reaction`, and `banter`.

## Project Status

This project is currently ready for the Colab baseline and fine-tuning stage.

Completed:

- Chosen community: `r/soccer`
- Drafted label taxonomy
- Collected 200 real public `r/soccer` comments
- Created a balanced labeled CSV with 50 examples per label
- Preserved original Reddit permalinks in the dataset

Next:

- Run zero-shot Groq baseline on the locked test set
- Fine-tune `distilbert-base-uncased`
- Add evaluation results, confusion matrix, failure analysis, and sample classifications

## Label Taxonomy

| Label | Definition |
|-------|------------|
| `analysis` | The comment makes a football-related argument using specific tactical, statistical, historical, or contextual reasoning. |
| `hot_take` | The comment makes a strong evaluation or prediction but gives little, weak, or mostly rhetorical support. |
| `reaction` | The comment is mainly an immediate emotional response to a match event, result, mistake, referee call, or news item. |
| `banter` | The comment is mainly a joke, meme, rivalry jab, sarcasm, or fan-culture reference rather than a serious claim. |

## Data

The labeled dataset lives at:

```text
project3/data/takemeter_dataset.csv
```

Required columns:

| Column | Meaning |
|--------|---------|
| `text` | The Reddit comment text |
| `label` | One of `analysis`, `hot_take`, `reaction`, `banter` |
| `notes` | Optional annotation notes, especially for difficult examples |
| `source_url` | Original Reddit permalink for the comment |

Source: public `r/soccer` comments collected through the PullPush Reddit comment search API. Each row includes the original Reddit permalink in `source_url`.

Size: 200 labeled examples.

Label distribution:

| Label | Count |
|-------|-------|
| `analysis` | 50 |
| `hot_take` | 50 |
| `reaction` | 50 |
| `banter` | 50 |

The starter Colab notebook will split the single CSV into train, validation, and test sets.

## Difficult Annotation Examples

| Comment | Final Label | Why |
|---------|-------------|-----|
| "Yea Partey is properly washed..." | `analysis` | The first sentence sounds like a hot take, but the rest gives specific reasons about midfield defense, ball progression, passing, and pressing. |
| "De Gea in general is overrated" | `hot_take` | It is a direct unsupported player evaluation, not an event reaction. |
| "Most normal reaction of any Inter fan last night after the winner hahaha" | `banter` | It refers to a reaction, but the meme phrasing is the main point. |

## Model Plan

Base model: `distilbert-base-uncased`

Training environment: Google Colab with T4 GPU

Default training settings to start with:

- Epochs: 3
- Learning rate: `2e-5`
- Batch size: 16

These may be adjusted after the first run, but any change will be documented here.

## Baseline Plan

The zero-shot baseline will use Groq `llama-3.3-70b-versatile`. The prompt will include the four label definitions and will instruct the model to output only one label name.

Baseline results will be reported on the same test set used for the fine-tuned model.

## Evaluation Report

TODO after training:

- Overall accuracy for Groq baseline
- Overall accuracy for fine-tuned DistilBERT model
- Per-class precision, recall, and F1 for both models
- Fine-tuned model confusion matrix as a Markdown table
- At least 3 wrong predictions with analysis
- Sample classifications with predicted label and confidence
- Reflection on what the model learned vs. what I intended it to learn

## AI Usage

Current AI usage:

- Codex helped create the project structure, remove the Colab link from the Markdown files, and draft the r/soccer label taxonomy.

TODO after model evaluation:

- Document failure-analysis assistance
- Explain what AI-suggested error patterns were accepted, revised, or rejected
