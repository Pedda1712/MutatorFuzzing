from .Input import Input
from .Base import Base

DEFAULT_START_OF_PROMPT: str = "Please generate complicated input for the following system."

class New(Base):
    """Strategy for creating prompts that encourage the generation of SUT input from SUT information and task summaries."""

    start_of_prompt: str
    
    def __init__(self, start_of_prompt: str = DEFAULT_START_OF_PROMPT):
        self.start_of_prompt = start_of_prompt

    def embed(self, _input: Input) -> str:
        prompt: str = self.start_of_prompt + "\n"
        prompt += f"The system is {_input.info.name}, a {_input.info.sut_type.value} for {_input.info.description}, supporting {_input.info.version}.\n"
        if _input.summary:
            prompt += "The following summary describes the system and the focus of your task. \n"
            prompt += _input.summary
        return prompt

    def is_applicable(self, _input: Input) -> bool:
        return True
