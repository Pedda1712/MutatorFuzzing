import logging
import os
from pathlib import Path

from .Source import Information, Source
from .SourceSampler import Urn

logger = logging.getLogger(__name__)

class FileInformation(Information):
    """A static piece of SUT information, fetched from disk."""

    info: str
    """Information content"""

    def __init__(self, info: str):
        """Initialize a piece of text from a file.

        Parameters
        ----------
        info : str
          content of a file from disk
        """
        self.info = info
class FileSource(Source):
    """An information source that abstracts a text file."""

    path: Path
    """Path to file on disk."""

    def __init__(self, path: Path):
        """Initialize a FileSource.

        Parameters
        ----------
        path : Path
          path to file
        """
        self.path = path

    def fetch(self) -> FileInformation | None:
        with open(self.path, 'r') as f:
            return FileInformation(f.read())
        logger.warn(f'did not read file {self.path}')
        return None

class FolderUrn(Urn):
    """Turns a folder into a collection or source documents."""

    def __init__(self, path: Path, suffix: str):
        """Initialize a FolderUrn.

        Parameters
        ----------
        path : Path
          every file within the folder pointed to by this path
          will be added as a source to the urn.
        suffix : str
          only the files with this suffix will be considered
        """
        super().__init__([])
        for f in os.listdir(path):
            if f.endswith(f'.{suffix}'):
                self.content.append(FileSource(Path(path, f)))
