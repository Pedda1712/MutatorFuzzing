import logging
import ollama
from .Summarization import Summarization
from .Context import ContextSource, ContextInformation, SUTContextInformation, SoupContextInformation

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_SYSTEM_MESSAGE: str = "You are an auto-prompting model within a fuzzing system. Your task is to summarize technical documentation of compilers and libraries into small descriptions that will enable a fast lightweight coding model to generate fuzzing input for compilers and libraries. You must never include any spurious information that is intended for human consumption, keep your descriptions to a short and concise minimum. Focus your instructions on SUT crashes."
DEFAULT_OLLAMA_USER_MESSAGE_START: str = "Summarize the following sources of information:\n"

class OllamaSummarization(Summarization):
    """Autoprompting implementation using local Ollama backend."""
    
    model_name: str
    """Ollama model name to use in the backend."""
    
    def __init__(self, sources: list[ContextSource], model_name: str ="gemma3", system_message: str = DEFAULT_OLLAMA_SYSTEM_MESSAGE, user_message: str = DEFAULT_OLLAMA_USER_MESSAGE_START):
        """Initialize an Ollama autoprompting backend.

        Parameters
        ----------
        sources : list[ContextSource]
          Information sources to fetch during summarization.
        model_name: str
          Ollama identifier of LLM to use for Summarization.
        system_message : str
          System message for summarization model.
        user_message: str
          Start of the user message that will have information appended to it.
        """
        super().__init__(sources)
        self.model_name = model_name
        self.system_message = system_message
        self.user_message = user_message
        
    def summarize(self) -> str:
        """Use the local Ollama model to summarize the information sources."""
        
        logger.info(f"Begin OllamaSummarization:{self.model_name} ...")

        infos = [source.fetch() for source in self.sources]
        for info in infos:
            if info is None:
                continue
            user_message += self._context_source_mapper(info) 

        logger.info(f"Built user message: {user_message}")

        try:
            return ollama.chat(
                model = self.model_name,
                messages = [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            ).message.content
        except Exception as e:
            logger.warn(f"Ollama returned exception {e}, using empty prompt ...")
            return ""
        
    def _context_source_mapper(self, info: ContextInformation) -> str:
        """Convert a piece of ContextInformation into a piece of prompt.

        Parameters
        ----------
        info : ContextInformation
          Piece of information to turn into a string.
        """
        if type(info) is SUTContextInformation:
            return f"""# IMPORTANT: The following general information that concerns the SUT should be included:
- The SUT is a {info.sut_type.value}
- The name of the SUT is {info.name}
- The SUT's input is {info.description}
- The SUT supports version {info.version}
"""
        elif type(info) is SoupContextInformation:
            return f"""# This information about the SUT was screen-scraped from {info.url}:
{info.info}
"""
        else:
            info_string = f"Information Source {type(info)} not implemented in OllamaSummarization"
            logger.error(info_string)
            raise NotImplementedError(info_string)
