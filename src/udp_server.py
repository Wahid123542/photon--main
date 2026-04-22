import socket
import threading
from model import Model
from interface import Server

DEFAULT_RECEIVE_IP = "0.0.0.0"     
DEFAULT_BROADCAST_IP = "255.255.255.255"
BUFFER_SIZE = 1024

SERVER_PORT=7500
CLIENT_PORT=7501


class UDPServer:
    def __init__(
        self,
        receive_ip=DEFAULT_RECEIVE_IP,
        broadcast_ip=DEFAULT_BROADCAST_IP,
    ):
        self.receive_ip = receive_ip
        self.broadcast_ip = broadcast_ip

        # socket for receiving data 
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind((self.receive_ip, CLIENT_PORT))

        # socket for broadcasting data
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            1
        )

        # model
        self.model = None

        print(f"[UDP] Receiving on {self.receive_ip}:{CLIENT_PORT}")
        print(f"[UDP] Broadcasting on {self.broadcast_ip}:{SERVER_PORT}")
    
    def assign_model(self, model:Model):
        self.model=model

    # ==========================
    # Broadcasting
    # ==========================

    def broadcast(self, string):
        self.send_socket.sendto(
            str(string).encode(),
            (self.broadcast_ip, SERVER_PORT)
        )
    
    def announce_game_start(self):
        self.broadcast("202")
        print(f"[UDP] Broadcasted a signal 202, meaning that the game is began")
    
    def announce_game_end(self):
        for _ in range(3):
            self.broadcast("221")
        print(f"[UDP] Broadcasted signal 221 three times, game has ended")

    # broadcast equipment codes after each player addition
    def broadcast_equipment_id(self, equipment_id):
        self.broadcast(equipment_id)
        print(f"[UDP] Broadcasted equipment ID: {equipment_id}")

    # ==========================
    # Receival
    # ==========================

    def on_receive(self, data:bytes, addr):
        data=data.decode()
        print(f"[UDP] recv: {data} from {addr}")
        if not self.model.handleInput(data):
            print(f"[UDP] Error: unsupported request from client: {data}")
                                
    def start_readloop(self):
        print("[UDP] started a read-loop")

        self._running=True
        self._thread = threading.Thread(target=self._readloop, daemon=True)
        self._thread.start()
    
    def _readloop(self):
        while self._running:
            try:
                data, addr = self.recv_socket.recvfrom(BUFFER_SIZE)
                self.on_receive(data, addr)
            except OSError:
                break
    
    def end_readloop(self):
        print("[UDP] ended a read-loop")
        self._running=False

        try:
            self.recv_socket.close()
        except:
            pass
        
        if hasattr(self, "_thread"):
            self._thread.join(timeout=1)
    
