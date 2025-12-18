from MutatorFuzzing.SUTInformation import SUTInformation
from dataclasses import dataclass

@dataclass
class Input:
    info: SUTInformation
    summary: str | None
