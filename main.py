from app import App, load_html, compose_response
import socket

app = App(hostname="server_name.local")

def home_page(cl: socket.socket, parameters: dict):
    
    cl.sendall(compose_response(response=load_html("static/index.html")))


if __name__ == "__main__":
    
    app.register_endpoint("/v1", home_page)
    
    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")
