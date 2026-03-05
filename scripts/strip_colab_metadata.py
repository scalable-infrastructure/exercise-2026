#!/usr/bin/env python3
"""Strip Colab/Google PII metadata from Jupyter notebooks (photoUrl, userId, base_uri)."""

import json
import sys
from pathlib import Path

COLAB_USER_ID = "13897213013486729084"
COLAB_BASE_URI = "https://localhost:8080/"
GOOGLE_AVATAR_PREFIX = "https://lh3.googleusercontent.com/"


def clean_obj(obj):
    """Recursively remove Colab/PII keys from dicts. Modifies in place, returns obj."""
    if isinstance(obj, dict):
        keys_to_drop = []
        for k, v in obj.items():
            if k == "photoUrl" and isinstance(v, str) and (GOOGLE_AVATAR_PREFIX in v or v == ""):
                keys_to_drop.append(k)
            elif k == "userId" and v == COLAB_USER_ID:
                keys_to_drop.append(k)
            elif k == "base_uri" and v == COLAB_BASE_URI:
                keys_to_drop.append(k)
            else:
                clean_obj(v)
        for k in keys_to_drop:
            del obj[k]
    elif isinstance(obj, list):
        for item in obj:
            clean_obj(item)
    return obj


def main():
    repo_root = Path(__file__).resolve().parent.parent
    notebooks = sorted(repo_root.rglob("*.ipynb"))
    if not notebooks:
        print("No .ipynb files found.", file=sys.stderr)
        sys.exit(1)

    for nb_path in notebooks:
        try:
            data = json.loads(nb_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Skip {nb_path}: {e}", file=sys.stderr)
            continue
        before = json.dumps(data)
        clean_obj(data)
        if json.dumps(data) != before:
            nb_path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print(nb_path.relative_to(repo_root))
    print("Done.")


if __name__ == "__main__":
    main()
