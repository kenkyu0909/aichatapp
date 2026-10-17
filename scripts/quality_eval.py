"""Independent grader for generated reply candidates.

This module deliberately imports nothing from ``app.py``. The quality-check
runners previously scored generated text with the same product helpers that
produced or filtered it, so a shared blind spot could report a defective set as
PASS. Everything here is an independent re-implementation: its own
normalization, its own similarity metric, its own placeholder and punctuation
checks, and its own first-person claim scan.

The functions are pure and offline-testable. Nothing in this module performs
network or filesystem access.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable, Sequence

_SENTENCE_SEPARATORS = re.compile(r"[。．.!?！？\n\r,、，;；]+")
_TERMINAL = "。．.!?！？"
_FILLERS = (
    "ですね", "ますね", "ますよ", "ですよ", "でしょうね", "そうですね",
    "いいですね", "わかります", "たしかに", "なるほど", "そうなんですね",
)

# First-person assertion markers. Independent of the product's regexes.
_FIRST_PERSON = re.compile(r"(?:私は|私も|僕は|僕も|俺は|俺も|自分は|わたしは|わたしも)")
_INTERROGATIVE = re.compile(r"[?？]|ですか|ますか|でしょうか|かな|どう")

# Topic lexicon used only by this grader.
_TOPIC_LEXICON: dict[str, tuple[str, ...]] = {
    "映画": ("映画", "作品", "スクリーン"),
    "カフェ": ("カフェ", "喫茶店", "コーヒー", "珈琲"),
    "旅行": ("旅行", "旅", "温泉", "観光"),
    "読書": ("読書", "本", "小説", "漫画"),
    "音楽": ("音楽", "ライブ", "ギター", "ピアノ"),
    "スポーツ": ("スポーツ", "運動", "ジム", "ランニング"),
    "料理": ("料理", "自炊", "お菓子作り"),
    "ペット": ("ペット", "犬", "猫", "動物"),
    "買い物": ("買い物", "ショッピング"),
    "ゲーム": ("ゲーム", "ゲームセンター"),
    "散歩": ("散歩", "ウォーキング"),
    "美術": ("美術館", "絵画", "アート", "芸術"),
}


def normalize_text(text: str) -> str:
    """Fold width, collapse whitespace, and strip. No product helpers reused."""
    folded = unicodedata.normalize("NFKC", str(text))
    return re.sub(r"\s+", " ", folded).strip()


def clause_split(text: str) -> list[str]:
    """Split a message into clauses on sentence terminators and newlines."""
    return [part.strip() for part in _SENTENCE_SEPARATORS.split(text) if part.strip()]


def char_ngrams(text: str, n: int = 3) -> set[str]:
    """Character n-grams over normalized text with separators removed."""
    compact = _SENTENCE_SEPARATORS.sub("", normalize_text(text))
    if len(compact) < n:
        return {compact} if compact else set()
    return {compact[index:index + n] for index in range(len(compact) - n + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    """Jaccard similarity of two sets, treating two empty sets as identical."""
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def has_near_duplicate_candidates(texts: Sequence[str], *, threshold: float = 0.9) -> bool:
    """True when any two candidates are near-duplicates by character n-gram overlap."""
    grams = [char_ngrams(text) for text in texts]
    for index, left in enumerate(grams):
        for right in grams[index + 1:]:
            if jaccard(left, right) >= threshold:
                return True
    return False


def _strip_filler(text: str) -> str:
    stripped = normalize_text(text)
    for filler in _FILLERS:
        stripped = stripped.replace(filler, "")
    return _SENTENCE_SEPARATORS.sub("", stripped)


def has_redundant_reaction_set(texts: Sequence[str], *, threshold: float = 0.5) -> bool:
    """True when candidate first clauses are near-identical reactions."""
    heads = []
    for text in texts:
        clauses = clause_split(_strip_filler(text))
        heads.append(char_ngrams(clauses[0] if clauses else ""))
    for index, left in enumerate(heads):
        for right in heads[index + 1:]:
            if left and right and jaccard(left, right) >= threshold:
                return True
    return False


def has_placeholder(text: str) -> bool:
    """Independent placeholder detection (own patterns)."""
    pattern = re.compile(
        r"〇{2,}|\[(?:名前|name|your name|氏名|placeholder|xxx+)\]"
        r"|\{\{(?:名前|name)\}\}|(?<![A-Za-z])TBD(?![A-Za-z])|(?<![A-Za-z])XXX+(?![A-Za-z])",
        re.IGNORECASE,
    )
    return bool(pattern.search(normalize_text(text)))


def has_missing_sentence_break(text: str) -> bool:
    """True when a long message has no sentence break at all."""
    compact = _SENTENCE_SEPARATORS.sub("", normalize_text(text))
    if len(compact) < 40:
        return False
    return not any(char in normalize_text(text) for char in _TERMINAL)


def has_meeting_related_question(text: str) -> bool:
    """True when a candidate asks the partner about a real meeting."""
    for clause in clause_split(text):
        if _INTERROGATIVE.search(clause) and re.search(
            r"会(?:う|えますか|いましょうか)|お会い|会った|一緒に行|デート|待ち合わせ",
            clause,
        ):
            return True
    return False


def untrusted_first_person_topics(
    texts: Iterable[str], trusted_claims: Sequence[str] = ()
) -> list[str]:
    """Topics asserted by the candidate in the first person without grounding.

    Independent of the product's claim catalog. Interrogative clauses are
    skipped; a topic is ignored when a trusted claim fragment grounds it.
    """
    grounded = [normalize_text(claim) for claim in trusted_claims if claim]
    found: list[str] = []
    for text in texts:
        for clause in clause_split(text):
            if not _FIRST_PERSON.search(clause) or _INTERROGATIVE.search(clause):
                continue
            normalized_clause = normalize_text(clause)
            for topic, tokens in _TOPIC_LEXICON.items():
                if not any(token in normalized_clause for token in tokens):
                    continue
                if any(token in claim for claim in grounded for token in tokens):
                    continue
                if topic not in found:
                    found.append(topic)
    return found


def all_candidates_answer(texts: Sequence[str], tokens: Sequence[str]) -> bool:
    """True only when EVERY candidate mentions one of the required tokens."""
    if not tokens:
        return True
    return all(any(token in text for token in tokens) for text in texts)


def independent_quality_verdict(
    texts: Sequence[str],
    *,
    trusted_claims: Sequence[str] = (),
    required_answer_tokens: Sequence[str] = (),
    require_all_answer: bool = False,
    duplicate_threshold: float = 0.9,
    reaction_threshold: float = 0.5,
) -> dict[str, Any]:
    """Independent PASS/FAIL evaluation of a candidate set with reasons."""
    reasons: list[str] = []
    # The product's absolute rule is that candidate text must NOT contain 、 or 。;
    # the style uses line breaks and ！？ instead.
    punctuation = any("、" in text or "。" in text for text in texts)
    if punctuation:
        reasons.append("missing_japanese_punctuation")
    placeholders = [i for i, text in enumerate(texts) if has_placeholder(text)]
    if placeholders:
        reasons.append("placeholder_text")
    missing_breaks = [i for i, text in enumerate(texts) if has_missing_sentence_break(text)]
    if missing_breaks:
        reasons.append("missing_sentence_break")
    duplicates = has_near_duplicate_candidates(texts, threshold=duplicate_threshold)
    if duplicates:
        reasons.append("near_duplicate_candidates")
    redundant = has_redundant_reaction_set(texts, threshold=reaction_threshold)
    if redundant:
        reasons.append("redundant_reactions")
    unsupported = untrusted_first_person_topics(texts, trusted_claims)
    if unsupported:
        reasons.append("unsupported_first_person_claim")
    answer_violation = False
    if require_all_answer and required_answer_tokens:
        answer_violation = not all_candidates_answer(texts, required_answer_tokens)
        if answer_violation:
            reasons.append("answer_missing_in_some_candidate")
    return {
        "punctuation_violation": punctuation,
        "placeholder_violation": bool(placeholders),
        "missing_sentence_break_violation": bool(missing_breaks),
        "duplicate_violation": duplicates,
        "redundant_reaction_violation": redundant,
        "unsupported_topics": unsupported,
        "answer_violation": answer_violation,
        "result": "FAIL" if reasons else "PASS",
        "reasons": reasons,
    }


def combine_quality_verdict(
    product_pass: bool,
    independent_pass: bool,
    *,
    http_status: int,
    error_code: str | None,
) -> str:
    """Combine the product and independent verdicts; fail when either fails."""
    if http_status >= 500 or error_code:
        return "BLOCKED"
    if product_pass and independent_pass:
        return "PASS"
    return "FAIL"
