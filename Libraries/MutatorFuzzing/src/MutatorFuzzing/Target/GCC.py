import subprocess
import asyncio
import os

from tempfile import NamedTemporaryFile
from pathlib import Path

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

    binary_and_suffix : tuple[str, str]
    """what gcc binary to use and what file suffix to use"""

    flags: list[str]
    """List of flags, i.e. version specifiers"""

    def __init__(self, binary_directory: Path, build_directory: Path, coverage_accumulation_directory: Path, binary_and_suffix: tuple[str, str] = ("gcc", "c"), flags: list[str] = [], subdirectories: list[Path] = [Path(".")]):
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
        binary_and_suffix : tuple[str, str]
          choose what specific gcc binary to use;
          e.g. if you want to use c++, choose ("g++", ".cpp")
        coverage_accumulation_directory : Path
          directory used to accumulate the gcda coverage files, you may use a temporary directory here
        """
        self.binary_directory = binary_directory
        self.build_directory = build_directory
        self.subdirectories = subdirectories
        self.coverage_accumulation_directory = coverage_accumulation_directory
        self.gcov_prefix_strip = len(build_directory.parents)
        self.binary_and_suffix = binary_and_suffix
        self.flags = flags

    async def run(self, cmd, env):
        # helper to asynchronously call a subprocess
        proc = await asyncio.create_subprocess_shell(
            cmd,
            env = env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        
        stdout, stderr = await proc.communicate()
        stdout_s = ''
        stderr_s = ''
        if stdout:
            stdout_s = stdout.decode()
        if stderr:
            stderr_s = stderr.decode()

        return proc.returncode, stdout_s, stderr_s

    async def _validate(self, input: str) -> ValidationResult:
        with NamedTemporaryFile('w', suffix=self.binary_and_suffix[1], delete_on_close = False) as input_file, NamedTemporaryFile(delete_on_close = False) as output_file:
            input_file.write(input)
            input_file.close()
            output_file.close()
            environment_variables = os.environ.copy()
            environment_variables['GCOV_PREFIX_STRIP'] = str(self.gcov_prefix_strip)
            environment_variables['GCOV_PREFIX'] = str(self.coverage_accumulation_directory)
            command = [
                Path(self.binary_directory, self.binary_and_suffix[0]),
                Path('-c'),
                Path(input_file.name),
                Path('-o'),
                Path(output_file.name)
            ]
            for flag in self.flags:
                command.append(flag)
            command = [str(c) for c in command]
            try:
                returncode, stdout, stderr = await asyncio.wait_for(self.run(' '.join(command), environment_variables), timeout = 5)
                if returncode == 0:
                    return ValidationResult('Ok', False, None)
                elif returncode == 1:
                    return ValidationResult('WrongInput', False, None)
                else: # non 0 or 1 exit-code -> compiler crash
                    return ValidationResult('Crash', True, {
                        'stdout': stdout,
                        'stderr': stderr
                    })
            except TimeoutError:
                return ValidationResult('Timeout', True, None)

    def validate(self, input: str) -> ValidationResult:
        return asyncio.run(self._validate(input))

    def validate_batch(self, inputs: list[str]) -> list[ValidationResult]:
        pending_validations = [self._validate(input) for input in inputs]
        async def wait_for_requests():
            return await asyncio.gather(*pending_validations)
        return asyncio.run(wait_for_requests())
            
    def get_coverage(self) -> tuple[float, int]:
        scan_gcda_directories = [Path(self.coverage_accumulation_directory, p) for p in self.subdirectories]
        scan_gcno_directories = [Path(self.build_directory, p) for p in self.subdirectories]

        with NamedTemporaryFile(delete_on_close = False) as lcov_output_file:
            lcov_output_file.close()
            command = [
                'lcov',
                '--capture',
                '--output-file',
                f'{lcov_output_file.name}',
                '--gcov-tool',
                'gcov',
                '--ignore-errors',
                'inconsistent,inconsistent'
            ]
            for directory in scan_gcda_directories:
                command.append('--directory')
                command.append(f'{directory}')
            for directory in scan_gcno_directories:
                command.append('--build-directory')
                command.append(f'{directory}')

            completed_process = subprocess.run(command, env = os.environ,  capture_output = True, encoding = 'utf-8')

            if completed_process.returncode != 0:
                raise RuntimeError('lcov failed: ' + completed_process.stdout + completed_process.stderr)
            
            line_coverage = None
            absolute_line_coverage = None
            for line in completed_process.stdout.splitlines():
                if line.strip().startswith('lines'):
                    line_elements = line.split('(')[1].split(' ')
                    absolute_line_coverage = int(line_elements[0])
                    line_coverage = int(line_elements[0]) / int(line_elements[2])

            if line_coverage is None:
                raise RuntimeError('lcov output did not include coverage information: ' + completed_process.stdout)
                    
            return line_coverage, absolute_line_coverage
    
    def clear_coverage(self):
        command = ['lcov', '-z', '-d', self.coverage_accumulation_directory]
        completed_process = subprocess.run(command, env = os.environ, capture_output = True, encoding = 'utf-8')
        if completed_process.returncode != 0:
            raise RuntimeError('clearing of coverage failed with message ' + completed_process.stdout + completed_process.stderr)


