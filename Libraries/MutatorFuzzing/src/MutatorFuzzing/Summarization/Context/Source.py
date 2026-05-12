"""
ContextSources are sources of information that get summarized.
"""

class Information:
    """An abstract piece of current information about SUT."""
    def __init__(self):
        pass
    def format(self) -> str:
        """Format this information as string, if possible.

        Returns empty string if information is not formattable.
        """
        return ""
        

class Source:
    cached: Information | None = None
    """An abstract source of information, either about the SUT or current progress of fuzzing."""
    def __init__(self):
        self.cached = None
        pass
    def fetch(self) -> Information | None:
        """Fetch the current information state from this source."""
        raise NotImplementedError("Base Context Source does not provide any information!")
    def get_semantic_name(self) -> str:
        """Name of this source.

        Used for displaying in reporting server.
        """
        raise NotImplementedError("Base Context Source does not provide any information!")
    def get_cached_fetch(self) -> Information:
        if self.cached is None:
            self.cached = self.fetch()
        return self.cached

