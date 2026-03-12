from core.state_engine import StateEngine
from core.decision_engine import DecisionEngine
from persistance.mongo_repository import MongoRepository
import json
from datetime import datetime
import re


class EventProcessor:

  def __init__(self, stateEngine: StateEngine, mongo_repo: MongoRepository, decision_engine: DecisionEngine):
    self.state_engine = stateEngine
    self.mongo_repo = mongo_repo
    self.decision_engine = decision_engine


  def process(self, topic, payload):
    
    try:
      data = json.loads(payload)
    except Exception:
      print("[ERROR] Invalid JSON. Ignored.")
      return

    data = self._normalize_keys(data)

    player = self._extract_player(topic)

    if "mazemov" in topic:
      self._handle_movement(data, player)

    elif "mazetemp" in topic:
      self._handle_temperature(data, player)

    elif "mazesound" in topic:
      self._handle_sound(data, player)

    else:
      print("[WARNING] Unknown topic. Ignored.")


  def _normalize_keys(self, data):
    
    normalized = {}

    for key, value in data.items():
      
      clean_key = key.lower()
      clean_key = re.sub(r'[^a-z]', '', clean_key)

      normalized[clean_key] = value

    return normalized


  def _extract_player(self, topic):
      
    try:
      return int(topic.split("_")[-1])
    except:
      return None


  def _handle_movement(self, data, player):

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

    event = self.state_engine.process_movement(
      marsami_id=marsami,
      origin=origin,
      destiny=destiny,
      status=status
    )

    if event:
      
      event["player"] = player
      event["timestamp"] = event.get("timestamp", datetime.now())

      self.mongo_repo.save_movement(event)

      if not event["is_invalid"]:

        self.mongo_repo.save_room_occupancy(self.state_engine.rooms)
              
      if(self.state_engine.game_started == True):
        self.decision_engine.evaluate() 
  


  def _handle_temperature(self, data, player):

    if "temperature" not in data:
      return

    value = data["temperature"]
    timestamp = data.get("hour")

    if not isinstance(value, (int, float)):
      return

    parsed_time = self._parse_timestamp(timestamp)

    event = self.state_engine.update_temperature(
        timestamp=parsed_time,
        temp=value
    )

    event["player"] = player

    self.mongo_repo.save_temperature(event)
    if(self.state_engine.game_started == True):
      self.decision_engine.evaluate() 



  def _handle_sound(self, data, player):

    if "sound" not in data:
      return

    value = data["sound"]
    timestamp = data.get("hour")

    if not isinstance(value, (int, float)):
      return

    parsed_time = self._parse_timestamp(timestamp)

    event = self.state_engine.update_sound(
      timestamp=parsed_time,
      sound=value
    )

    event["player"] = player

    self.mongo_repo.save_sound(event)
    if(self.state_engine.game_started == True):
      self.decision_engine.evaluate() 


  def _parse_timestamp(self, timestamp):

    if not timestamp:
      return datetime.now()

    try:
      return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
      print("[WARNING] Invalid timestamp. Using system time.")
      return datetime.now()