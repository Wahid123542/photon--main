# Test file for udp_server.py (Sprint 2)
# Run with:
#   python3 test_udp.py

from udp_server import UDPServer
import time


udp = UDPServer()

time.sleep(1)  # give sockets time to bind

udp.broadcast_equipment_id(11)
udp.broadcast_equipment_id(22)