import threading


class NonBlockingCall(threading.Thread):
    # TODO: should we block a second call if we are not done with the first one
    def __init__(self, callback):
        super().__init__(target=callback)
        self.start()
