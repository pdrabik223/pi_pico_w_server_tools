# Server tools for pi pico w

## Install
1. In your project root run 
```
git submodule add https://github.com/pdrabik223/pi_pico_w_server_tools
```

2. Optionally define wifi_config.json file in root folder, here's an example:
```
[
    {
        "default_network": "admin1"
    }
]
```    

3. Simply import App class in your project and call 'main_loop' function    

```
from pi_pico_w_server_tools.app import App

app = App(hostname="rpi_pi_pico.local")

if __name__ == "__main__":

    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")
```
4. To define custom endpoints simply follow an example in main.py
```
import socket
from app import App, compose_response, load_html

app = App(hostname="rpi_pi_pico.local")

def home_page(cl: socket.socket, parameters: dict):
    cl.sendall(compose_response(response=load_html("static/index.html")))

if __name__ == "__main__":

    app.register_endpoint("/v1", home_page)

    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")
```
By default 

## TODO
- [ ] add connection monitoring and restoring
- [ ] optionally require that network has connection to the internet
- [ ] create request wrapper so that in case of network error, framework can catch the error, retry connection and re-send request