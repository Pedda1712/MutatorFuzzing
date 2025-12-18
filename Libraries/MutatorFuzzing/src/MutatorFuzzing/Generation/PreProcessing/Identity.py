from .Base import Base

class Identity(Base):

    def __init__(self):
        pass

    def process(self, prompt: str) -> str:
        return prompt
