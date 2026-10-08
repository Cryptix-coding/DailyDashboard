from config import Config
from typing import List, Dict

def get_emergency_contacts() -> List[Dict[str, str]]:
    """Return the list of emergency contacts defined in the environment variables."""
    return Config.EMERGENCY_CONTACTS