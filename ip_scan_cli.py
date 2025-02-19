import requests
from bs4 import BeautifulSoup
import urllib3
from requests.auth import HTTPBasicAuth
import getpass


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
        return f"10.1.1.{user_input}"
    
    print("Invalid input. Using default IP:", default)
    return default

####################################### Banner Function ###########################################
def print_banner():
    banner_text = [
        "IP Scanning Tool",
        "",
        "Attempts to retrieve device info using Redfish API with the username and password provided.",
        "Press Enter to use default (admin,password)",
        "",
        "IP range",
        "Starting IP can be complete IP (e.g., 10.2.1.1) or host addr (1->10.1.111.1) (default:10.1.111.100)",
        "Ending IP can only be host addr (1 to 254, default:200)",
        "",
        "Timeout",
        "set to 0.2 seconds may sometimes fail to receive some responses",
        "set to 0.5 seconds will be more stable but slower",
        "For any issues, please contact Rock (rock.shih0401@gmail.com)",
    ]

    max_length = max(len(line) for line in banner_text)
    print("*" * (max_length + 4))
    for line in banner_text:
        print(f"* {line.ljust(max_length)} *")
    print("*" * (max_length + 4) ,"\n")

####################################### Main Function ###########################################

try:
    valid_ip = []
    print_banner()
    username=input("Please enter username(default: admin, press enter):") or "admin"
    password=input("Please enter password(default: password):") or "password"

    scan_ip=(get_ip_input(("Please enter starting IP for scan range(default: 100):"),"10.1.111.100"))
    scan_end=(input("Please enter ending IP for scan range (default: 200, host address only):")) or 200
    timeout=(input("Please enter timeout (default: 0.2):")) or 0.2

    parts=scan_ip.split(".")
    network_addr=".".join(parts[:3]) +"."
    scan_start=int(parts[3])
    for i in range(scan_start,int(scan_end)+1):
        target_ip=network_addr+f"{i}"
        target_url = f"http://{target_ip}/redfish/v1/Chassis/1"

        try:
            response = requests.get(target_url, auth=HTTPBasicAuth(username,password), verify=False, timeout=float(timeout))
            #verify=False to disable SSL warning/error

            print(target_url)
            # check if success
            if response.status_code == 200:
                chassis_data = response.json()
                model = chassis_data.get("Model", "no Model column")
                print(f"Model: {model}")
                if(model):
                    valid_ip.append((target_ip, model))  # add to result
            else:
                print("Login Fail")
        except requests.exceptions.RequestException:
            print(f"{target_ip} cannot connnect with the account you provided")
    print(" ")
    for ip,model in valid_ip:
        print(f"IP:{ip}-> {model}")
    input("Press Enter to exit...")
except KeyboardInterrupt:
    print("\nUser interrupted the program. Exiting gracefully.")
