from random import random
from . import PromptStrategy

class StrategySampler:
    """From some given prompt input, create a fixed number of proto-prompts."""

    strategies: list[PromptStrategy.Base]
    """Collection of strategies to be sampled from"""

    weights: list[float]
    """Cumulative probabilities of sampling a given strategy"""

    def __init__(self, strategies: list[PromptStrategy.Base], weights: list[float] = []):
        """Initialize a StrategySampler.

        Parameter
        ---------
        strategies : list[BasePromptStrategy]
          strategies that will be sampled from to create prompts
        """
        self.strategies = strategies

        if len(self.strategies) == 0:
            raise RuntimeError("Atleast one sampling strategy is needed.")
        
        self.weights = weights
        if len(self.weights) == 0:
            self.weights = [1/len(self.strategies)] * len(self.strategies)
        eta = sum(self.weights)
        self.weights = [w / eta for w in self.weights]


    def sample(self, n : int, _input: PromptStrategy.Input) -> list[str]:
        """Sample some natural language prompts from input.

        Example: If the strategies of this sampler include new generation
        and mutation of old input, then a call to this function will
        retrieve some prompts with instructions for the generation of
        new input and some prompts with instructions to mutate some old
        input.

        Parameters
        ----------
        n : int
          how many prompts to sample
        _input: PromptStrategyInput
          input to pass to the chosen strategies to create the prompts


        Return
        ------
        A list of natural language prompt prototypes.
        """
        applicable = [strategy.is_applicable(_input) for strategy in self.strategies]
        strategies = [strategy for index, strategy in enumerate(self.strategies) if applicable[index]]
        weights = [weight for index, weight in enumerate(self.weights) if applicable[index]]

        eta = sum(weights)
        weights = [w/eta for w in weights]

        if len(strategies) == 0:
            raise RuntimeError("No strategies are applicable given the current input.")
        
        cumsum = 0
        for index, weight in enumerate(weights):
            weights[index] += cumsum
            cumsum += weight

        def _sample_strategy() -> PromptStrategy.Base:
            value = random()
            i = 0
            while True:
                if value <= weights[i]:
                    break
                i+=1
            return strategies[i]

        return [_sample_strategy().embed(_input) for _ in range(n)]
