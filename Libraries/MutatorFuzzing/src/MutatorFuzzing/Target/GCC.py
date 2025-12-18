from pathlib import Path
from datetime import datetime

from .FuzzingTarget import FuzzingTarget

class GCC(FuzzingTarget[str]):
    """Provides a local GCC build as a target."""

    build_directory: Path
    """Directory containing GCCs gcno coverage infofiles."""

    binary_directory: Path
    """Directory containing the GCC binary."""

    coverage_accumulation_directory: Path
    """Directory where gcda files will be directed to."""

    created_tmp_directory : bool
    """If true, coverage_accumulation_directory will be deleted after the target is destroyed."""

    subdirectories: list[Path]
    """When non-empty, only the gcno files in these subdirectories will be considered."""

    def __init__(self, binary_directory: Path, build_directory: Path, subdirectories: list[Path] = [Path(".")], coverage_accumulation_directory: Path | None = None):
        """Initialize a GCC target.

        To use this, you must have built gcc with the --enable-coverage option.

        Parameters
        ----------
        binary_directory : Path
          directory containing the GCC binary
        build_directory : Path
          the gcc/ subdirectory of the build directory, should contain the gcno files
        subdirectories : list[Path]
          of the <build_directory>, only these subdirectories are scanned during coverage;
          the default option scans the entire compiler, which is quite slow.
          one could choose to only track the 'c' and 'c-family' subdirectories
        coverage_accumulation_directory : Path | None
          directory used to accumulate the gcda coverage files
          if set to None, a tmp directory will be created
        """
        self.binary_directory = binary_directory
        self.build_directory = build_directory
        self.subdirectories = subdirectories
        if coverage_accumulation_directory is None:
            timestamp = int((datetime.now() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
            self.coverage_accumulation_directory = Path(Path.home(), Path('tmp'), Path(f'GCCRun{timestamp}'))
            self.created_tmp_directory = True
        else:
            self.coverage_accumulation_directory = coverage_accumulation_directory
            self.created_tmp_directory = False
