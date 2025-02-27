import socket
import pickle
import threading
import time

class NetworkManager:
    def __init__(self):
        self.server = None
        self.client = None
        self.is_server = False
        self.host = "0.0.0.0"  # Default host
        self.port = 5555  # Default port
        self.connected = False
        self.client_connected = False
        self.server_thread = None
        self.receive_thread = None
        self.data_buffer = []
        self.max_buffer_size = 10
        self.running = False
        
    def start_server(self):
        """Start a game server that listens for one client"""
        try:
            self.is_server = True
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.settimeout(1.0)  # Set timeout for accepting connections
            self.server.listen(1)
            self.running = True
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            return True, "Server started successfully."
        except Exception as e:
            return False, f"Failed to start server: {str(e)}"
    
    def connect_to_server(self, server_ip):
        """Connect to a game server as a client"""
        try:
            self.is_server = False
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5.0)  # 5 second timeout for connection
            self.client.connect((server_ip, self.port))
            self.client.settimeout(1.0)  # Set timeout for recv
            self.connected = True
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._client_receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True, "Connected to server successfully."
        except Exception as e:
            return False, f"Failed to connect to server: {str(e)}"
    
    def _server_loop(self):
        """Background thread for server to accept and handle client connections"""
        try:
            print("Waiting for client to connect...")
            while self.running:
                try:
                    self.client, addr = self.server.accept()
                    print(f"Client connected from {addr}")
                    self.client_connected = True
                    self.connected = True
                    
                    # Start receiving data from client
                    self._client_receive_loop()
                    break
                except socket.timeout:
                    # This is expected due to the timeout we set
                    continue
                except Exception as e:
                    print(f"Error accepting client: {str(e)}")
                    break
        except Exception as e:
            print(f"Server loop error: {str(e)}")
        finally:
            self.close()
    
    def _client_receive_loop(self):
        """Background thread for receiving data from server or client"""
        try:
            while self.running and self.connected:
                try:
                    data = self.client.recv(4096)
                    if not data:
                        print("Connection closed by peer")
                        break
                    
                    # Deserialize the received data
                    received_data = pickle.loads(data)
                    
                    # Add to buffer for game to process
                    self.data_buffer.append(received_data)
                    if len(self.data_buffer) > self.max_buffer_size:
                        self.data_buffer.pop(0)  # Remove oldest data if buffer is full
                except socket.timeout:
                    # This is expected due to the timeout we set
                    continue
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Receive loop error: {str(e)}")
        finally:
            self.connected = False
            self.client_connected = False
    
    def send_data(self, data):
        """Send data to the connected client/server"""
        if not self.connected:
            return False, "Not connected"
        
        try:
            # Serialize the data
            serialized_data = pickle.dumps(data)
            self.client.send(serialized_data)
            return True, "Data sent successfully"
        except Exception as e:
            self.connected = False
            return False, f"Failed to send data: {str(e)}"
    
    def get_latest_data(self):
        """Get the latest data from the buffer and clear it"""
        if not self.data_buffer:
            return None
        
        # Get the latest data
        latest_data = self.data_buffer.copy()
        self.data_buffer.clear()
        return latest_data
    
    def close(self):
        """Close all connections and stop threads"""
        self.running = False
        
        # Close client socket
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        
        # Close server socket
        if self.server:
            try:
                self.server.close()
            except:
                pass
            self.server = None
        
        self.connected = False
        self.client_connected = False
        
        # Wait for threads to terminate
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1.0)
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
        
        return True, "Network connections closed."

    def get_server_ip(self):
        """Get the local machine's IP address for hosting"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # This doesn't actually establish a connection, but helps get the local IP
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"  # Fallback to localhost
