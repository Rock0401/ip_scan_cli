# ip_scan_cli
Use redfish command to get the IP you want in Python.
A valid account/password pair is required, which will be used to attempt login to the server.
You can create a "password.txt" in the same directory, and it will attempt to use the PWs listed in it. 
Note1: a maximum of 5 attempts is allowed.(Included the one provided via the command line) Exceeding this limit may result in the server blocking further access(response 401), even if valid credentials are provided afterward.
Note2: Enter one password per line in password.txt (i.e., each password should be separated by a line break).
ex. cat password.txt
123456789
ABCDEFG
PASSWORD
