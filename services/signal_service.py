import json
import subprocess
import threading
import time
import datetime
import shutil
import os
from typing import Any, Optional
from config import Config

# Holds the currently active message
_active_message: Optional[dict[str, Any]] = None

# Smart toggle: Checks if signal-cli is installed on the current system.
_signal_cli_available = shutil.which("signal-cli") is not None

def _send_read_receipt(sender_number: str, timestamp: int) -> None:
    """Send a read receipt back to the sender (only active in production with signal-cli)."""
    if not _signal_cli_available or not sender_number or not timestamp:
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

def _send_group_message(text: str) -> None:
    """Send a confirmation message to the Signal group."""
    if not _signal_cli_available or not Config.SIGNAL_GROUP_ID:
        return
    try:
        subprocess.run(
            [
                "signal-cli",
                "-a", Config.SIGNAL_PHONE_NUMBER,
                "send",
                "-m", text,
                "-g", Config.SIGNAL_GROUP_ID
            ],
            capture_output=True,
            check=False
        )
    except Exception as error:
        print(f"[SignalService] Error sending group confirmation: {error}")


def _listen_loop() -> None:
    """Background loop polling either signal-cli (Production) or mock_signal.txt (Local Dev)."""
    global _active_message
    
    # ==========================================
    # LOCAL DEVELOPMENT MODE
    # ==========================================
    if not _signal_cli_available:
        print("[SignalService] Running in Local-Mode: 'signal-cli' not found.")
        print("[SignalService] Create/Edit 'mock_signal.txt' in the root directory to test messages.")
        
        mock_file = "mock_signal.txt"
        last_mtime = 0.0
        
        while True:
            try:
                if os.path.exists(mock_file):
                    current_mtime = os.path.getmtime(mock_file)
                    
                    if current_mtime > last_mtime:
                        last_mtime = current_mtime
                        with open(mock_file, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                        
                        if content:
                            if "löschen" in content.lower():
                                _active_message = None
                                print("[SignalService (Mock)] Active message cleared via command.")
                            else:
                                _active_message = {
                                    "sender": "Local Tester 🧪",
                                    "text": content,
                                    "timestamp_display": datetime.datetime.now().strftime("%d.%m.%Y um %H:%M")
                                }
                                print(f"[SignalService (Mock)] Message loaded successfully: {content[:20]}...")
            except Exception as e:
                print(f"[SignalService (Mock)] Error reading mock file: {e}")
                
            time.sleep(2)
        return

    # ==========================================
    # PRODUCTION MODE (Raspberry Pi)
    # ==========================================
    print("[SignalService] Background listener started (Real signal-cli mode).")
    while True:
        try:
            result = subprocess.run(
                ["signal-cli", "--output", "json", "-a", Config.SIGNAL_PHONE_NUMBER, "receive"],
                capture_output=True, 
                text=True, 
                encoding="utf-8",
                errors="replace"
            )
            
            if result.returncode != 0 and result.stderr.strip():
                print(f"[SignalService] CLI Error: {result.stderr.strip()}")

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                    
                envelope = data.get("envelope", {})
                data_message = envelope.get("dataMessage", {})
                
                # Ignore non-text messages
                if not data_message:
                    continue
                
                sender_number = envelope.get("sourceNumber")
                
                # CRITICAL: Prevent infinite loop by ignoring messages sent by the Pi itself
                if sender_number == Config.SIGNAL_PHONE_NUMBER:
                    continue
                    
                # Process only messages originating from the designated group
                if data_message.get("groupInfo", {}).get("groupId") == Config.SIGNAL_GROUP_ID:
                    msg_text = data_message.get("message", "")
                    
                    # Resolve sender name
                    raw_sender = envelope.get("sourceName") or sender_number or "Family"
                    sender_name = Config.SIGNAL_USER_MAPPING.get(raw_sender, raw_sender)
                    msg_timestamp = data_message.get("timestamp")
                    
                    if msg_text:
                        # Robust clear command detection
                        if "löschen" in msg_text.strip().lower():
                            _active_message = None
                            print("[SignalService] Active message cleared via command.")
                            _send_group_message("❌ Deleted")
                        else:
                            _active_message = {
                                "sender": sender_name,
                                "text": msg_text,
                                "timestamp_display": datetime.datetime.now().strftime("%d.%m.%Y um %H:%M")
                            }
                            print(f"[SignalService] New message processed from {sender_name}.")
                            _send_group_message("✅ Displayed")
                            
                        # Trigger read receipt
                        if sender_number and msg_timestamp:
                            _send_read_receipt(sender_number, msg_timestamp)

        except Exception as error:
            print(f"[SignalService] Error fetching messages: {error}")
            
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