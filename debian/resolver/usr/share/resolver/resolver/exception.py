class NotFoundException(Exception):
    def __init__(self):
        self.message = "Not Found"

class EntityPIDExistsException(Exception):
    """This exception is raised if an entity's PID is not unique"""
    def __init__(self):
        self.message = "Duplicate PID"

class EntityCollisionException(Exception):
    """This exception is raise if two distinct PIDs are mapped onto the same
       value. Example: an entity with PID 12/3 is added to the database under
       the cleaned up PID 123. Afterwards, we try to add a new entity with PID
       1/23, which is also cleaned up to PID 123 ==> collision."""
    def __init__(self, original_id):
        self.message = "PID collision"
        self.original_id = original_id
