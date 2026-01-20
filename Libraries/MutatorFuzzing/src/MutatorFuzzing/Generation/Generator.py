import ollama
import logging

from typing import TypeVar, Generic
from .StrategySampler import StrategySampler
from . import PostProcessing, PreProcessing, PromptStrategy

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Generator(Generic[T]):
    """Generator LLM wrapper."""

    strategy_sampler: StrategySampler

    pre_processing: PreProcessing.Base

    post_processing: PostProcessing.Base[T]

    model_name: str
    """Ollama string of the model to use."""

    timeout: int
    """Timmeout to use for the individual ollama requests."""

    def __init__(self, strategy_sampler: StrategySampler, pre_processing: PreProcessing.Base, post_processing: PostProcessing.Base[T], timeout = 5, model_name="qwen2.5-coder:1.5b"):
        self.strategy_sampler = strategy_sampler
        self.pre_processing = pre_processing
        self.post_processing = post_processing
        self.model_name = model_name
        self.timeout = timeout

    def _sample_one(self, prompt: str) -> str | None:
        try:
            return str(ollama.Client(timeout = self.timeout).chat(
                model = self.model_name,
                messages = [
                    {
                        "role": "user",
                        "content": self.pre_processing.process(prompt)
                    }
                ]
            ).message.content)
        except Exception as e:
            logger.warn(f"Ollama returned exception {e}, returning None ...")
            return None

    def sample(self, n: int, _input: PromptStrategy.Input) -> tuple[list[T], list[str], list[str]]:
        """Sample some SUT input from the generator LLM.

        Parameter
        ---------
        n : int
          how many inputs to sample
        _input : PromptStrategyInput
          input information for the generator LLM

        Return
        ------
        post_processed_outputs : list[T]
          List of SUT inputs of length n. 
        prompts : list[str]
          Natural language prompts used to generate each output
        raw_outputs : list[str]
          raw llm outputs (without post-processing applied)
        """

        prompts : list[str] = []
        outputs : list[str] = []
        while len(outputs) < n:
            prompt = self.strategy_sampler.sample(1, _input)
            output = self._sample_one(prompt[0])
            if output is not None: # request timed out, or other issue?
                prompts.append(prompt[0])
                outputs.append(output)
                
        post_processed_outputs : list[T] = [self.post_processing.process(output) for output in outputs]

        return post_processed_outputs, prompts, outputs
