import random
import string


def create_random_id() -> str:
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(20)
    )
