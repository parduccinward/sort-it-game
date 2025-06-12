import logging
from typing import List, Optional
from datetime import datetime

from db import ProgressJsonAdapter, Settings, Progress


class ProgressController:
    DEFAULT_FILEPATH = "memory/progress.json"

    def __init__(
        self, filepath: str = DEFAULT_FILEPATH, progress: Optional[Progress] = None
    ):
        self.adapter = ProgressJsonAdapter(filepath)
        self.progress: Optional[Progress] = (
            progress if progress else self.adapter.load()
        )

    def _require_progress(self) -> None:
        if self.progress is None:
            raise ValueError("Progress data is not loaded.")

    def get_unlocked_levels(self) -> List[int]:
        """Return a list of all levels the player can access."""
        self._require_progress()
        return list(range(1, self.progress.unlocked_level + 1))

    def get_unlocked_level(self) -> int:
        """Return the highest unlocked level number."""
        self._require_progress()
        return self.progress.unlocked_level

    def is_level_unlocked(self, level: int) -> bool:
        """Check if a given level is unlocked."""
        self._require_progress()
        return level <= self.progress.unlocked_level

    def complete_level(self, level: int, score: int) -> None:
        """
        Mark a level as completed, update score if higher,
        unlock the next level, and update last played timestamp.
        """
        self._require_progress()
        if level < 1:
            raise ValueError("Level must be greater than or equal to 1.")
        if score < 0:
            raise ValueError("Score cannot be negative.")

        if level not in self.progress.completed_levels:
            self.progress.completed_levels.append(level)
            logging.debug(f"Level {level} added to completed levels.")

        prev_score = self.progress.performance_score.get(str(level), 0)
        if score > prev_score:
            self.progress.performance_score[str(level)] = score
            logging.debug(
                f"Score for level {level} updated from {prev_score} to {score}."
            )

        if level >= self.progress.unlocked_level:
            self.progress.unlocked_level = level + 1
            logging.debug(f"Unlocked level updated to {self.progress.unlocked_level}.")

        self.progress.timestamps.last_played = datetime.utcnow().isoformat()
        self.adapter.save()

        logging.info(f"Level {level} completed with score {score}. Progress saved.")

    def set_performance_score(self, level: int, score: int) -> None:
        """Directly update the maximum score for a level."""
        self._require_progress()
        if level < 1 or score < 0:
            raise ValueError("Invalid level or score.")
        self.progress.performance_score[str(level)] = score
        self.adapter.save()
        logging.info(f"Max score for level {level} set to {score}.")

    def get_performance_score(self, level: int) -> int:
        """Return the highest score achieved for a specific level."""
        self._require_progress()
        return self.progress.performance_score.get(str(level), 0)

    def get_completed_levels(self) -> List[int]:
        """Return a list of levels the player has completed."""
        self._require_progress()
        return self.progress.completed_levels

    def update_settings(self, sounds: bool) -> None:
        """Update the user's sound settings."""
        self._require_progress()
        self.progress.settings.sounds = sounds
        self.adapter.save()
        logging.info(f"Settings updated: sounds = {sounds}")

    def get_settings(self) -> Settings:
        """Return the current settings object."""
        self._require_progress()
        return self.progress.settings

    def get_last_played(self) -> Optional[str]:
        """Return the ISO timestamp of the last time the game was played."""
        self._require_progress()
        return self.progress.timestamps.last_played

    def reset_progress(self) -> None:
        """Reset all progress to initial state."""
        self.adapter.reset()
        self.progress = self.adapter.read()
        logging.info("Progress has been reset.")

    def delete_progress(self) -> None:
        """Delete all progress data and unload from memory."""
        self.adapter.delete()
        self.progress = None
        logging.info("Progress file has been deleted.")
