import ollama
import logging

from .StrategySampler import StrategySampler
from . import PostProcessing, PreProcessing, PromptStrategy

logger = logging.getLogger(__name__)

class Generator[T]:
    """Generator LLM wrapper."""

    strategy_sampler: StrategySampler

    pre_processing: PreProcessing.Base

    post_processing: PostProcessing.Base[T]

    model_name: str
    """Ollama string of the model to use."""

    def __init__(self, strategy_sampler: StrategySampler, pre_processing: PreProcessing.Base, post_processing: PostProcessing.Base, model_name="qwen2.5-coder:1.5b"):
        self.strategy_sampler = strategy_sampler
        self.pre_processing = pre_processing
        self.post_processing = post_processing
        self.model_name = model_name

    def _sample_one(self, prompt: str) -> str:
        try:
            return str(ollama.chat(
                model = self.model_name,
                messages = [
                    {
                        "role": "user",
                        "content": self.pre_processing.process(prompt)
                    }
                ]
            ).message.content)
        except Exception as e:
            logger.warn(f"Ollama returned exception {e}, using empty output ...")
            return ""

    def sample(self, n: int, _input: PromptStrategy.Input) -> list[T]:
        """Sample some SUT input from the generator LLM.

        Parameter
        ---------
        n : int
          how many inputs to sample
        _input : PromptStrategyInput
          input information for the generator LLM

        Return
        ------
        List of SUT inputs.
        """

        prompts = self.strategy_sampler.sample(n, _input)

        outputs = [self._sample_one(p) for p in prompts]

        post_processed_outputs = [self.post_processing.process(output) for output in outputs]

        return post_processed_outputs
