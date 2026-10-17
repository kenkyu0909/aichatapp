"""Render the self-contained HTML report from the saved fictional JSON log."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from simulate_conversation import HTML_FILE, JSON_FILE, render_html


def main() -> int:
    if not JSON_FILE.is_file():
        print("会話JSONがありません。シミュレーション結果を先に保存してください。")
        return 2
    state = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    render_html(state, HTML_FILE)
    print(f"HTML report rendered: {HTML_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
