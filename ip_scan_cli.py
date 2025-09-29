import requests
from bs4 import BeautifulSoup
import urllib3
from requests.auth import HTTPBasicAuth
import concurrent.futures
import time

#disable warning of SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

####################################### Input Function ###########################################
def get_ip_input(prompt, default):
    user_input = input(prompt).strip()
    
    if not user_input:  # default IP
        return default
    
    if user_input.count(".") == 3:  # complete IP
        return user_input
    
    if user_input.isdigit() and 0 <= int(user_input) <= 255:  # host addr only
        return f"10.1.111.{user_input}"
    
    print("Invalid input. Using default IP:", default)
    return default

def get_limited_input(prompt, max_value, default_value):
    try:
        value = float(input(prompt))
        if value > max_value:
            print(f"The number exceeds {max_value}, using the default value {default_value}.")
            return default_value
        return value
    except ValueError:
        return default_value
####################################### Banner Function ###########################################
def print_banner():
    banner_text = [
        "IP Scanning Tool",
        "",
        "This tool retrieve device via Redfish API with the provided username and password.",
        "Press Enter to use default (admin,password)",
        "",
        "IP range:",
        "Starting IP can be full IP (e.g., 10.2.1.1) or last octet (e.g., 1 for 10.1.111.1) (default:2)",
        "Ending IP should be the last octet (1 to 254, default:254)",
        "",
        "For any issues, please contact Rock",
    ]
    """
        "",
        "Timeout:",
        "set to 0.5 seconds for faster scans (may miss some responses sometimes).",
        "set to 1 seconds for more stability (slower).",
    """
    max_length = max(len(line) for line in banner_text)
    print("*" * (max_length + 4))
    for line in banner_text:
        print(f"* {line.ljust(max_length)} *")
    print("*" * (max_length + 4) ,"\n")

####################################### Scan Function ###########################################
def scan_ip(target_ip, username, password, timeout, password_list):
    target_url = f"http://{target_ip}/redfish/v1/Chassis/1"

    try_passwords = [password] + password_list.copy()
    for pw in try_passwords:
        try:
            response = requests.get(target_url, auth=HTTPBasicAuth(username,pw), verify=False, timeout=float(timeout))
            #verify=False to disable SSL warning/error
            if response.status_code == 200:

                chassis_data = response.json()
                model = chassis_data.get("Model", "No Model column")
                sn = chassis_data.get("Oem", {}).get("GBTChassisOemProperty", {}).get("Board Serial Number", "No SerialNumber column")
                print(f"IP:{target_ip.ljust(20)} {model.ljust(30)}"+f"SN:{sn.ljust(25)}")
                if model=="No Model column":
                    continue
                return target_ip, model, sn
            elif response.status_code == 401:
                time.sleep(0.2)
        except requests.exceptions.RequestException as e:
            continue
        except KeyboardInterrupt:
            print("\nUser interrupted the program. Exiting gracefully.")
        time.sleep(0.05)
    return target_ip, "Cannot connect.", "N/A"
        
####################################### Load password.txt Function ###########################################
def load_password_list(file_path="password.txt"):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Password file not found. Skipping alternate password attempts.")
        return []

####################################### Main Function ###########################################
def main():
    try:
        valid_ip = []
        print_banner()
        username=input("Please enter username (default: admin, press enter):") or "admin"
        password=input("Please enter password (default: password):") or "password"
        
        scan_ip_start=get_ip_input(("Please enter starting IP for scan range (default: 2):"), "10.1.111.2")
        scan_ip_end=int(get_limited_input("Please enter ending IP for scan range (default: 254, last octet only):",254,254))
        #timeout=float(get_limited_input("Please enter timeout (default: 0.6):",10,0.6) or 0.6)
        timeout=0.6
        
        password_list = load_password_list()
        print("Passwords:",password_list)

        #handling input for IP range
        parts=scan_ip_start.split(".")
        network_addr=".".join(parts[:3]) +"."
        scan_start=int(parts[3])
        ip_range=[f'{network_addr}{i}' for i in range(scan_start,int(scan_ip_end)+1)]
        print("Scanning IP:",ip_range[0],"to",ip_range[-1],"......")
        print(" ")
        #Start scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor: #using ThreadPoolExecutor for faster scan
            results=executor.map(lambda ip: scan_ip(ip,username,password,timeout,password_list),ip_range)
            for target_ip,model,sn in results:
                if model != "Cannot connect." and model != "Login Fail":
                    valid_ip.append((target_ip,model,sn))
        #for ip,model,sn in valid_ip:          #print the result in order
        #    print(f"IP:{ip.ljust(20)} {model.ljust(30)}"+f"SN:{sn.ljust(25)}")
        print("Found",len(valid_ip),"devices")
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\nUser interrupted the program. Exiting gracefully.")
if __name__ == "__main__":
    main()