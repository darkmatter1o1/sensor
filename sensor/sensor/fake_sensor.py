import socket
import struct
import time

def start_fake_sensor():
    HOST = '127.0.0.1'
    PORT = 2000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"Fake Sensor running on {HOST}:{PORT}")

    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            print(f"Received: {data.strip()}")

            if data.startswith("#03"):
                # Start Command - Parse interval
                interval = struct.unpack('<H', bytes.fromhex(data[3:-2]))[0]
                print(f"Start Command Received. Interval: {interval} ms")
                while True:
                    # Send status message every interval
                    time.sleep(interval / 1000.0)
                    payload = struct.pack('<Hhhhh', 5000, 250, 150, -100, 75)  # Fake data
                    payload_hex = payload.hex().upper()
                    response = f"$11{payload_hex}\r\n"
                    conn.sendall(response.encode())
                    print(f"Sent: {response.strip()}")
            elif data.startswith("#09"):
                # Stop Command
                print("Stop Command Received.")
                break
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()
        server_socket.close()

def main():
    start_fake_sensor()

if __name__ == "__main__":
    main()
