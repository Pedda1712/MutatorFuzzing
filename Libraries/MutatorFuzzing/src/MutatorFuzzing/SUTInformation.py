from enum import Enum

class SUTInformation:
    """A piece of information describing a SUT for fuzzing."""
    
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
        """Initialize SUT information.

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
