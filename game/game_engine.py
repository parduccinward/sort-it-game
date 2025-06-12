from datetime import datetime


def calculate_performance_score(
    start_time: datetime,
    end_time: datetime,
    base_score: float = 10.0,
    factor: float = 0.1,
) -> int:
    """
    Calculate the performance score based on the time taken to complete a level.
    The score decreases as the duration increases, using an exponential decay formula.
    """
    duration = (end_time - start_time).total_seconds()
    score = base_score * (1 / (1 + factor * duration))
    return max(0, round(score))
