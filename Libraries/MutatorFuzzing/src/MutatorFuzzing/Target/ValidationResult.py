import typing
from dataclasses import dataclass

@dataclass
class ValidationResult:
    
    name: str
    """type of validation result, i.e. Timeout/Ok/WrongInput/Crash for compilers"""
    
    should_report: bool = False
    """is this a reportable result? (i.e. True if the compiler crashed)"""
    
    info: typing.Any = None
    """any info about the result"""
