from typing import Dict
from config import Config

def get_emergency_contact() -> Dict[str, str]:
    return {
        "name": Config.EMERGENCY_CONTACT_NAME,
        "number": Config.EMERGENCY_CONTACT_NUMBER
    }