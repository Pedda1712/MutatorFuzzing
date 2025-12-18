from pathlib import Path
from datetime import datetime

from .FuzzingTarget import FuzzingTarget

class GCCFuzzingTarget(FuzzingTarget[str]):
    """Provides a local GCC build as a target."""

    build_directory: Path
    """Directory containing GCCs gcno coverage infofiles."""

    coverage_accumulation_directory: Path
    """Directory where gcda files will be directed to."""

    subdirectories: list[Path]
    """When non-empty, only the gcno files in these subdirectories will be considered."""

    def __init__(self, build_directory: Path, subdirectories: list[Path] = [Path(".")], coverage_accumulation_directory: Path | None = None):
        self.build_directory = build_directory
        self.subdirectories = subdirectories
        if coverage_accumulation_directory is None:
            self.coverage_accumulation_directory = Path(Path.home(), Path('tmp'), Path(f'GCCRun{datetime.now()}'))
        else:
            self.coverage_accumulation_directory = coverage_accumulation_directory
        print(self.coverage_accumulation_directory)
