import json
import os
import subprocess
import time
import requests
from glob import glob

XRAY_PATH = "/Users/taesiri/Downloads/XRAY/xray"

def modify_config_and_run_xray(file_path, new_port):
    # Load the JSON config
    with open(file_path, "r") as f:
        config = json.load(f)

    # Modify the port
    for inbound in config["inbounds"]:
        if inbound["port"] == 10808:
            inbound["port"] = new_port

    # Save the modified config to a temp file
    temp_path = os.path.join(os.path.dirname(file_path), "temp_config.json")
    with open(temp_path, "w") as f:
        json.dump(config, f)

    # Run xray in the background using the specified path and return the process
    process = subprocess.Popen([XRAY_PATH, "-c", temp_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return temp_path, process

def speed_test(proxy_port):
    proxies = {
        "http": f"socks5://127.0.0.1:{proxy_port}",
        "https": f"socks5://127.0.0.1:{proxy_port}",
    }
    url = "https://github.com/taesiri/dummy/raw/master/random_25MB.dat"
    
    try:
        start_time = time.time()
        response = requests.get(url, proxies=proxies, stream=True, timeout=30)
        total_time = time.time() - start_time

        if len(response.content) == 25 * 10**6:
            speed = (25 * 10**6) / total_time
            return speed
        else:
            return None
    except requests.RequestException as e:
        print(f"Error downloading with proxy on port {proxy_port}: {e}")
        return None

if __name__ == "__main__":
    # Get all JSON config files but exclude the 'temp_config.json' files
    config_files = [f for f in glob("./*.json") if "temp_config" not in f]
    speeds = {}
    processes = []

    for file_path in config_files:
        new_port = 10808 + config_files.index(file_path)
        temp_config_path, xray_process = modify_config_and_run_xray(file_path, new_port)
        processes.append(xray_process)

        # Wait a bit to ensure xray has started
        time.sleep(5)

        download_speed = speed_test(new_port)
        if download_speed:
            speeds[file_path] = download_speed

        # Cleanup: Stop xray and remove temp config
        xray_process.terminate()
        os.remove(temp_config_path)
        time.sleep(2)

    # Print speeds
    for config, speed in speeds.items():
        print(f"Config: {config}, Speed: {speed} bytes/sec")
