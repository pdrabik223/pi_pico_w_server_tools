from app import App

app = App(hostname="server_name.local")

if __name__ == "__main__":

    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")
