import requests
import network
import json
import time


def connect_to_wlan(
    ssid: str, password: str, retry_attempts: int = 10, hostname: str | None = None
) -> str:

    wlan = network.WLAN(network.STA_IF)

    if hostname != None:
        network.hostname(hostname)

    wlan.active(True)
    wlan.connect(ssid, password)

    while retry_attempts > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        retry_attempts -= 1
        print("connecting...")
        time.sleep(1)

    if wlan.status() != 3:
        print("connection failed")
        raise RuntimeError("network connection failed")

    else:

        status = wlan.ifconfig()
        print(f"connection succeeded, ip: '{status[0]}' hostname: {network.hostname()}")

        return status[0]


def get_wifi_info() -> dict:
    wifi_config = {}
    try:
        with open("wifi_config.json", "r") as file:
            wifi_config = json.loads(file.read())
    except Exception as err:
        print("wifi_config.json file not found")
        raise Exception("wifi_config.json file not found")

    return wifi_config


def save_wifi_info(ssid, password, wifi_config):
    if next(iter(wifi_config)) == ssid:
        return

    # FIXME new reconfigured file is not saved to memory
    new_config = {ssid: password}

    for key in wifi_config.keys():
        if key != ssid:
            new_config[key] = wifi_config[key]

    with open("wifi_config.json", "w") as file:
        file.write(json.dumps(new_config))


def connect_to_wifi(hostname: str | None = None) -> str:
    wifi_list = get_wifi_info()
    print(f"loaded wifi list: '{wifi_list}'")

    for key in wifi_list.keys():
        print(f"connecting to wifi: '{key}' with password: '{wifi_list[key]}'")
        try:
            ip = connect_to_wlan(key, wifi_list[key], hostname=hostname)

            if check_connection():
                print("network connected to the internet: OK")
            else:
                print("network connected to the internet: FAIL")

            save_wifi_info(key, wifi_list[key], wifi_list)
            return ip

        except Exception as err:
            print(err)
            continue

    raise RuntimeError("network connection failed")


def check_connection(url: str = "https://www.google.com/") -> bool:
    resp = requests.get(url=url, timeout=2)
    return resp.status_code == 200
