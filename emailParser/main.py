import time
import csv
import socket
from getMail import get_email_data
from fuzzywuzzy import process

SERVER_IP = '192.168.1.113'  # This should be the IP of the receiving Pi (LED CONTROLLER)
SERVER_PORT = 50000  # Choose a port that is not in use. Receving Pi (LED CONTROLLER) must be listening on the same port

def find_closest_address(location, data):
    # Capitalize the location
    location = location.upper()
    # Extract list of streets for fuzzy matching
    streets = [row[0] for row in data]
    # Using fuzzywuzzy to find the closest match (accounts for spelling errors or abbreviations in dispatches)
    best_match = process.extractOne(location, streets)
    if best_match:
        best_match_name, match_score = best_match
        # Setting threshold for match score
        if match_score > 80:
            # Find the row with the best match
            for row in data:
                if row[0] == best_match_name:
                    return [int(i) for i in row[1].split(', ')]

    return None

def send_message(msg):
    # Server IP and port
    server_ip = SERVER_IP  # This should be the IP of the receiving Pi
    server_port = SERVER_PORT  # Choose a port that is not in use
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            s.sendall(msg.encode())
    except Exception as e:
        print(f'Error occurred while sending message: {msg}. Error: {e}')

def format_message(category, msg):
    # Lowercase the category for case insensitivity
    category = category.lower()

    # Decide the prefix based on the category
    if category == 'fire':
        return f'{msg},RED'
    elif category == 'ems':
        return f'{msg},BLUE'
    else:  # 'info' or any other category
        return f'{msg},GREEN'

def main():
    # Loading the csv file into a list
    #csv file is the list of all addresses and the corresponding LEDs that they light up when chosen
    #same csv file as map1.csv used in the Touch Screen Interface Pi 
    with open('/home/pi/Documents/mapIndex.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    while True:
        #additional logic can be added to utilize the cross street visually (is not currently displayed)
        location, cross_streets, category = get_email_data()
        if location is not None:
            send_message("500,BLK")  # the map board will be cleared of whatever it is currently displaying
            send_message("176,ORANGE") #always light up LED 176 (which is the firehouse) for any call
            closest_address = find_closest_address(location, data) #find the matching street to the recieved address
            if closest_address:
                # For each int (LED) in the list, send a separate message to the server
                # each street may have either 1,2 or 3 LEDs associated with it
                # this loop will walk through each LED associated with the matching street
                for msg in closest_address:
                    #send command to LED Controller PI to light up matching LEDs in the color that corresponds to the nature of the incident
                    formatted_msg = format_message(category, str(msg))
                    send_message(formatted_msg)
        # Wait for 5 seconds (polling time for emails)
        time.sleep(5)

if __name__ == "__main__":
    main()
