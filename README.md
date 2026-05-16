# Raspberry Pi Pico W Server Tools

This library provides server tools for the Raspberry Pi Pico W, enabling easy setup of web servers and Wi-Fi management.

## Installation

1. In your project root, run the following command to add this library as a Git submodule:
   ```
   git submodule add https://github.com/pdrabik223/pi_pico_w_server_tools
   ```

2. Optionally, define a `wifi_config.json` file in the root folder. Here is an example configuration:
   ```json
   [
       {
           "default_network": "admin1"
       }
   ]
   ```
   This file specifies known Wi-Fi networks.

3. Import the `App` class in your project and call the `main_loop` function:
   ```python
   from pi_pico_w_server_tools.app import App

   app = App(hostname="rpi_pi_pico.local")

   if __name__ == "__main__":
       try:
           app.main_loop()
       except (KeyboardInterrupt, Exception) as ex:
           print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")
   ```

4. To define custom endpoints, follow the example in `main.py`:
   ```python
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

## Passing Variables to HTML

### HTML
Encapsulate variable names with double curly braces `{{}}`:

```html
<h1>{{page_name}}</h1>
```

A full example can be found in the `static/index.html` file.

### Python
Wrap the `load_html` function with `format_dict` and pass a dictionary where the keys correspond to variables defined in the HTML file. The `format_dict` function replaces segments in the format `{{variable_name}}` with the corresponding values from the dictionary.

A full example can be found in the `app.py` file:

```python
def home_page(cl: socket.socket, parameters: dict):
    cl.sendall(compose_response(response=format_dict(load_html("pi_pico_w_server_tools/static/index.html"), {"page_name": "Home Page"})))
```

## TODO

- [ ] Add connection monitoring and restoring
- [ ] Optionally require that the network has an internet connection - tested with ping to google.com
- [ ] Create a request wrapper to catch network errors, retry connections, and resend requests
- [ ] Add request ID support
- [ ] Integrate option for remote http and js hosting. Pico simply points to remotely hosted js web app, and runs script in local network. No shure if it will work  
- [ ] request param validation support
- [ ] support for post requests