from . import Context

class Summarization:
    """Base Summarization Class."""
    
    sources: list[Context.Source]
    """Information pieces that are integrated during summarization every time."""
    
    def __init__(self, sources: list[Context.Source]):
        self.sources = sources
        
    def summarize(self, new_sources: list[Context.Source]) -> str:
        """Summarize SUT information from the sources provided in the constructor with additional sources.

        Parameters:
        -----------
        new_sources: list[Context.Source]
          These and the constructor sources are used for summarization.
          Used for refocusing summarization: The constructor sources are used always, while these may change during fuzzing.
        """
        raise NotImplementedError("Base Summarization Engine does not provide summarization!")
