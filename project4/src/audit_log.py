import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.entries_by_id: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for entry in payload.get("entries", []):
            self.entries_by_id[entry["content_id"]] = entry

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entries = sorted(
            self.entries_by_id.values(),
            key=lambda item: item["timestamp"],
        )
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump({"entries": entries}, handle, indent=2)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def text_hash(text: str) -> str:
        return sha256(text.encode("utf-8")).hexdigest()

    def create_submission(
        self,
        *,
        creator_id: str,
        text: str,
        analysis: dict,
    ) -> dict:
        entry = {
            "content_id": str(uuid4()),
            "creator_id": creator_id,
            "timestamp": self._now(),
            "text_hash": self.text_hash(text),
            "attribution": analysis["attribution"],
            "confidence": analysis["confidence"],
            "label": analysis["label"],
            "llm_score": analysis["llm_score"],
            "heuristic_score": analysis["heuristic_score"],
            "status": "classified",
        }
        self.entries_by_id[entry["content_id"]] = entry
        self._save()
        return entry

    def get_entry(self, content_id: str) -> dict | None:
        return self.entries_by_id.get(content_id)

    def record_appeal(self, content_id: str, creator_reasoning: str) -> dict | None:
        entry = self.entries_by_id.get(content_id)
        if entry is None:
            return None

        entry["status"] = "under_review"
        entry["appeal_reasoning"] = creator_reasoning
        entry["appeal_timestamp"] = self._now()
        self._save()
        return entry

    def list_entries(self) -> list[dict]:
        return sorted(
            self.entries_by_id.values(),
            key=lambda item: item["timestamp"],
        )
