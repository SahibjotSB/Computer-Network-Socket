import socket

# Server details
HOST = '127.0.0.1'  # Localhost
PORT = 12345        # Server port

def start_client():
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print("Connected to the server.")

        # Receive assigned client name
        client_name = client_socket.recv(1024).decode()
        print(f"Assigned name: {client_name}")

        # Communication loop
        while True:
            message = input("> ")  # User input

            if not message:
                continue  # Ignore empty messages

            client_socket.send(message.encode())

            # Handle exit case
            if message.lower() == "exit":
                print("Disconnecting from server.")
                break

            # Receive response from server
            response = client_socket.recv(1024).decode()
            print(f"Server: {response}")

    except ConnectionRefusedError:
        print("Server is unavailable. Try again later.")

    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
