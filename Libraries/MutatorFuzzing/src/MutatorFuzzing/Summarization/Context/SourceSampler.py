import random
from .Source import Source

class Urn:
    """A collection of context sources, to be sampled from."""
    
    content: list[Source]

    def __init__(self, content: list[Source]):
        self.content = content

    def sample(self, n: int) -> list[Source]:
        """Sample n sources and return them in a list."""
        return random.sample(self.content, n)

class SourceSampler:
    """Randomly chooses context sources for summarization."""

    urns: list[Urn]

    def __init__(self, urns: list[Urn]):
        self.urns = urns

    def sample(self, k: int) -> list[Source]:
        """Sample k sources from each urn and returns them in a list."""
        return sum([urn.sample(k) for urn in self.urns], [])
