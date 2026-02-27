from core.state_engine import StateEngine
import json
from datetime import datetime

class EventProcessor:

  def __init__(self):
    self.StateEngine = StateEngine()

  def process(self, topic, payload):
    try:
      data = json.load(payload)
    except json.JSONDecodeError:
      print("Invalid Json. File Ignored.")
      return
    
    if "mazemov" in topic:
      self._handle_movement(data)
    elif "mazetemp" in topic:
      self._handle_temperature(data)
    elif "mazesound" in topic:
      self._handle_sound(data)
    else:
      print("Unknow topic. Ignored")

    
  def _handle_movement(self, data):
    required_fields = ["Marsami", "RoomOrigin", "RoomDestiny", "Status"]

    if not all(field in data for field in required_fields):
      print("Movement missing fields")
      return
      
    marsami = data["Marsami"]
    origin = data["RoomOrigin"]
    destiny = data["RoomDestiny"]
    status = data["Status"]

    if not isinstance(marsami, int):
      return
    if not isinstance(origin, int) or not isinstance(destiny, int):
      return
    if status not in [1, 2]:
      return

    if origin < 0 or destiny < 0:
      return

    self.StateEngine.process_movement(marsami_id=marsami, origin=origin, destiny=destiny, status=status)

  def _handle_temperature(self, data):
    if "Temperature" not in data:
      return
    
    value = data["Temperature"]
    timestamp = data.get("Hour")

    if not isinstance(value, (int, float)):
      return
    
    if value < -20 or value > 100:
      print("Temperature out of range")
      return
    
    parsed_time = self._parse_timestamp(timestamp)

    self.StateEngine.update_temperature(timestamp=parsed_time, temp=value)

  def _handle_sound(self, data):

    if "Sound" not in data:
      return

    value = data["Sound"]
    timestamp = data.get("Hour")

    if not isinstance(value, (int, float)):
      return

    if value < 0 or value > 150:
      print("Sound out of range.")
      return

    parsed_time = self._parse_timestamp(timestamp)

    self.StateEngine.update_sound(value, parsed_time)

  
  def _parse_timestamp(self, timestamp):

    if not timestamp:
      return datetime.now()

    try:
      return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
      print("Invalid timestamp. Using system time.")
      return datetime.now()


