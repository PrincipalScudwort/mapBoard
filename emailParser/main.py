import time
import csv
import socket
from getMail import get_email_data
from fuzzywuzzy import process

def find_closest_address(location, data):
    # Capitalize the location
    location = location.upper()

    # Extract list of streets for fuzzy matching
    streets = [row[0] for row in data]

    # Using fuzzywuzzy to find the closest match
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
    server_ip = '192.168.1.113'  # This should be the IP of the receiving Pi
    server_port = 50000  # Choose a port that is not in use

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
    with open('/home/pi/Documents/mapIndex.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    while True:
        location, cross_streets, category = get_email_data()
        if location is not None:
            send_message("500,BLK")  # Sending "500" for each location received
            send_message("176,ORANGE")
            closest_address = find_closest_address(location, data)
            if closest_address:
                # For each int in the list, send a separate message to the server
                for msg in closest_address:
                    formatted_msg = format_message(category, str(msg))
                    send_message(formatted_msg)

        # Wait for 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    main()
