from .Input import Input

class Base:
    """Base Class for all Prompt Strategies."""

    def __init__(self):
        pass

    def embed(self, _input: Input) -> str:
        """Embed some input (i.e. task summary, SUT information) into a prompt for input generation.

        Parameters
        ----------
        _input: Input
          The information to be wrapped in a natural language prompt.

        Return
        ------
        A natural language prompt which contains the information.
        """
        raise NotImplementedError("Base PromptStrategy does not implement prompt generation.")

    def is_applicable(self, _input: Input) -> bool:
        """Determine if the prompt strategy is applicable given the input.

        Some strategies (like semantically changing a previous generation) rely
        on the availability of information (e.g. the previous generation), and
        would fail if attempted otherwise.

        Parameters
        ----------
        _input: Input
          The input for which to check if this strategy is applicable on

        Return
        ------
        True, if applicable (then one can proceed with embedding)
        False, if information is missing for this prompt strategy
        """
        raise NotImplementedError("Base PromptStrategy is not intended to be used by itself, use one of the derived strategies.")
    
