# NAMES Sahibjot Singh Bhoday, Mahad Chaudhary
import socket
import base64

def recv_until_newline(sock):

    data = b""
    while b'\n' not in data:
        part = sock.recv(1024)
        if not part:
            break
        data += part
    if b'\n' in data:
        header, leftover = data.split(b'\n', 1)
        return header, leftover
    return data, b""

def main():
    server_host = "127.0.0.1"  
    server_port = 12345

    # TCP socket creation & server connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_host, server_port))
    
    # local connection display
    local_ip, local_port = sock.getsockname()
    print(f"Connected to server at {server_host}:{server_port} from local address {local_ip}:{local_port}")
    
    # welcome message recieve & display
    welcome_msg = sock.recv(1024).decode('utf-8')
    print("Server:", welcome_msg)
    
    while True:
        # user input
        message = input("Enter message (or command): ")
        sock.sendall(message.encode())
        
        # goodbye message and exit.
        if message.lower() == "exit":
            response = sock.recv(1024).decode('utf-8')
            print("Server:", response)
            break

        # get server's response.
        data = sock.recv(4096)
        
        # Check if file transfer
        if data.startswith(b"FILE_TRANSFER"):
            # Ensure full header
            if b'\n' not in data:
                header, leftover = recv_until_newline(sock)
            else:
                header, leftover = data.split(b'\n', 1)
            header_str = header.decode('utf-8')
            parts = header_str.split()
            if len(parts) < 3:
                print("Invalid file transfer header received.")
                continue

            # get filename and filesize.
            filename = parts[1]
            try:
                filesize = int(parts[2])
            except ValueError:
                print("Invalid filesize in header.")
                continue
            print(f"Downloading file '{filename}' ({filesize} bytes).")
            
            # Tell server ready to receive file.
            sock.sendall("READY".encode())
            
            # Calculate length of base64 data.
            expected_b64_length = 4 * ((filesize + 2) // 3)
            file_data_encoded = leftover  
            
            # Continue receiving until base64 data done
            while len(file_data_encoded) < expected_b64_length:
                packet = sock.recv(4096)
                if not packet:
                    break
                file_data_encoded += packet
            
            try:
                # Decode the base64 data.
                file_data = base64.b64decode(file_data_encoded)
                download_filename = "downloaded_" + filename
                with open(download_filename, 'wb') as f:
                    f.write(file_data)
                print(f"File '{filename}' downloaded and saved as '{download_filename}'.")
            except Exception as e:
                print("Error decoding or saving file:", e)
        else:
            # response from the server.
            print("Server:", data.decode('utf-8'))
            
    sock.close()

if __name__ == "__main__":
    main()