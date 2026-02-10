class PlateauCriterion:
    width : int
    line_delta: int

    coverage_history: list[int]
    
    def __init__(self, width: int, line_delta: int):
        """Initialize a criterion for plateau detection.

        If over <width> updates, there is less than <line_delta> of lines
        in increased coverage, a plateau will be reported.
        """
        self.width = width
        self.line_delta = line_delta
        self.coverage_history = []

    def step(self, absolute_coverage: int):
        """Update the plateau detector and return criterion result.

        Parameters:
        -----------
        absolute_coverage: int
          absolute coverage from the last target validation epoch

        Returns true if a plateau is detected, false otherwise.
        """
        self.coverage_history.append(absolute_coverage)
        while len(self.coverage_history) > self.width:
            self.coverage_history.pop(0)
        current_line_delta = absolute_coverage - self.coverage_history[0]
        if len(self.coverage_history) == self.width:
            return current_line_delta < self.line_delta
        return False

    def clear_history(self):
        self.coverage_history = []
