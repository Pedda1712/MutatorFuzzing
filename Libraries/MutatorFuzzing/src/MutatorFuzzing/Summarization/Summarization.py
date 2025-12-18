from . import Context

class Summarization:
    """Base Summarization Class."""
    
    sources: list[Context.Source]
    """Information pieces that are integrated during summarization."""
    
    def __init__(self, sources: list[Context.Source]):
        self.sources = sources
        
    def summarize(self) -> str:
        """Summarize SUT information from the sources provided in the constructor."""
        raise NotImplementedError("Base Summarization Engine does not provide summarization!")
