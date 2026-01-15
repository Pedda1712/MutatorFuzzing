import random

from .Input import Input
from .Base import Base

DEFAULT_START_OF_PROMPT: str = "Please mutate the input at the bottom for the following system."

class Mutate(Base):
    """Strategy for mutating previously generated input"""

    start_of_prompt: str
    
    def __init__(self, start_of_prompt: str = DEFAULT_START_OF_PROMPT):
        self.start_of_prompt = start_of_prompt

    def embed(self, _input: Input) -> str:
        prompt: str = self.start_of_prompt + "\n"
        prompt += f"The system is {_input.info.name}, a {_input.info.sut_type.value} for {_input.info.description}, supporting {_input.info.version}.\n"
        if _input.summary:
            prompt += "System: \n"
            prompt += _input.summary
        prompt += "\nInput to mutate: \n"
        prompt += random.choice(_input.previous_generations)
        return prompt

    def is_applicable(self, _input: Input) -> bool:
        return not (_input.previous_generations is None or len(_input.previous_generations) == 0)
