import gc
import socket

from pi_pico_w_server_tools.wifi_tools import connect_to_wifi


def load_html(path_to_html_file: str = "index.html") -> str:

    try:
        with open(path_to_html_file, "r") as file:            
            return file.read()
    except:
        raise Exception(f"file:{path_to_html_file} not found")


def format_dict(target: str, replacement_dict: dict) -> str:
    for key in replacement_dict.keys():
        target = target.replace("{{" + key + "}}", str(replacement_dict[key]))

    return target

def error_page(cl: socket.socket, headline:str = "Unknown Error", message: str = "No message"):
    cl.sendall(compose_response(response=format_dict(load_html("pi_pico_w_server_tools/static/error_page.html"),{"error_text": message, "headline": headline})))

    
def compose_response(
    
    status_code: int = 200,
    status_message: str = "OK",
    response: str | None = None,
) -> str:
    content_length = str(len(response.encode("utf-8")))
    return f"HTTP/1.1 {str(status_code)} {status_message}\nConnection: close \nAccess-Control-Allow-Origin: *\nContent-Length: {content_length}\n\n{str(response)}"


def __favicon(cl: socket.socket, params:dict):
    # in the future framework will support sending files
    return
    try:
        with open("static/logo_only_squares_orange.png", "rb") as file:
            response = file.read()
            cl.sendall(
                f"HTTP/1.1 {str(200)} OK\nServer: {"h.l"}\nConnection: close \nAccess-Control-Allow-Origin: *\n\n{response}"
            )
    except Exception as ex:
        print(f"icon error type: {type(ex)} error: {str(ex)}")


class App:

    def __init__(self, hostname: str | None = None):
        self.hostname = hostname
        self.ip = connect_to_wifi(hostname=self.hostname)
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(1)

        # we ignore favicon for now
        self.routes_map = {"/favicon.ico": __favicon}
        self.error_page_function = error_page

    def main_loop(self):
        
        print(f"listening on: http://{self.ip}")
        print("registered endpoints:")
        
        for i in self.routes_map:
            print(f"\thttp://{self.ip}{i}")

        while True:
            try:

                cl, _ = self.socket.accept()
                self.__redirect(cl)

            except OSError:
                print("connection closed")

            cl.close()
            gc.collect()

    def register_endpoint(self, path: str, func: function):
        if path[-1] == "/":
            path = path[:-1]
        self.routes_map[path] = func

    def register_error_page(self, func:function = error_page):
        self.error_page_function = func
        

    def __parse_uri(self, uri: str) -> tuple[str, dict]:
        params_separator = uri.find("?")
        
        if params_separator == -1:
            return uri, {}

        path = uri[:params_separator]
        
        if path[-1] == "/":
            path = path[:-1]

        params = uri[params_separator + 1:].split("&")
        
        named_parameters = {}
        
        for param in params:
            try:
                key = param.split("=")[0]
                value = param.split("=")[1]
                named_parameters[key] = value
            except Exception as ex:
                print(
                    f"param parsing exception: {str(ex)}, param: {param}",
                )

        return path.strip(), named_parameters

    def __redirect(self, cl: socket.socket):

        request = cl.recv(1024)
        begin = str(request).find("GET")
        referer_str = str(request)[begin:].split("\\n")[0]
        referer_str = referer_str[3:-10]

        route_str = referer_str.strip()

        path, parameters = self.__parse_uri(route_str)
        

        if path not in self.routes_map:
            print(f"page: {path} is not in routes_map")
            error_page(cl, "Page not found error", f"description: page '{path}' not found")
            return

        try:
            print(f"Registered connection to: {path}, params: {parameters}")
            self.routes_map[path](cl, parameters)

        except KeyboardInterrupt as err:
            print("KeyboardInterrupt error appeared")
            raise err

        except Exception as err:
            print(f"error 500, {str(err)}")
            error_page(cl, "Internal server error",f"description: {str(err)}")
   
   
    