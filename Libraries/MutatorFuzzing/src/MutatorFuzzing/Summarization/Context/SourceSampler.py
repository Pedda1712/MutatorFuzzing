import random
from .Source import Source

class Urn:
    """A collection of context sources, to be sampled from."""
    
    content: list[Source]
    semantic_name: str

    def __init__(self, content: list[Source], semantic_name: str):
        """Initialize an Urn.

        This object is used to randomly sample documentation sources
        for summarization.

        Parameters
        ----------
        content : list[Source]
          List of content to sample from.
        semantic_name : str
          Some name describing the commonality of the documents
          in the Urn. Used for display purposes.
        """
        self.content = content
        self.semantic_name = semantic_name

    def sample(self, n: int) -> list[Source]:
        """Sample n sources and return them in a list."""
        return random.sample(self.content, n)

    def get_sources(self) -> list[Source]:
        """Return all information sources in the Urn."""
        return self.content

    def get_semantic_name(self) -> str:
        return self.semantic_name

class SourceSampler:
    """Randomly chooses context sources for summarization."""

    urns: list[Urn]

    def __init__(self, urns: list[Urn]):
        self.urns = urns

    def sample(self, k: int) -> list[Source]:
        """Sample k sources from each urn and returns them in a list."""
        return sum([urn.sample(k) for urn in self.urns], [])
