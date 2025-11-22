from enum import Enum, auto
from .ContextSource import ContextInformation, ContextSource

"""
This ContextSource  describes the SUT to the auto-prompting model.
"""

class SUTContextInformation(ContextInformation):
    """A piece of information statically describing a SUT for fuzzing."""
    
    class SUT(Enum):
        """Type of SUT, i.e. 'Compiler' or 'Library'"""
        Compiler = "Compiler"

    sut_type: SUT
    """Basic SUT type, i.e. is it a compiler or a library?"""
    
    name: str
    """Name of the SUT, e.g. GCC, G++, clang."""
    
    description: str
    """Short description, e.g. 'the C Programming Language'."""
    
    version: str
    """SUT version, e.g. 'C11'."""

    def __init__(self, sut_type: SUT, name: str, description: str, version: str):
        """Initialize static SUT information.

        Parameters
        ----------
        sut_type: SUT
          Of what fundamental type is the SUT? (e.g. Compiler)
        name: str
          What name identifies the SUT? (e.g. 'GCC')
        description: str
          What input does the SUT process? (e.g. 'the C Programming Language')
        version: str
          If there are input versions, then which version? (e.g. 'C11')
        """
        self.sut_type = sut_type
        self.name = name
        self.description = description
        self.version = version

class SUTContextSource(ContextSource):
    """A source of static SUT information."""
    
    info: SUTContextInformation
    """The piece of information to return on fetching."""
    
    def __init__(self, info: SUTContextInformation):
        """Initialize a source of static SUT information.

        Parameters
        ----------
        info : SUTContextInformation
          The piece of static context information to return.
        """
        self.info = info
        
    def fetch(self) -> SUTContextInformation | None:
        return self.info



