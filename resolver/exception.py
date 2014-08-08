class NotFoundException(Exception):
    def __init__(self):
        self.message = "Not Found"
