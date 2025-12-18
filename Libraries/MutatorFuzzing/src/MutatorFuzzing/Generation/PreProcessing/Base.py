class Base:
    def __init__(self):
        pass

    def process(self, prompt: str) -> str:
        """Process a prompt before feeding it to the generation model.

        An Example PreProcessing step would be embedding the prompt in a
        source code comment of the target language before feeding it to a
        model like starcoder.

        Parameter
        ---------
        prompt : str
          Prompt obtained from PromptStrategy or StrategySampler

        Return
        ------
        The embedded prompt.
        """
        raise NotImplementedError("base prompt pre processing not implemented")
