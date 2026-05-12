import logging

from typing import TypeVar, Generic, Callable
from .StrategySampler import StrategySampler
from . import PostProcessing, PreProcessing, PromptStrategy
from ..ModelHorde import ModelHorde

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Generator(Generic[T]):
    """Generator LLM wrapper."""

    strategy_sampler: StrategySampler

    pre_processing: PreProcessing.Base

    post_processing: PostProcessing.Base[T]

    model_horde: ModelHorde

    def __init__(self, strategy_sampler: StrategySampler, pre_processing: PreProcessing.Base, post_processing: PostProcessing.Base[T], model_horde: ModelHorde):
        self.strategy_sampler = strategy_sampler
        self.pre_processing = pre_processing
        self.post_processing = post_processing
        self.model_horde = model_horde
        
    def sample(self, n: int, _input: PromptStrategy.Input, reporter = Callable[[], None]) -> tuple[list[T], list[str], list[str]]:
        """Sample some SUT input from the generator LLM.

        Parameter
        ---------
        n : int
          how many inputs to sample
        _input : PromptStrategyInput
          input information for the generator LLM
        reporter : Callable[[], None
          function that gets called after each generation is finished

        Return
        ------
        post_processed_outputs : list[T]
          List of SUT inputs of length n. 
        prompts : list[str]
          Natural language prompts used to generate each output
        raw_outputs : list[str]
          raw llm outputs (without post-processing applied)
        """

        prompts : list[str] = self.strategy_sampler.sample(n, _input)

        outputs: list[str] = self.model_horde.request(prompts, reporter = reporter)
                
        post_processed_outputs : list[T] = [self.post_processing.process(output) for output in outputs]

        return post_processed_outputs, prompts, outputs
