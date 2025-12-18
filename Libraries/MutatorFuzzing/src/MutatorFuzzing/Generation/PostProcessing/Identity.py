from .Base import Base

class Identity(Base[str]):

    def __init__(self):
        pass

    def process(self, output: str) -> str:
        return output
