import json
import subprocess
import threading
import time
import datetime
from typing import Any, Optional
from config import Config

# Holds the currently active message
_active_message: Optional[dict[str, Any]] = None


def _send_read_receipt(sender_number: str, timestamp: int) -> None:
    """Send a read receipt back to the sender."""
    if not sender_number or not timestamp:
        return
    try:
        subprocess.run(
            [
                "signal-cli",
                "-a", Config.SIGNAL_PHONE_NUMBER,
                "sendReceipt",
                "--read",
                "-t", str(timestamp),
                sender_number
            ],
            capture_output=True,
            check=False
        )
    except Exception as error:
        print(f"[SignalService] Error sending read receipt: {error}")


def _listen_loop() -> None:
    """Background loop polling signal-cli for new messages."""
    global _active_message
    print("[SignalService] Background listener started.")
    
    while True:
        try:
            result = subprocess.run(
                ["signal-cli", "-a", Config.SIGNAL_PHONE_NUMBER, "receive", "--json"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                
                data = json.loads(line)
                envelope = data.get("envelope", {})
                data_message = envelope.get("dataMessage", {})
                
                if not data_message:
                    continue
                
                # Process only messages from the designated family group
                if data_message.get("groupInfo", {}).get("groupId") == Config.SIGNAL_GROUP_ID:
                    msg_text = data_message.get("message", "")
                    sender_name = envelope.get("sourceName") or "Familie"
                    sender_number = envelope.get("sourceNumber")
                    msg_timestamp = data_message.get("timestamp")
                    
                    if msg_text:
                        # Command to hide/clear the active message (Strictly "Löschen")
                        if msg_text.strip().lower() == "löschen":
                            _active_message = None
                            print("[SignalService] Message cleared via command.")
                        else:
                            _active_message = {
                                "sender": sender_name,
                                "text": msg_text,
                                "timestamp_display": datetime.datetime.now().strftime("%H:%M")
                            }
                            print(f"[SignalService] New message received from {sender_name}")
                            
                            # Trigger read receipt so the family knows it was processed
                            if sender_number and msg_timestamp:
                                _send_read_receipt(sender_number, msg_timestamp)
                                
        except Exception as error:
            print(f"[SignalService] Error fetching messages: {error}")
            
        # Poll every 5 seconds
        time.sleep(5)


def start_signal_listener() -> None:
    """Start the background thread for receiving Signal messages."""
    if not Config.SIGNAL_PHONE_NUMBER or not Config.SIGNAL_GROUP_ID:
        print("[SignalService] Warning: SIGNAL variables not set in .env")
        return
        
    thread = threading.Thread(target=_listen_loop, daemon=True)
    thread.start()


def get_active_signal_message() -> Optional[dict[str, Any]]:
    """Return the currently active message, or None if it was cleared."""
    return _active_message