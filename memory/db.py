import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


@dataclass
class Settings:
    sounds: bool = True


@dataclass
class Timestamps:
    last_played: Optional[str] = None


@dataclass
class Progress:
    unlocked_level: int = 1
    completed_levels: List[int] = field(default_factory=list)
    performance_score: Dict[str, int] = field(default_factory=dict)
    settings: Settings = field(default_factory=Settings)
    timestamps: Timestamps = field(default_factory=Timestamps)

    @classmethod
    def from_dict(cls, data: dict) -> "Progress":
        """Convert a dictionary into a Progress instance."""
        return cls(
            unlocked_level=data.get("unlocked_level", 1),
            completed_levels=data.get("completed_levels", []),
            performance_score=data.get("performance_score", {}),
            settings=Settings(**data.get("settings", {})),
            timestamps=Timestamps(**data.get("timestamps", {})),
        )


class ProgressJsonAdapter:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.progress: Optional[Progress] = None

    def load(self) -> Progress:
        """Load progress from the JSON file."""
        if not self.filepath.exists():
            logging.info("File does not exist. Creating new progress.")
            self.progress = Progress()
            return self.progress

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.progress = Progress.from_dict(data)
            logging.info("Progress loaded successfully.")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading progress: {e}. Resetting progress.")
            self.progress = Progress()
        return self.progress

    def save(self) -> None:
        """Save the current progress to the JSON file."""
        if self.progress is None:
            raise ValueError("No progress data to save")
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(asdict(self.progress), f, indent=4)
            logging.info("Progress saved successfully.")
        except IOError as e:
            logging.error(f"Error saving progress: {e}")

    def create(self, progress: Progress) -> None:
        """Create new progress and save it to the file."""
        self.progress = progress
        self.save()

    def read(self) -> Progress:
        """Read progress from memory or load it from the file."""
        if self.progress is None:
            return self.load()
        return self.progress

    def update(self, **kwargs) -> None:
        """Update specific fields in the progress."""
        if self.progress is None:
            self.load()
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                if key == "unlocked_level" and not isinstance(value, int):
                    raise ValueError("unlocked_level must be an integer")
                if key == "completed_levels" and not isinstance(value, list):
                    raise ValueError("completed_levels must be a list")
                setattr(self.progress, key, value)
            else:
                raise AttributeError(f"Progress has no attribute '{key}'")
        self.save()

    def delete(self) -> None:
        """Delete the progress file and reset in-memory progress."""
        if self.filepath.exists():
            self.filepath.unlink()
            logging.info("Progress file deleted.")
        self.progress = None

    def reset(self) -> None:
        """Reset progress to default and save it to the file."""
        self.progress = Progress()
        self.save()
        logging.info("Progress reset to default.")
