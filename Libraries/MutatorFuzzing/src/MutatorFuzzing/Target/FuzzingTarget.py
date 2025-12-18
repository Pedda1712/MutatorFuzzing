from .ValidationResult import ValidationResult

class FuzzingTarget[T]:
    """Base class for fuzzing targets."""
    
    def __init__(self):
        pass

    def validate(self, input: T) -> ValidationResult:
        """Validate some target input.

        Parameters:
        -----------
        input : T
          some input for the fuzzing target
        (e.g. a string for a compiler)

        Returns:
        --------
        ValidationResult with target-specific name and information
        """
        raise NotImplementedError("base target does not implement input validation")

    def get_coverage(self) -> float:
        """Obtain target coverage information.

        Returns the fraction was covered by input processed
        (that was passed to validate()) since the last call
        to clear_coverage().

        Returns
        -------
        Float in the range [0; 1], that denotes the fraction
        of target code covered.
        """
        raise NotImplementedError("base target does not implement coverage tracking")

    def clear_coverage(self):
        """Reset coverage tracking.
        """
        raise NotImplementedError("base target does not implement coverage tracking")
