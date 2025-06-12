import json
import tempfile
from pathlib import Path
from typing import Generator, Any
import pytest
from controller import ProgressController
import os


@pytest.fixture
def temp_progress_file(**kwargs: Any) -> Generator[Path, None, None]:
    default_progress = {
        "max_level": 5,
        "unlocked_level": 3,
        "completed_levels": [1, 2],
        "max_score": {"1": 3, "2": 5},
        "settings": {"sounds": True},
        "timestamps": {"last_played": "2025-06-11T18:00:00Z"},
    }

    fake_progress = {**default_progress, **kwargs}

    with tempfile.TemporaryDirectory() as tmpdir:
        progress_path = Path(tmpdir) / "progress.json"
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump(fake_progress, f)
        yield progress_path


def test_get_unlocked_levels_returns_correct_list(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))
    unlocked_levels = controller.get_unlocked_levels()
    assert unlocked_levels == [1, 2, 3], "Unlocked levels list is incorrect"


def test_get_unlocked_level_returns_correct_value(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))
    unlocked_level = controller.get_unlocked_level()
    assert unlocked_level == 3, "Unlocked level is incorrect"


def test_is_level_unlocked_returns_correct_value(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    assert controller.is_level_unlocked(1) is True, "Level 1 should be unlocked"
    assert controller.is_level_unlocked(3) is True, "Level 3 should be unlocked"
    assert controller.is_level_unlocked(4) is False, "Level 4 should not be unlocked"


def test_complete_level_adds_completed_level_and_updates_score(
    temp_progress_file: Path,
) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    controller.complete_level(level=3, score=10)

    progress = controller.adapter.read()
    assert 3 in progress.completed_levels, "Level 3 should be in completed levels"
    assert (
        progress.max_score.get("3") == 10
    ), "Score for level 3 should be updated to 10"
    assert progress.unlocked_level == 4, "Unlocked level should update to 4"
    assert (
        progress.timestamps.last_played is not None
    ), "Timestamp last_played should be set"


def test_complete_level_does_not_duplicate_completed_levels(
    temp_progress_file: Path,
) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    controller.complete_level(level=2, score=5)
    completed_before = controller.adapter.read().completed_levels.count(2)

    controller.complete_level(level=2, score=7)  # Higher score should update

    completed_after = controller.adapter.read().completed_levels.count(2)

    assert completed_before == 1, "Level 2 should be completed once before"
    assert completed_after == 1, "Level 2 should not be duplicated in completed levels"


def test_complete_level_updates_score_only_if_higher(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    controller.complete_level(level=2, score=5)
    assert controller.adapter.read().max_score["2"] == 5

    controller.complete_level(level=2, score=3)
    assert (
        controller.adapter.read().max_score["2"] == 5
    ), "Score should not update to lower value"

    controller.complete_level(level=2, score=10)
    assert (
        controller.adapter.read().max_score["2"] == 10
    ), "Score should update to higher value"


def test_complete_level_unlocks_next_level_only_if_needed(
    temp_progress_file: Path,
) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    controller.complete_level(level=2, score=5)
    assert (
        controller.adapter.read().unlocked_level == 3
    ), "Unlocked level should not change"

    controller.complete_level(level=3, score=5)
    assert (
        controller.adapter.read().unlocked_level == 4
    ), "Unlocked level should update to 4"


def test_complete_level_raises_error_for_invalid_level_and_score(
    temp_progress_file: Path,
) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    with pytest.raises(ValueError, match="Level must be greater than or equal to 1"):
        controller.complete_level(level=0, score=5)

    with pytest.raises(ValueError, match="Score cannot be negative"):
        controller.complete_level(level=1, score=-1)


def test_set_max_score_updates_score_correctly(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    controller.set_max_score(level=1, score=50)
    progress = controller.adapter.read()
    assert (
        progress.max_score.get("1") == 50
    ), "Max score for level 1 should be updated to 50"


def test_set_max_score_overwrites_existing_score(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    controller.set_max_score(level=2, score=30)
    assert controller.adapter.read().max_score.get("2") == 30

    controller.set_max_score(level=2, score=70)
    assert controller.adapter.read().max_score.get("2") == 70


def test_set_max_score_raises_error_for_invalid_level(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    with pytest.raises(ValueError, match="Invalid level or score."):
        controller.set_max_score(level=0, score=10)


def test_set_max_score_raises_error_for_negative_score(
    temp_progress_file: Path,
) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    with pytest.raises(ValueError, match="Invalid level or score."):
        controller.set_max_score(level=1, score=-5)


def test_get_max_score_returns_correct_value(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    assert controller.get_max_score(1) == 3
    assert controller.get_max_score(99) == 0


def test_get_completed_levels_returns_correct_list(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    assert controller.get_completed_levels() == [1, 2]


def test_update_settings_saves_and_updates_sounds(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))
    controller.update_settings(sounds=False)

    settings = controller.get_settings()

    assert settings.sounds is False
    reloaded_controller = ProgressController(filepath=str(temp_progress_file))
    assert reloaded_controller.get_settings().sounds is False


def test_get_settings_returns_settings_object(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    settings = controller.get_settings()

    assert settings.sounds is True


def test_get_last_played_returns_correct_timestamp(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    assert controller.get_last_played() == "2025-06-11T18:00:00Z"


def test_reset_progress_resets_and_loads_progress(temp_progress_file: Path) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))
    controller.update_settings(sounds=False)
    assert controller.get_settings().sounds is False

    controller.reset_progress()
    settings = controller.get_settings()
    assert settings.sounds is True


def test_delete_progress_removes_file_and_clears_memory(
    temp_progress_file: Path,
) -> None:
    controller = ProgressController(filepath=str(temp_progress_file))

    assert os.path.exists(temp_progress_file)
    controller.delete_progress()

    assert not os.path.exists(temp_progress_file)
    assert controller.progress is None
