import socket
import json
import threading
import time

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients = []
        self.game_state = {
            'player1': {'x': 100, 'y': 300, 'attacking': False, 'health': 100},
            'player2': {'x': 700, 'y': 300, 'attacking': False, 'health': 100},
            'clash_battle': None
        }
        print(f"Server started on {host}:{port}")

    def handle_client(self, conn, player_num):
        while True:
            try:
                data = conn.recv(2048).decode()
                if not data:
                    break
                
                # Update game state with received player data
                player_data = json.loads(data)
                if player_num == 1:
                    self.game_state['player1'].update(player_data)
                else:
                    self.game_state['player2'].update(player_data)
                
                # Send updated game state to both players
                game_state_json = json.dumps(self.game_state)
                for client in self.clients:
                    try:
                        client.send(game_state_json.encode())
                    except:
                        pass
            except:
                break
        
        conn.close()
        if conn in self.clients:
            self.clients.remove(conn)

    def start(self):
        while len(self.clients) < 2:
            conn, addr = self.server.accept()
            self.clients.append(conn)
            player_num = len(self.clients)
            print(f"Player {player_num} connected from {addr}")
            
            # Start a new thread to handle this client
            thread = threading.Thread(target=self.handle_client, args=(conn, player_num))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    server = GameServer()
    server.start()
