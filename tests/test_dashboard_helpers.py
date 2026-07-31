from ophbench.dashboard import _leaderboard_rows, _metric_rank_table, _text_or_dash


def test_zero_is_not_rendered_as_missing():
    assert _text_or_dash(0) == "0"
    assert _text_or_dash(0.0) == "0.0"


def test_leaderboard_hides_metrics_missing_for_every_model():
    runs = [
        {
            "model_id": "model-a",
            "checkpoint_id": "checkpoint-a",
            "metrics": {
                "Macro-F1": 0.8,
                "Balanced Accuracy": 0.7,
                "Accuracy": 0.9,
                "Top-3 Accuracy": None,
                "Macro-AUROC": 0.95,
            },
        }
    ]

    rendered = _leaderboard_rows(runs)

    assert 'data-metrics="4"' in rendered
    assert "Top-3" not in rendered


def test_metric_table_explains_rank_and_gap_to_best():
    rows = [
        {"model_id": "model-a", "Macro-F1": 0.8},
        {"model_id": "model-b", "Macro-F1": 0.7},
    ]

    rendered = _metric_rank_table(rows)

    assert "#1" in rendered
    assert "#2 · -0.100" in rendered
