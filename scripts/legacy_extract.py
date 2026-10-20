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
    "居住地": r"住んで|在住|実家|地元|引っ越|(?:都|道|府|県|区|市|町|村)",
    "仕事学校": r"仕事|働いて|勤務|職場|職種|会社|アルバイト|パート|正社員|学校|大学|大学院|学生|学部|学科|専攻|勉強|研究",
    "趣味": r"趣味|好き|ハマって|はまって|よく(?:行|見|読|聞|観|作|や)|集めて|巡り",
    "食べ物": r"食べ|飲み|好物|料理|スイーツ|甘い|辛い|コーヒー|お茶|パン|カレー",
    "休日": r"休日|休みの日|週末|過ごし|のんびり|散歩|お出かけ",
    "苦手": r"苦手|にがて|嫌い|きらい|克服|怖い|不安",
    "性格": r"性格|穏やか|マイペース|心配性|人見知り|せっかち",
}
FIRST_PERSON = re.compile(r"私|僕|俺|自分|うち|わたし|ぼく")
PARTNER_DIRECTED = re.compile(r"あなた|君|きみ")
QUESTION_LIKE = re.compile(r"[?？]|ですか|ますか|でしょうか|なんですか|ことある|ますかー")
IMPRESSION = re.compile(r"素敵ですね|いいですね|行かれて|お好き|憧れ|うらやま|楽しそう|すぎます|ください|すごいです|じゃないですか|すごくないですか")
SELF_STATEMENT = re.compile(r"(?:私|僕|俺|自分|うち|わたし|ぼく)(?:は|も|が)|(?:しています|してます|ています|です|ます|ません|好きです|苦手です|飲めない)$")


def _is_self_statement(sentence: str) -> bool:
    """本人が自分のことを述べている文だけを残す (T495)."""
    if QUESTION_LIKE.search(sentence) or IMPRESSION.search(sentence):
        return False
    return bool(SELF_STATEMENT.search(sentence))
JOKE = re.compile(r"笑|ｗ|w\)|（笑）")
TEMPORARY = re.compile(r"今日|明日|明後日|昨日|来週|今週|来月|今度|次回|予定|待ち合わせ|約束|今から|あとで")


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", str(text)).strip()


def _replace_name(value: object, real_name: str, display_name: str) -> object:
    """出力に含まれる本名を置き換える (T495).

    リポジトリは PUBLIC のため、出力（JSON/MD/HTML）には実名を残さない。
    """
    if not real_name:
        return value
    if isinstance(value, str):
        return value.replace(real_name, display_name)
    if isinstance(value, list):
        return [_replace_name(item, real_name, display_name) for item in value]
    if isinstance(value, dict):
        return {key: _replace_name(item, real_name, display_name) for key, item in value.items()}
    return value


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


_SCHOOL_PROFILE = re.compile(r"大学院|大学|学生|学部|専攻|研究")
_EMPLOYMENT = re.compile(r"会社|勤務|デスクワーク|会社員|正社員|パート|アルバイト|フリーランス|在宅|リモートワーク")


def _job_conflicts_with_profile(sentence: str, occupation: str) -> bool:
    """profile の職業が学生系のとき、勤務を示す申告は食い違いとして要確認にする (T495)."""
    if not occupation or not _SCHOOL_PROFILE.search(occupation):
        return False
    return bool(_EMPLOYMENT.search(sentence))


def _extract_message_facts(
    messages: list[dict], max_per_category: int, occupation: str = ""
) -> tuple[dict[str, list[dict]], list[dict]]:
    facts: dict[str, list[dict]] = {category: [] for category in (*CATEGORY_PATTERNS, "言い回し")}
    needs_review: list[dict] = []
    seen: set[str] = set()
    for message in messages:
        text = _normalize(message.get("content", ""))
        if not text or len(text) > 160:
            continue
        if JOKE.search(text) or TEMPORARY.search(text):
            continue
        if not FIRST_PERSON.search(text):
            continue
        for sentence in re.split(r"[。！!？?\n]+", text):
            sentence = _normalize(sentence)
            if len(sentence) < 8 or PARTNER_DIRECTED.search(sentence):
                continue
            if not _is_self_statement(sentence):
                continue
            key = re.sub(r"[\s、。！!？?]", "", sentence)
            if key in seen:
                continue
            category = _classify(sentence)
            if not category:
                continue
            # T495: プロフィールの職業（学生・大学院など）と食い違う仕事の申告は
            # 確定事実に入れず、要確認として別に置く（推測を避ける）。
            if category == "仕事学校" and _job_conflicts_with_profile(sentence, occupation):
                needs_review.append(
                    {
                        "text": sentence,
                        "source_ids": [message.get("id")],
                        "reason": "profileの職業と食い違う可能性があるため要確認",
                    }
                )
                continue
            if len(facts[category]) >= max_per_category:
                continue
            seen.add(key)
            facts[category].append({"text": sentence, "source_ids": [message.get("id")]})
    # よく使う言い回し: 短く繰り返し出る一人称の文だけ（頻度2回以上）。推測はしない。
    phrase_counts: dict[str, dict] = {}
    for message in messages:
        text = _normalize(message.get("content", ""))
        if not text or len(text) > 60 or PARTNER_DIRECTED.search(text) or QUESTION_LIKE.search(text):
            continue
        if not FIRST_PERSON.search(text):
            continue
        key = re.sub(r"[\s、。！!？?]", "", text)
        if 4 <= len(key) <= 16:
            entry = phrase_counts.setdefault(key, {"text": text, "ids": []})
            entry["ids"].append(message.get("id"))
    for entry in phrase_counts.values():
        if len(entry["ids"]) >= 2 and len(facts["言い回し"]) < max_per_category:
            facts["言い回し"].append({"text": entry["text"], "source_ids": entry["ids"][:3]})
    return {category: items for category, items in facts.items() if items}, needs_review


