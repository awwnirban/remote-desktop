import socket
import threading
import tkinter as tk
from PIL import Image, ImageTk
import io

class RemoteDesktopClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = tk.Tk()
        self.root.title("Remote Desktop Client")
        self.root.geometry("1920x1080")
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<Button-1>', self.on_mouse_left_click)
        self.root.bind('<Button-3>', self.on_mouse_right_click)
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()
        self.connect_to_server()
        self.receive_screen()

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to server")
        except Exception as e:
            print("Error connecting to server:", e)
            self.root.destroy()

    def receive_screen(self):
        try:
            while True:
                size_data = self.client_socket.recv(4)
                if not size_data:
                    break
                size = int.from_bytes(size_data, byteorder='big')
                image_data = b''
                while len(image_data) < size:
                    chunk = self.client_socket.recv(min(size - len(image_data), 4096))
                    if not chunk:
                        break
                    image_data += chunk
                if len(image_data) < size:
                    print("Error: Incomplete image data received")
                    break
                image = Image.open(io.BytesIO(image_data))
                self.display_screen(image)
        except Exception as e:
            print("Error receiving screen:", e)
        finally:
            self.client_socket.close()

    def display_screen(self, image):
        img = ImageTk.PhotoImage(image)
        self.canvas.delete("all")  # Clear previous image
        self.canvas.config(width=image.width, height=image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.root.update()  # Update the GUI
        
    def on_mouse_move(self, event):
        # Send mouse move event to the server
        x, y = event.x, event.y
        message = f"MOVE {x} {y}\n"
        self.client_socket.sendall(message.encode())

    def on_mouse_left_click(self, event):
        # Send left mouse click event to the server
        message = "CLICK LEFT\n"
        self.client_socket.sendall(message.encode())

    def on_mouse_right_click(self, event):
        # Send right mouse click event to the server
        message = "CLICK RIGHT\n"
        self.client_socket.sendall(message.encode())
    

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = RemoteDesktopClient('192.168.0.7', 5555)
    client.start()