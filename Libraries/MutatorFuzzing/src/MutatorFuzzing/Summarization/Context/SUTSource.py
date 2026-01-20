from ...SUTInformation import SUTInformation as _SUTInformation
from .Source import Information, Source

"""
This ContextSource describes the SUT to the auto-prompting model.
"""

class SUTInformation(Information):
    """A piece of information statically describing a SUT for fuzzing."""

    info: _SUTInformation

    def __init__(self, info: _SUTInformation):
        """Initialize static SUT information.

        Parameters
        ----------
        info: MutatorFuzzing.SUTInformation
        """
        self.info = info

class SUTSource(Source):
    """A source of static SUT information."""
    
    info: SUTInformation
    """The piece of information to return on fetching."""
    
    def __init__(self, info: SUTInformation):
        """Initialize a source of static SUT information.

        Parameters
        ----------
        info : SUTContextInformation
          The piece of static context information to return.
        """
        self.info = info
        
    def fetch(self) -> SUTInformation | None:
        return self.info



