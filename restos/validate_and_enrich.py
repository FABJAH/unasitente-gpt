import os
import json
from datetime import datetime
from jsonschema import validate, ValidationError

BASE        = os.path.dirname(__file__)
SRC_DIR     = os.path.join(BASE, "data", "articles")
DST_DIR     = os.path.join(BASE, "data", "articles_enriched")
SCHEMA_PATH = os.path.join(BASE, "article_schema.json")

with open(SCHEMA_PATH, encoding="utf-8") as f:
    schema = json.load(f)

os.makedirs(DST_DIR, exist_ok=True)

for filename in os.listdir(SRC_DIR):
    if not filename.lower().endswith(".json"):
        continue

    src_path = os.path.join(SRC_DIR, filename)
    dst_path = os.path.join(DST_DIR, filename)

    with open(src_path, encoding="utf-8") as f:
        doc = json.load(f)

    try:
        validate(instance=doc, schema=schema)
    except ValidationError as e:
        print(f"✘ {filename} inválido: {e.message}")
        continue

    doc["validated_at"] = datetime.utcnow().isoformat() + "Z"
    doc["summary"]      = doc.get("content", "")[:100]

    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    print(f"✅ {filename} validado y enriquecido")
