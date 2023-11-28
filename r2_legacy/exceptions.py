class StructException(Exception):
    def __init__(self, event, **kwargs):
        super().__init__(event)
        self.event = event
        self.kwargs = kwargs
