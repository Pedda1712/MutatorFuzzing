class Base[T]:

    def __init__(self):
        pass

    def process(self, output: str) -> T:
        """Process LLM output into system input.

        For a C Fuzzer, extract the source code portion from LLM output.
        For something like a DLL fuzzer, you would extract function inputs.

        Parameter
        ---------
        output : str
          The raw output from the LLM.

        Return
        ------
        The extracted information from the SUT.
        """
        raise NotImplementedError("Base output post processing not implemented.")
