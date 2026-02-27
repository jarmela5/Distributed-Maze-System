class StateEngine:

  def __init__(self):
    self.rooms = {}
    self.marsami_positions = {}
    self.marsami_types = {}
    self.temperature = {}
    self.sound = {}

  def _ensure_room_exists(self, room_id):
    if room_id not in self.rooms:
      self.rooms[room_id] = {"total": 0, "odd": 0, "even": 0}

  def _get_type(self, marsami_id):
    if marsami_id not in self.marsami_types:
      if marsami_id % 2 == 0:
        self.marsami_types[marsami_id] = "even"
      else:
        self.marsami_types[marsami_id] = "odd"
    
    return self.marsami_type[marsami_id]
  

  def process_movement(self, marsami_id, origin, destiny, status):

    marsami_type = self._get_type(marsami_id=marsami_id)

    if origin == 0 and destiny != 0:
      self._ensure_room_exists(room_id=destiny)

      self.rooms[destiny]["total"] += 1
      self.rooms[destiny][marsami_type] +=1

      self.marsami_positions[marsami_id] = destiny
      return
    
    if origin != 0 and destiny != 0:
      # verificar consistência
      if marsami_id not in self.marsami_positions:
        print(f"[WARNING] Marsami {marsami_id} sem posição conhecida.")
        return

      current_room = self.marsami_positions[marsami_id]

      if current_room != origin:
        print(f"[INCONSISTÊNCIA] Marsami {marsami_id} esperado em {current_room} mas veio de {origin}")
        return

      self._ensure_room_exists(origin)
      self._ensure_room_exists(destiny)

      # remover da origem
      self.rooms[origin]["total"] -= 1
      self.rooms[origin][marsami_type] -= 1

      # adicionar ao destino
      self.rooms[destiny]["total"] += 1
      self.rooms[destiny][marsami_type] += 1

      self.marsami_positions[marsami_id] = destiny
      return

    # CASO 3 — Parado definitivo (Status 2)
    if origin == 0 and destiny == 0 and status == 2:
      # não altera sala
      return
    
  def update_temperature(self, timestamp, temp):
    self.temperature[timestamp] = temp

  def update_sound(self, timestamp, sound):
    self.sound[timestamp] = sound





    