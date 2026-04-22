from interface import Server
from collections import deque
import database
from constants import CODE_BASESCORE_RED, CODE_BASESCORE_GREEN, SCORE_TAKEDOWN, PENALTY_TAKEDOWN, SCORE_BASE

# 
# core purpose: handling data between a server and clients
# 
class Model:
  GREEN = 0
  RED = 1

  def __init__(self, server:Server):
    self.udp=server
    self.basedq = deque()
    self.basedset = set()
    self.messageq = deque()
    self.scorediffq = deque()
    self.equip_to_codename = {} # codename dictionary via equip id
    self.equip_to_team = {}     # team id lookup via equip id

  # def basedPlayerCount(self):
  #   return len(self.basedq)
  
  def pop_live_message(self):
    return self.messageq.popleft() if self.messageq else False
  
  # called every frame by window.py
  def pop_based_equip_id(self):
    return self.basedq.popleft() if self.basedq else False

  def pop_score_diff(self):
    return self.scorediffq.popleft() if self.scorediffq else False

  # this will be called by self.handleInput()
  def _insertBasedEquipID(self, id):
    if id in self.basedset:
      return
    self.basedset.add(id)
    self.basedq.append(id)
  
  def _insertLiveMessage(self, string:str, emergent=False):
    if emergent:
      self.messageq.appendleft(string)
    else:
      self.messageq.append(string)

  #  called by UDPServer in need
  def handleInput(self, input: str) -> bool:
    parts = input.split(':')
    print(f"[Model] handleInput called with: {input}")

    if len(parts)!=2 or not parts[0].isdigit() or not parts[1].isdigit() :
      return False
    
    self._handleDigitPair(int(parts[0]), int(parts[1]))
    return True
  
  # TODO: needs to implemented
  # return a value exactly how it's stored in the database class
  # def _getPlayerID(self, equip_id: int) -> int:
  #   return 0
  
  # # TODO: needs to be implemented
  # # return either 0 or 1 (red or green)
  # def _getTeamID(self, equip_id: int) -> int:
  #   return equip_id%2

  def _grant_score(self, equip_id: int, diff: int):
    self.scorediffq.append((equip_id, diff))

  def _get_team(self, equip_id: int):
    return self.equip_to_team.get(equip_id)

  # should call methods at self.udp based on the situation
  def _handleDigitPair(self, hitter: int, receiver: int):
    print(f"[Model] _handleDigitPair: hitter={hitter}, receiver={receiver}")
    print(f"[Model] equip_to_codename: {self.equip_to_codename}")

    if receiver == int(CODE_BASESCORE_RED):
      hitter_name = self.equip_to_codename.get(hitter)
      if self._get_team(hitter) == Model.GREEN and hitter_name is not None:
        self._insertBasedEquipID(hitter)
        self._grant_score(hitter, SCORE_BASE)
        self._insertLiveMessage(f"{hitter_name} hit Red Team's Base")
      return

    if receiver == int(CODE_BASESCORE_GREEN):
      hitter_name = self.equip_to_codename.get(hitter)
      if self._get_team(hitter) == Model.RED and hitter_name is not None:
        self._insertBasedEquipID(hitter)
        self._grant_score(hitter, SCORE_BASE)
        self._insertLiveMessage(f"{hitter_name} hit Green Team's Base")
      return

    hitter_name = self.equip_to_codename.get(hitter)
    receiver_name = self.equip_to_codename.get(receiver)

    if hitter_name is None or receiver_name is None:
      print(f"Unknown equipment ID(s): hitter={hitter}, receiver={receiver}")
      return

    self.udp.broadcast_equipment_id(receiver)

    if self._get_team(hitter) is not None and self._get_team(hitter) == self._get_team(receiver):
      self._grant_score(hitter, PENALTY_TAKEDOWN)
      self._grant_score(receiver, PENALTY_TAKEDOWN)
      self._insertLiveMessage(f"{hitter_name} hit teammate {receiver_name}")
      self.udp.broadcast_equipment_id(hitter)
    else:
      self._grant_score(hitter, SCORE_TAKEDOWN)
      self._insertLiveMessage(f"{hitter_name} hit {receiver_name}")