def _profile_facts(profile: dict) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in ("name", "gender", "age", "occupation", "hobbies", "personality", "speaking_style", "profile", "my_info"):
        value = profile.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value.strip()
    return result


def _write_markdown(
    path: Path,
    profile: dict,
    knowledge: list[dict],
    facts: dict[str, list[dict]],
    needs_review: list[dict] = (),
) -> None:
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
    if needs_review:
        lines.append("")
        lines.append("## 要確認（プロフィールと食い違う可能性があるため確定事実には入れていない）")
        for item in needs_review:
            ids = ",".join(str(i) for i in item.get("source_ids", []))
            lines.append(f"- {item['text']}  _(id: {ids})_")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_html(path: Path, profile: dict, knowledge: list[dict], facts: dict[str, list[dict]]) -> None:
    def esc(value: object) -> str:
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    rows: list[str] = []
    rows.append('<h2>user_profile</h2><table border="1" cellspacing="0" cellpadding="4">')
    for key, value in profile.items():
        rows.append(f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>")
    rows.append("</table>")
    rows.append('<h2>抽出した本人の事実（カテゴリ別・根拠ID付き）</h2><table border="1" cellspacing="0" cellpadding="4">')
    rows.append("<tr><th>カテゴリ</th><th>事実</th><th>根拠ID</th></tr>")
    for category, items in facts.items():
        for item in items:
            ids = ",".join(str(i) for i in item.get("source_ids", []))
            rows.append(f"<tr><td>{esc(category)}</td><td>{esc(item['text'])}</td><td>{esc(ids)}</td></tr>")
    rows.append("</table>")
    rows.append('<h2>user_knowledge（本人の事実ではないため facts からは除外）</h2><table border="1" cellspacing="0" cellpadding="4">')
    rows.append("<tr><th>質問</th><th>回答</th></tr>")
    for item in knowledge:
        rows.append(f"<tr><td>{esc(_normalize(item.get('question', '')))}</td><td>{esc(_normalize(item.get('answer', '')))}</td></tr>")
    rows.append("</table>")
    html = (
        "<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\">"
        "<title>旧アプリから抽出した本人の事実</title></head><body>"
        "<h1>旧アプリから抽出した本人の事実（レビュー用）</h1>"
        + "".join(rows)
        + "<p>自動抽出です。誤りはこのファイルを直すか、取り込み前の JSON から削ってください。</p>"
        "</body></html>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract legacy user facts (read-only)")
    parser.add_argument("--db", required=True, help="legacy app.db path")
    parser.add_argument("--out-json", required=True, help="output JSON path")
    parser.add_argument("--out-md", required=True, help="output Markdown path")
    parser.add_argument("--out-html", default="", help="output HTML review path")
    parser.add_argument("--max-per-category", type=int, default=12)
    parser.add_argument(
        "--replace-name",
        default="",
        help="本名を出力に残さないための置き換え名（例: S）。指定すると user_profile の名前を実名として置換する",
    )
    args = parser.parse_args()

    profile_row, knowledge, messages = _read_legacy(args.db)
    real_name = str((profile_row.get("name") or "")).strip()
    if args.replace_name and real_name:
        # T495: 実名を出力に残さない。読み込み直後に置換してから抽出する。
        profile_row = _replace_name(profile_row, real_name, args.replace_name)
        knowledge = _replace_name(knowledge, real_name, args.replace_name)
        messages = _replace_name(messages, real_name, args.replace_name)
    profile = _profile_facts(profile_row)
    facts, needs_review = _extract_message_facts(messages, args.max_per_category, profile.get("occupation", ""))

    # T495: user_knowledge は本人の事実ではない（相手についての回答や無意味な値）ため
    # facts には含めない。レビュー用に JSON/HTML へは残す。
    flat_facts: list[str] = []
    for key, value in profile.items():
        flat_facts.append(f"{key}: {value}")
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
        "needs_review": needs_review,
    }
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(Path(args.out_md), profile, knowledge, facts, needs_review)
    if args.out_html:
        _write_html(Path(args.out_html), profile, knowledge, facts)
    print(f"wrote {out_json} ({len(flat_facts)} facts) and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
