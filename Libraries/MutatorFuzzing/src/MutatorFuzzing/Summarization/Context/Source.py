"""
ContextSources are sources of information that get summarized.
"""

class Information:
    """An abstract piece of current information about SUT."""
    def __init__(self):
        pass

class Source:
    """An abstract source of information, either about the SUT or current progress of fuzzing."""
    def __init__(self):
        pass
    def fetch(self) -> Information | None:
        """Fetch the current information state from this source."""
        raise NotImplementedError("Base Context Source does not provide any information!")
