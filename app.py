import gc
import socket
from wifi_tools import connect_to_wifi


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

def error_page(cl: socket.socket, message: str = None, stack_trace: dict = None):

    page_str = load_html("static/page_404.html")
    
    if message == None:
        message = "No message"
    if stack_trace == None:
        stack_trace = "No stack trace"

    page_str = page_str.format(short_message=message, stack_trace=str(stack_trace))

    cl.send(page_str)


def __favicon(cl: socket.socket, params:dict):
    try:
        with open("static/ogo_only_squares_orange.png", "r") as file:
            response = file.read()
            print(len(response))
            cl.sendall(
                f"HTTP/1.1 {str(200)} OK\nServer: {"h.l"}\nConnection: close \nAccess-Control-Allow-Origin: *\n\n{str(response)}"
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

    def compose_response(
        self,
        status_code: int = 200,
        status_message: str = "OK",
        response: str | None = None,
    ) -> str:
        content_length = str(len(response.encode("utf-8")))
        return f"HTTP/1.1 {str(status_code)} {status_message}\nServer: {self.hostname}\nConnection: close \nAccess-Control-Allow-Origin: *\nContent-Length: {content_length}\n\n{str(response)}"

    def main_loop(self):
        
        print(f"listening on: http://{self.ip}")
        print("registered endpoints:")
        
        for i in self.routes_map:
            print(f"\thttp://{self.ip}{i}")

        while True:
            try:

                cl, _ = self.socket.accept()
                self.__redirect(cl)

            except OSError as e:
                print("connection closed")

            cl.close()
            gc.collect()

    def register_endpoint(self, path: str, func: function):
        if path[-1] == "/":
            path = path[:-1]
        self.routes_map[path] = func

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
            error_page(cl, f"404 page: {path} is not in routes_map")
            return

        try:
            print(f"Registered connection to: {path}, params: {parameters}")
            self.routes_map[path](cl, parameters)

        except KeyboardInterrupt as err:
            print("KeyboardInterrupt error appeared")
            raise err

        except Exception as err:
            print("Endpoint error")
            raise err
