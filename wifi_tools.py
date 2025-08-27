import requests
import network
import json
import time


class WifiConfiguration:
    def __init__(self, ssid: str, password: str):
        self.ssid = ssid
        self.password = password

    @staticmethod
    def from_dict(data: dict) -> "WifiConfiguration":
        # {
        #   "default_network": "admin1"
        # }
        if len(data) != 1:
            raise ValueError(
                "malformed wifi configuration, expected {'<ssid>':'<password>'}, received: ",
                data,
            )

        ssid = next(iter(data))
        password = data[ssid]

        return WifiConfiguration(ssid, password)

    def __eq__(self, value):
        return self.ssid == value.ssid and self.password == value.password

    def __ne__(self, value):
        return not self.__eq__(value)
    
    def __str__(self) -> str:
        return f"{self.ssid} {self.password}"
    
    def to_dict(self) -> dict:
        return {self.ssid: self.password}

    def connect_to_wlan(
        self, retry_attempts: int = 10, hostname: str | None = None
    ) -> str:

        wlan = network.WLAN(network.STA_IF)

        if hostname != None:
            network.hostname(hostname)

        wlan.active(True)
        
        # got connection exception here once
        wlan.connect(self.ssid, self.password)
        print("connecting", end="")

        while retry_attempts > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                print("\t")
                break

            retry_attempts -= 1
            print(".", end="")
            time.sleep(1)

        # TODO add more info to this error
        if wlan.status() != 3:
            print("connection status: FAIL")
            raise RuntimeError("network connection failed")

        else:
            status = wlan.ifconfig()
            print("connection status: OK")
            print(f"ip: '{status[0]}' hostname: {network.hostname()}")

            if check_connection():
                print("network connected to the internet: OK")
            else:
                print("network connected to the internet: FAIL")

            return status[0]


def get_wifi_info() -> list[WifiConfiguration]:
    wifi_config = []
    # TODO improve error description
    try:
        with open("wifi_config.json", "r") as file:
            wifi_config = json.loads(file.read())
            print(f"loaded wifi config: {wifi_config}")

    except Exception as err:
        print("wifi_config.json file error")
        raise Exception("wifi_config.json file error")

    try:
        wifi_list = [WifiConfiguration.from_dict(wifi) for wifi in wifi_config]
    except ValueError as err:
        print(f"wifi configuration error: {str(err)}")
            
    return wifi_list


def save_wifi_info(
    current_config: WifiConfiguration, wifi_config: list[WifiConfiguration]
):

    new_config = [current_config]
    new_config_dict = [current_config.to_dict()]

    for wifi in wifi_config:
        if wifi != current_config:
            new_config.append(wifi)
            new_config_dict.append(wifi.to_dict())

    if all([new == old for new, old in zip(new_config, wifi_config)]):
        print("wifi_config is already up to date")
        return

    # TODO improve error description
    try:
        print("updating wifi_config file")
        with open("wifi_config.json", "w") as file:
            file.write(json.dumps(new_config_dict))
            file.flush()
        return
    except Exception:
        print("wifi_config.json file error")
        raise Exception("wifi_config.json file error")


def connect_to_wifi(hostname: str | None = None) -> tuple[str, WifiConfiguration]:
    wifi_list = get_wifi_info()

    for config in wifi_list:
        try:
            print(f"connecting to wifi: '{config.ssid}', password: '{config.password}'")

            ip = config.connect_to_wlan(hostname=hostname)

            save_wifi_info(config, wifi_list)
            return ip, config

        except Exception as err:
            print(err)
            continue

    raise RuntimeError("network connection failed")


def check_connection(url: str = "https://www.google.com/") -> bool:

    try:
        requests.get(url=url, timeout=2)
        # we don't care whether response status is 200
        return True
    except Exception as ex:
        print(f"failed to reach {url}, error: {str(ex)}")
        # mainly catching [Errno 110] ETIMEDOUT
        return False
