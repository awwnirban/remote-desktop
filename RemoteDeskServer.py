import socket
import threading
from PIL import ImageGrab
import io
import pyautogui

def send_screen(client_socket):
    try:
        while True:
            # Capture the screen
            screen = ImageGrab.grab()
            
            # Convert the screen image to RGB mode
            screen_rgb = screen.convert('RGB')
            
            # Convert the screen image to bytes
            img_bytes = io.BytesIO()
            screen_rgb.save(img_bytes, format='JPEG')
            img_bytes = img_bytes.getvalue()
            
            # Send the screen image bytes to the client
            client_socket.sendall(len(img_bytes).to_bytes(4, byteorder='big'))
            client_socket.sendall(img_bytes)
    except Exception as e:
        print("Error sending screen:", e)


def handle_client(client_socket):
    try:
        while True:
            # Receive mouse events from the client
            data = client_socket.recv(1024).decode()
            if not data:
                break
            
            # Process the mouse events
            parts = data.split()
            if len(parts) == 3 and parts[0] == 'MOVE':
                x, y = int(parts[1]), int(parts[2])
                pyautogui.moveTo(x, y)
            elif len(parts) == 2 and parts[0] == 'CLICK':
                button = parts[1]
                if button == 'LEFT':
                    pyautogui.click(button='left')
                elif button == 'RIGHT':
                    pyautogui.click(button='right')
    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server listening on", (host, port))
    while True:
        client_socket, addr = server_socket.accept()
        print("Connected to", addr)
        # Start a thread to handle screen sending
        screen_thread = threading.Thread(target=send_screen, args=(client_socket,))
        screen_thread.daemon = True
        screen_thread.start()
        # Start a thread to handle client commands
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server('192.168.0.7', 5555)