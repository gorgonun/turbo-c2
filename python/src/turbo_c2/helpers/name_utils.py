import uuid


class NameUtils:
    @classmethod
    def get_anonymous_name(cls, prefix: str) -> str:
        if not prefix:
            return uuid.uuid4().hex

        return generate_resource_id(prefix)
    

def generate_resource_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"
