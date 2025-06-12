from datetime import datetime, timedelta
from game.game_engine import calculate_performance_score


def test_calculate_performance_score_fast_completion():
    start_time = datetime(2025, 1, 1, 12, 0, 0)
    end_time = start_time + timedelta(seconds=5)
    score = calculate_performance_score(start_time, end_time)
    assert score >= 7


def test_calculate_performance_score_medium_completion():
    start_time = datetime(2025, 1, 1, 12, 0, 0)
    end_time = start_time + timedelta(seconds=30)
    score = calculate_performance_score(start_time, end_time)
    assert 2 <= score < 7


def test_calculate_performance_score_slow_completion():
    start_time = datetime(2025, 1, 1, 12, 0, 0)
    end_time = start_time + timedelta(seconds=120)
    score = calculate_performance_score(start_time, end_time)
    assert score <= 1