from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from audit_log import AuditLog
from detection import analyze_text

load_dotenv()

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "audit_log.json"


def create_app() -> Flask:
    app = Flask(__name__)
    audit_log = AuditLog(AUDIT_LOG_PATH)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[],
        storage_uri="memory://",
    )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/submit")
    @limiter.limit("10 per minute;100 per day")
    def submit():
        payload = request.get_json(silent=True) or {}
        text = payload.get("text")
        creator_id = payload.get("creator_id")

        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "text is required"}), 400
        if not isinstance(creator_id, str) or not creator_id.strip():
            return jsonify({"error": "creator_id is required"}), 400

        analysis = analyze_text(text.strip())
        entry = audit_log.create_submission(
            creator_id=creator_id.strip(),
            text=text.strip(),
            analysis=analysis,
        )

        return jsonify(
            {
                "content_id": entry["content_id"],
                "attribution": entry["attribution"],
                "confidence": entry["confidence"],
                "label": entry["label"],
                "llm_score": entry["llm_score"],
                "heuristic_score": entry["heuristic_score"],
                "status": entry["status"],
            }
        )

    @app.post("/appeal")
    def appeal():
        payload = request.get_json(silent=True) or {}
        content_id = payload.get("content_id")
        creator_reasoning = payload.get("creator_reasoning")

        if not isinstance(content_id, str) or not content_id.strip():
            return jsonify({"error": "content_id is required"}), 400
        if not isinstance(creator_reasoning, str) or not creator_reasoning.strip():
            return jsonify({"error": "creator_reasoning is required"}), 400

        entry = audit_log.record_appeal(
            content_id.strip(),
            creator_reasoning.strip(),
        )
        if entry is None:
            return jsonify({"error": "content_id not found"}), 404

        return jsonify(
            {
                "content_id": entry["content_id"],
                "status": entry["status"],
                "message": "Appeal received. This submission is now under review.",
            }
        )

    @app.get("/log")
    def log():
        return jsonify({"entries": audit_log.list_entries()})

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
