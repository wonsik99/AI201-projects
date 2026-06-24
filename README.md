# CodePath AI201 — Projects

Larger standalone projects from the CodePath AI201 course. (Smaller weekly labs
live in a separate repo: [`codepath-ai201`](https://github.com/wonsik99/codepath-ai201).)

## Projects

| # | Project | Description |
|---|---------|-------------|
| 1 | [The Unofficial Guide](./project1) | RAG system for choosing UMich CS/EECS courses with source-attributed answers |
| 2 | [FitFindr](./project2) | Outfit-recommendation agent over secondhand clothing listings and a user wardrobe |
| 3 | [TakeMeter](./project3) | Fine-tuned classifier for r/soccer discourse quality and comment type |

## How to run (each project)

```bash
cd projectN
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your API key to .env
python app.py
```
