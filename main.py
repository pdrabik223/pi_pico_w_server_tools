from server.app import App, load_html
import socket

app = App(hostname="server_name.local")

def home_page(cl: socket.socket, parameters: dict):
    cl.sendall(load_html("index.html"))

if __name__ == "__main__":
    
    app.register_endpoint("/v1", home_page)
    
    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")
