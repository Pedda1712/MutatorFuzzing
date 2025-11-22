from .Context import ContextSource

class Summarization:
    """Base Summarization Class."""
    
    sources: list[ContextSource]
    """ContextSources are information pieces that are integrated during summarization."""
    
    def __init__(self, sources: list[ContextSource]):
        self.sources = sources
        
    def summarize(self) -> str:
        """Summarize SUT information from the sources provided in the constructor."""
        raise NotImplementedError("Base Summarization Engine does not provide summarization!")
