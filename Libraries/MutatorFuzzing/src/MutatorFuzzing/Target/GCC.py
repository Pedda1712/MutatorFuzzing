import subprocess, os
from tempfile import NamedTemporaryFile
from pathlib import Path
from datetime import datetime

from .FuzzingTarget import FuzzingTarget
from .ValidationResult import ValidationResult

class GCC(FuzzingTarget[str]):
    """Provides a local GCC build as a target."""

    build_directory: Path
    """Directory containing GCCs gcno coverage infofiles."""

    binary_directory: Path
    """Directory containing the GCC binary."""

    coverage_accumulation_directory: Path
    """Directory where gcda files will be directed to."""

    subdirectories: list[Path]
    """When non-empty, only the gcno files in these subdirectories will be considered."""

    gcov_prefix_strip: int
    """Value to use for the GCOV_PREFIX_STRIP env variable, calculated from the number of elements in build_directory"""

    def __init__(self, binary_directory: Path, build_directory: Path, subdirectories: list[Path] = [Path(".")], coverage_accumulation_directory: Path | None = None):
        """Initialize a GCC fuzzing target.

	Uses gcc's own gcov framework to track coverage of itself.

        To use this, you must have built gcc itself with the --enable-coverage option.
	The parameters require you to specify locations of (sub)directories of the build directory.

        Also you must have the lcov utility installed on your system.

        Parameters
        ----------
        binary_directory : Path
          directory containing the GCC binary
        build_directory : Path
          the gcc/ subdirectory of the build directory, should contain the gcno files
        subdirectories : list[Path]
          of the <build_directory>, only these subdirectories are scanned during coverage;
          The default option scans the entire compiler, which is quite slow.
          One could choose to only track the 'c' and 'c-family' subdirectories, which is faster
          but most likely only tracks compiler frontend coverage.
        coverage_accumulation_directory : Path
          directory used to accumulate the gcda coverage files, you may use a temporary directory here
        """
        self.binary_directory = binary_directory
        self.build_directory = build_directory
        self.subdirectories = subdirectories
        self.coverage_accumulation_directory = coverage_accumulation_directory
        self.gcov_prefix_strip = len(build_directory.parents)

    def validate(self, input: str) -> ValidationResult:
        with NamedTemporaryFile('w', suffix='.c', delete_on_close = False) as input_file, NamedTemporaryFile(delete_on_close = False) as output_file:
            input_file.write(input)
            input_file.close()
            output_file.close()
            environment_variables = os.environ.copy()
            environment_variables['GCOV_PREFIX_STRIP'] = str(self.gcov_prefix_strip)
            environment_variables['GCOV_PREFIX'] = str(self.coverage_accumulation_directory)
            command = [
                Path(self.binary_directory, 'gcc'),
                '-c',
                input_file.name,
                '-o',
                output_file.name
            ];
            try:
                completed_process = subprocess.run(command, env = environment_variables, timeout = 5, capture_output = True)
                if completed_process.returncode == 0:
                    return ValidationResult('Ok', False, None)
                elif completed_process.returncode == 1:
                    return ValidationResult('WrongInput', False, None)
                else: # non 0 or 1 exit-code -> compiler crash
                    return ValidationResult('Crash', True, {
                        'stdout': completed_process.stdout,
                        'stderr': completed_process.stderr
                    })
            except subprocess.TimeoutExpired:
                return ValidationResult('Timeout', True, None)
    
    def get_coverage(self) -> float:
        raise NotImplementedError("TODO")

    def clear_coverage(self):
        raise NotImplementedError("TODO")


