"""Extract the user's own facts from a legacy chat app SQLite database.

Generic and data-free: the database path and the output paths are taken from
arguments or environment variables, so no personal data or machine-specific
path is stored in the repository. The legacy database is opened read-only.

Example:
    python scripts/legacy_extract.py --db <path/to/app.db> \
        --out-json <out/user_facts.json> --out-md <out/user_facts.md>

The extraction is intentionally modest and rule-based: it reads user_profile,
user_knowledge, and hand-written self messages, keeps a small number of
fact-like sentences per category, and records the source message ids so the
user can review and correct the result.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from pathlib import Path

CATEGORY_PATTERNS = {
    "居住地": r"住んで|在住|実家|地元|(?:都|道|府|県|区|市|町|村)$",
    "仕事": r"仕事|働いて|勤務|職場|職種|会社|アルバイト|パート|正社員",
    "趣味": r"趣味|好き|ハマって|はまって|よく(?:行|見|読|聞|観|作|や)|集めて|巡り",
    "食べ物": r"食べ|飲み|好物|料理|スイーツ|甘い|辛い|コーヒー|お茶|パン|カレー",
    "休日": r"休日|休みの日|週末|過ごし|のんびり|散歩|お出かけ",
    "性格": r"性格|穏やか|マイペース|心配性|人見知り|せっかち",
    "言い回し": r"^.{2,14}$",
}
FIRST_PERSON = re.compile(r"私|僕|俺|自分|うち|わたし|ぼく")
PARTNER_DIRECTED = re.compile(r"あなた|君|きみ|くん|さん|ちゃん")
QUESTION_ONLY = re.compile(r"[?？]\s*$")
JOKE = re.compile(r"笑|ｗ|w\)|（笑）")
TEMPORARY = re.compile(r"今日|明日|明後日|昨日|来週|今週|来月|今度|次回|予定|待ち合わせ|約束|今から|あとで")


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", str(text)).strip()


def _read_legacy(db_path: str) -> tuple[dict, list[dict], list[dict]]:
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    try:
        profile = dict(con.execute("SELECT * FROM user_profile LIMIT 1").fetchone() or {})
        knowledge = [dict(row) for row in con.execute("SELECT question, answer FROM user_knowledge")]
        messages = [
            dict(row)
            for row in con.execute(
                "SELECT id, content FROM messages WHERE sender='self' AND source='manual'"
            )
        ]
    finally:
        con.close()
    return profile, knowledge, messages


def _classify(sentence: str) -> str | None:
    for category, pattern in CATEGORY_PATTERNS.items():
        if category == "言い回し":
            continue
        if re.search(pattern, sentence):
            return category
    return None


def _extract_message_facts(messages: list[dict], max_per_category: int) -> dict[str, list[dict]]:
    facts: dict[str, list[dict]] = {category: [] for category in CATEGORY_PATTERNS}
    seen: set[str] = set()
    for message in messages:
        text = _normalize(message.get("content", ""))
        if not text or len(text) > 160:
            continue
        if JOKE.search(text) or TEMPORARY.search(text) or QUESTION_ONLY.search(text):
            continue
        if not FIRST_PERSON.search(text):
            continue
        for sentence in re.split(r"[。！!？?\n]+", text):
            sentence = _normalize(sentence)
            if len(sentence) < 8 or PARTNER_DIRECTED.search(sentence):
                continue
            if not FIRST_PERSON.search(sentence):
                continue
            key = re.sub(r"[\s、。！!？?]", "", sentence)
            if key in seen:
                continue
            category = _classify(sentence)
            if not category:
                continue
            if len(facts[category]) >= max_per_category:
                continue
            seen.add(key)
            facts[category].append({"text": sentence, "source_ids": [message.get("id")]})
    return {category: items for category, items in facts.items() if items}


def _profile_facts(profile: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in ("name", "gender", "age", "occupation", "hobbies", "personality", "speaking_style", "profile", "my_info"):
        value = profile.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value.strip()
    return result


def _write_markdown(path: Path, profile: dict, knowledge: list[dict], facts: dict[str, list[dict]]) -> None:
    lines = ["# 旧アプリから抽出した本人の事実（レビュー用）", ""]
    lines.append("## user_profile")
    for key, value in profile.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## user_knowledge（質問と回答）")
    for item in knowledge:
        lines.append(f"- Q: {_normalize(item.get('question', ''))}")
        lines.append(f"  A: {_normalize(item.get('answer', ''))}")
    lines.append("")
    lines.append("## 手入力メッセージから抽出した事実（カテゴリ別・根拠ID付き）")
    for category, items in facts.items():
        lines.append(f"### {category}")
        for item in items:
            ids = ",".join(str(i) for i in item.get("source_ids", []))
            lines.append(f"- {item['text']}  _(id: {ids})_")
        lines.append("")
    lines.append("※ この結果は自動抽出です。誤りや相手の話が混ざっている場合は、ここの文を削ってください。")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract legacy user facts (read-only)")
    parser.add_argument("--db", required=True, help="legacy app.db path")
    parser.add_argument("--out-json", required=True, help="output JSON path")
    parser.add_argument("--out-md", required=True, help="output Markdown path")
    parser.add_argument("--max-per-category", type=int, default=12)
    args = parser.parse_args()

    profile_row, knowledge, messages = _read_legacy(args.db)
    profile = _profile_facts(profile_row)
    facts = _extract_message_facts(messages, args.max_per_category)

    flat_facts: list[str] = []
    for key, value in profile.items():
        flat_facts.append(f"{key}: {value}")
    for item in knowledge:
        answer = _normalize(item.get("answer", ""))
        if answer:
            flat_facts.append(answer)
    for items in facts.values():
        flat_facts.extend(item["text"] for item in items)

    payload = {
        "source": "legacy app.db (read-only)",
        "profile": profile,
        "knowledge": [
            {"question": _normalize(item.get("question", "")), "answer": _normalize(item.get("answer", ""))}
            for item in knowledge
        ],
        "facts": facts,
        "facts_flat": flat_facts,
    }
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(Path(args.out_md), profile, knowledge, facts)
    print(f"wrote {out_json} and {args.out_md} ({len(flat_facts)} facts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
