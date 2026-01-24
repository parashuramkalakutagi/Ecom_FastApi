import uuid
import random

def generate_random_mock_id():
    rand = lambda : uuid.uuid4().hex[:8].upper()
    return {
        f"MOCK_OD_{rand()}",
        f"MOCK_PY_{rand()}",
        f"MOCK_SI_{rand()}",
    }