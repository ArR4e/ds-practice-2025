from checkout_request import ErrorMessage

class ErrorEvent(Exception):
    message: ErrorMessage

    def __init__(self, message, *args):
        super().__init__(*args)
        self.message = message

    def __setstate__(self, __state):
        super().__setstate__(__state)

    def with_traceback(self, __tb):
        return super().with_traceback(__tb)