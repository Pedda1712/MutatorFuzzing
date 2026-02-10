import logging

from ..ModelHorde import ModelHorde
from .Summarization import Summarization
from . import Context


logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_SYSTEM_MESSAGE: str = "You are an auto-prompting model within a fuzzing system. Your task is to summarize technical documentation of compilers and libraries into smaller descriptions that will enable a fast lightweight coding model to generate fuzzing input for compilers and libraries. You must never include any spurious information that is intended for human consumption, keep your descriptions to a short and concise minimum."
DEFAULT_OLLAMA_USER_MESSAGE_START: str = "Summarize the following sources of information:\n"

class Ollama(Summarization):
    """Autoprompting implementation using local Ollama backend."""
    
    model_horde: ModelHorde
    """Pool of ollama hosts to use for summarization."""
    
    def __init__(self, sources: list[Context.Source], model_horde: ModelHorde, system_message: str = DEFAULT_OLLAMA_SYSTEM_MESSAGE, user_message_start: str = DEFAULT_OLLAMA_USER_MESSAGE_START):
        """Initialize an Ollama autoprompting backend.

        Parameters
        ----------
        sources : list[Context.Source]
          Information sources to fetch during summarization.
        model_name: str
          Ollama identifier of LLM to use for Summarization.
        system_message : str
          System message for summarization model.
        user_message_start: str
          Start of the user message that will have information appended to it.
        host : ModelHorde
          Horde of ollama hosts (LLM wrapper) used for summarization
        """
        super().__init__(sources)
        self.model_horde = model_horde
        self.system_message = system_message
        self.user_message_start = user_message_start
        
    def summarize(self, new_sources: list[Context.Source]) -> str:
        """Use the local Ollama model to summarize the information sources."""

        user_message = self.user_message_start
        
        infos = [source.fetch() for source in (self.sources + new_sources)]
        for info in infos:
            if info is None:
                continue
            user_message += self._context_source_mapper(info) 

        logger.debug(f"Built user message: {user_message}")

        return self.model_horde.request([user_message], self.system_message)[0]
        
    def _context_source_mapper(self, info: Context.Information) -> str:
        """Convert a piece of ContextInformation into a piece of prompt.

        Parameters
        ----------
        info : ContextInformation
          Piece of information to turn into a string.
        """
        if type(info) is Context.SUTInformation:
            return f"""# IMPORTANT: The following general information that concerns the SUT should be included:
- The SUT is a {info.info.sut_type.value}
- The name of the SUT is {info.info.name}
- The SUT's input is {info.info.description}
- The SUT supports version {info.info.version}
"""
        elif type(info) is Context.SoupInformation:
            return f"""# This information about the SUT was screen-scraped from {info.url}:
{info.info}
"""
        else:
            info_string = f"Information Source {type(info)} not implemented in OllamaSummarization"
            logger.error(info_string)
            raise NotImplementedError(info_string)
