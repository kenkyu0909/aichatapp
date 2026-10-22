from scripts.run_quality_checks_004 import answer_fact_is_present, provider_priority_matches


def test_live_evaluator_accepts_natural_paraphrase_and_removed_quotation_marks():
    assert answer_fact_is_present("最近は架空作品の青い灯台を観ましたよ", ["最近", "青い灯台", "観ました"])
    assert answer_fact_is_present("ミステリーを読むことが多いです！", ["ミステリー", "読むことが多い"])
    assert not answer_fact_is_present("映画を観ました", ["青い灯台", "観ました"])


def test_provider_priority_checks_alias_and_model_as_a_sequence():
    expected = [
        {"api_alias": "API1", "model": "gemini-3.5-flash-lite"},
        {"api_alias": "API2", "model": "gemini-3.5-flash-lite"},
        {"api_alias": "API1", "model": "gemini-3.1-flash-lite"},
        {"api_alias": "API2", "model": "gemini-3.1-flash-lite"},
    ]
    assert provider_priority_matches(expected)
    assert not provider_priority_matches([expected[2], expected[3], expected[0], expected[1]])
