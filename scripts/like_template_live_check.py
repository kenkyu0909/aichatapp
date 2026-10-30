"""メッセージ付きいいね（likeモード）のテンプレート適合を実APIで確認する。

必ず架空のプロフィールだけを使う。実行回数は引数で制御（既定5回）。
出力は候補本文と3行テンプレートの適合判定のみ。キー等の機密は出力しない。
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

_CASES = [
    ("ゆい", "休日は水族館と読書を楽しんでいます。クラゲが特にお気に入りです。"),
    ("あおい", "散歩や喫茶店巡りが好きです。最近は小説をよく読みます。"),
    ("かえで", "映画が趣味です。週末はよくシネコンに通っています。"),
    ("みお", "旅行が大好きで、国内の温泉巡りをしています。犬を飼っています。"),
    ("さき", "カフェでゆっくりするのが好きです。甘いものに目がありません。"),
]

_GREETING = re.compile(r"^[^、。！？!?\n]{1,20}さん、(?:初めまして|はじめまして)[!！]?$")


def _check(text: str, name: str, description: str) -> list[str]:
    problems: list[str] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return ["3行テンプレートに沿っていない（行数不足）"]
    if _GREETING.match(lines[0]):
        if not lines[0].startswith(name):
            problems.append("1行目に相手の名前がない")
    elif lines[0] in ("初めまして！", "はじめまして！"):
        problems.append("1行目に「〇〇さん、」の呼びかけがない")
    else:
        problems.append(f"1行目が挨拶の形でない: {lines[0]!r}")
    body = "\n".join(lines[1:])
    if "、" in body or "。" in body:
        problems.append("2行目以降に句読点がある")
    grams = {description[i:i + 4] for i in range(max(len(description) - 3, 0))}
    tokens = {
        token
        for token in re.split(r"[、。！？!?\n]|は|が|を|に|と|で|や|の|も|から|して|です|ます|ので", description)
        if len(token.strip()) >= 2
    }
    tokens.update(gram for gram in grams)
    if not any(token in body for token in tokens):
        problems.append("2行目がプロフィールの言葉に触れていない")
    if not re.search(r"話し|話が", text):
        problems.append("お話ししたい気持ちがない")
    if re.search(r"させていただ|拝見|と思っております", text):
        problems.append("固い敬語が残っている")
    return problems


def main() -> None:
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    with tempfile.TemporaryDirectory(prefix="like-template-check-") as directory:
        os.environ["APP_DATA_DIR"] = directory
        from app import app

        with TestClient(app) as client:
            profile = client.put("/api/profile", json={
                "content": "20代男性。カフェ巡りと映画と読書が好き。親しみやすいカジュアル敬語で短めに話す。",
                "avoid": "自分の経験を勝手に作らない",
            })
            assert profile.status_code == 200, profile.text

            failures = 0
            for index, (name, description) in enumerate(_CASES[:rounds], start=1):
                response = client.post("/api/generate", json={
                    "mode": "like", "name": name, "description": description,
                    "count": 3, "response_version": 2, "tone": "自動",
                })
                if response.status_code != 200:
                    print(f"[{index}] {name}: HTTP {response.status_code} {response.json().get('detail', '')}")
                    failures += 1
                    continue
                data = response.json()
                if data.get("demo"):
                    print(f"[{index}] {name}: デモ応答（APIキー未設定の可能性）")
                    failures += 1
                    continue
                if not data.get("recommended"):
                    print(f"[{index}] {name}: 候補なし response_keys={sorted(data.keys())}")
                    print(f"    generation_blocked={data.get('generation_blocked')} needs_user_info={data.get('needs_user_info')}")
                    print(f"    user_info_reason={data.get('user_info_reason')}")
                    print(f"    candidate_notice={data.get('candidate_notice')}")
                    rejected = data.get("candidate_rejection_details") or data.get("candidate_rejection_summary")
                    if rejected:
                        print(f"    rejection={str(rejected)[:600]}")
                    failures += 1
                    continue
                candidates = [data["recommended"], *data["alternatives"]]
                print(f"[{index}] {name}（model={data.get('model')}）")
                round_bad = False
                for candidate in candidates:
                    problems = _check(candidate["text"], name, description)
                    mark = "OK " if not problems else "NG "
                    if problems:
                        round_bad = True
                    print(f"  {mark}{candidate['label']}: {candidate['text'].replace(chr(10), ' / ')}")
                    for problem in problems:
                        print(f"     → {problem}")
                if round_bad:
                    failures += 1
            print(f"結果: {rounds - failures}/{rounds} 件がテンプレート適合")


if __name__ == "__main__":
    main()
