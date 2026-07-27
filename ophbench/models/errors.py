class AdapterNotImplementedError(LookupError):
    pass


class AdapterEnvironmentError(RuntimeError):
    """Raised when optional runtime dependencies are unavailable."""


class CheckpointResolutionError(FileNotFoundError):
    """Raised when an explicit local checkpoint cannot be resolved."""


class InvalidCheckpointError(ValueError):
    """Raised when a checkpoint does not match the expected RETFound format."""
