from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
RAW_DATA_DIR = DOCUMENTS_DIR
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "umich_cs_course_guide"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE_CHARS = 750
CHUNK_OVERLAP_CHARS = 150
TOP_K = 5
MAX_DISTANCE_FOR_ANSWER = 0.68
