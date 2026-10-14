class OperationError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
