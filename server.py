# NAMES Sahibjot Singh Bhoday, Mahad Chaudhary
import socket
import threading
from datetime import datetime
import os
import base64

# Max num of clients that can connect to the server.
MAX_CLIENTS = 3

# client counter to assign unique client names.
client_counter = 1

# client connection details: Each entry is a dict with: name, address, port, accepted_time, finished_time.
client_cache = []
cache_lock = threading.Lock()

# Repository folder with files.
REPO_DIR = "repo"

def handle_client(conn, addr, assigned_name):
    """Handles communication with a connected client."""
    accepted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with cache_lock:
        client_cache.append({
            "name": assigned_name,
            "address": addr[0],
            "port": addr[1],
            "accepted_time": accepted_time,
            "finished_time": None
        })
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {assigned_name} connected from {addr[0]}:{addr[1]}")
    
    # welcome message.
    welcome_msg = f"Welcome {assigned_name}! You are connected from {addr[0]}:{addr[1]}"
    conn.sendall(welcome_msg.encode())
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8').strip()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received from {assigned_name}: {message}")
            
            if message.lower() == "exit":
                conn.sendall("Goodbye!".encode())
                break
            elif message.lower() == "status":
                #connection info.
                status_lines = ["Client Cache:"]
                with cache_lock:
                    for entry in client_cache:
                        finished = entry["finished_time"] if entry["finished_time"] else "N/A"
                        status_lines.append(
                            f"{entry['name']} - {entry['address']}:{entry['port']} - Connected at: {entry['accepted_time']} - Disconnected at: {finished}"
                        )
                status_response = "\n".join(status_lines)
                conn.sendall(status_response.encode())
            elif message.lower() == "list":
                # Forward list of files in the repository.
                if os.path.exists(REPO_DIR) and os.path.isdir(REPO_DIR):
                    files = os.listdir(REPO_DIR)
                    files_list = "\n".join(files) if files else "No files found in repository."
                    response = "Files in repository:\n" + files_list
                else:
                    response = "Repository directory not found."
                conn.sendall(response.encode())
            elif os.path.exists(os.path.join(REPO_DIR, message)) and os.path.isfile(os.path.join(REPO_DIR, message)):
                # file transfer.
                filepath = os.path.join(REPO_DIR, message)
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                file_size = len(file_data)
                # Send header with a newline.
                header = f"FILE_TRANSFER {message} {file_size}\n"
                conn.sendall(header.encode())
                # Wait for "READY" signal.
                ack = conn.recv(1024).decode('utf-8').strip()
                if ack.upper() == "READY":
                    # Send base64 file data.
                    b64_data = base64.b64encode(file_data)
                    conn.sendall(b64_data)
                else:
                    conn.sendall("File transfer aborted.".encode())
            else:
                # "ACK" added to text.
                response = message + " ACK"
                conn.sendall(response.encode())
    except Exception as e:
        print(f"Error with {assigned_name}: {e}")
    finally:
        finished_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with cache_lock:
            for entry in client_cache:
                if entry["name"] == assigned_name and entry["finished_time"] is None:
                    entry["finished_time"] = finished_time
                    break
        conn.close()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {assigned_name} disconnected.")

#count the clients connected to the server.
def main():
    global client_counter

    host = "0.0.0.0" 
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        with cache_lock:
            active_clients = sum(1 for entry in client_cache if entry["finished_time"] is None)
        if active_clients >= MAX_CLIENTS:
            conn.sendall("Server busy. Try again later.".encode())
            conn.close()
            print(f"Rejected connection from {addr[0]}:{addr[1]} - server full.")
        else:
            assigned_name = f"Client{client_counter:02d}"
            client_counter += 1
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, assigned_name))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    main()
