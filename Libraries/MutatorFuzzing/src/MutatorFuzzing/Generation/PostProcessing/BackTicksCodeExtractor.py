from .Base import Base

class BackTicksCodeExtractor(Base[str]):

    def __init__(self):
        pass

    def process(self, output: str) -> str:
        """Extract the first backticks-enclosed string from the output.

        Some code generation models generate not only code,
        but also explanations which will make compilation fail.
        This simple post-processing step will look for the first two
        lines starting with backticks and only return the enclosed part.

        Suitable for example for Qwen-Coder models, which like to output
        in backticks-enclosed blocks.

        Parameter
        ---------
        output : str
          Raw LLM output, e.g. from a Qwen-Coder model.

        Return
        ------
        The first backtick-enclosed string.
        If no lines starting with backticks are found, the complete
        raw llm output is returned.
        """

        lines = output.splitlines()
        enclosed_lines = []

        saw_backticks = False
        for line in lines:
            if line.lstrip().startswith('```'):
                if saw_backticks:
                    break
                else:
                    saw_backticks = True
                    continue
            if saw_backticks:
                enclosed_lines.append(line)

        if len(enclosed_lines) == 0:
            return output
            
        return '\n'.join(enclosed_lines)
