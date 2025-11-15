import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app


def main() -> None:
    schema = app.openapi()
    os.makedirs(os.path.join("docs", "schema", "blog"), exist_ok=True)
    out_path = os.path.join("docs", "schema", "blog", "openapi.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(out_path)


if __name__ == "__main__":
    main()
