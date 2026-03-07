from core.state_engine import StateEngine
import json
from datetime import datetime
import re

class EventProcessor:

  def __init__(self, stateEngine:StateEngine):
      self.state_engine = stateEngine

  def process(self, topic, payload):
    try:
      data = json.loads(payload)
    except Exception:
      print("[ERROR] Invalid JSON. Ignored.")
      return

    data = self._normalize_keys(data)

    if "mazemov" in topic:
        self._handle_movement(data)
    elif "mazetemp" in topic:
        self._handle_temperature(data)
    elif "mazesound" in topic:
        self._handle_sound(data)
    else:
        print("[WARNING] Unknown topic. Ignored.")


  def _normalize_keys(self, data):
    normalized = {}
    for key, value in data.items():
      clean_key = key.lower()
      clean_key = re.sub(r'[^a-z]', '', clean_key)
      
      normalized[clean_key] = value

    return normalized


  def _handle_movement(self, data):
    required_fields = ["marsami", "roomorigin", "roomdestiny", "status"]
    if not all(field in data for field in required_fields):
      print("[MOVEMENT] Missing required fields.")
      return

    marsami = data["marsami"]
    origin = data["roomorigin"]
    destiny = data["roomdestiny"]
    status = data["status"]

    if not isinstance(marsami, int):
       return
    if not isinstance(origin, int) or not isinstance(destiny, int):
       return
    if status not in [0, 1, 2]:
       return


    self.state_engine.process_movement(
        marsami_id=marsami,
        origin=origin,
        destiny=destiny,
        status=status
    )


  def _handle_temperature(self, data):
    if "temperature" not in data:
      return

    value = data["temperature"]
    timestamp = data.get("hour")

    if not isinstance(value, (int, float)):
      return

    parsed_time = self._parse_timestamp(timestamp)

    self.state_engine.update_temperature(
       timestamp=parsed_time,
       temp=value
    )


  def _handle_sound(self, data):
    if "sound" not in data:
      return

    value = data["sound"]
    timestamp = data.get("hour")

    if not isinstance(value, (int, float)):
      return

    parsed_time = self._parse_timestamp(timestamp)

    self.state_engine.update_sound(
       timestamp=parsed_time,
        sound=value
    )


  def _parse_timestamp(self, timestamp):
    if not timestamp:
      return datetime.now()

    try:
      return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
      print("[WARNING] Invalid timestamp. Using system time.")
      return datetime.now()