import socket
import threading
from datetime import datetime  # Correct import

# Server configuration
HOST = '127.0.0.1'  
PORT = 12345        # Port to listen on
MAX_CLIENTS = 3     # Maximum number of clients allowed

# Global variables
client_counter = 1  # Counter for client names
clients = {}        # Dictionary to store active clients
client_cache = {}   # Dictionary to store client connection details

def handle_client(client_socket, client_name):
    """Handles communication with a client."""
    
    # Log connection time
    connection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_cache[client_name] = {
        "connected_at": connection_time,
        "disconnected_at": None
    }

    print(f"{client_name} connected at {connection_time}")  # Print start time

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Client Left session 
            
            message = data.decode().strip()
            print(f"{client_name} sent: {message}")  # Example: Client01 sent: Hello

            if message.lower() == "exit":
                print(f"{client_name} disconnected.")
                break  # Exit the loop and close connection

            elif message.lower() == "status":
                # Send the current cache details back to the client
                status_report = "\n".join(
                    [f"{k}: Connected at {v['connected_at']}, Disconnected at {v['disconnected_at']}" 
                     for k, v in client_cache.items()]
                )
                client_socket.send(status_report.encode())

            else:
                # Echo message with ACK
                response = f"{message} ACK"
                client_socket.send(response.encode())  # Example: Hello ACK

    except ConnectionResetError:
        print(f"{client_name} disconnected unexpectedly.")

    finally:
        # Log disconnection time
        disconnect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_cache[client_name]["disconnected_at"] = disconnect_time
        
        # Print both start and end times
        print(f"{client_name} connected at {client_cache[client_name]['connected_at']} and disconnected at {disconnect_time}")

        # Clean up on client disconnect
        client_socket.close()
        del clients[client_name]

def start_server():
    global client_counter

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CLIENTS)
    print(f"Server is listening on {HOST}:{PORT}...")

    while True:
        # Accept a new client connection
        client_socket, client_address = server_socket.accept()

        # Enforce client limit
        if len(clients) >= MAX_CLIENTS:
            print(f"Max clients reached. Rejecting {client_address}")
            client_socket.send(b"Server full. Try again later.")
            client_socket.close()
            continue

        # Assign a unique name
        client_name = f"Client{client_counter:02d}"
        client_counter += 1

        # Store client info
        clients[client_name] = client_socket
        print(f"Assigned {client_name} to {client_address}")

        # Send the assigned name to the client
        client_socket.send(client_name.encode())

        # Start a thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_name))
        client_thread.start()

if __name__ == "__main__":
    start_server()
