import time
import csv
import socket
import logging
from getMail import get_email_data
from fuzzywuzzy import process

# Set up logging
logging.basicConfig(filename='/home/pi/Documents/app.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

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
                    logging.info(f'Best match found: {best_match_name} with score: {match_score}')
                    return [int(i) for i in row[1].split(', ')]

    logging.info('No suitable match found.')
    return None

def send_message(msg):
    # Server IP and port
    server_ip = '192.168.1.113'  # This should be the IP of the receiving Pi
    server_port = 50000  # Choose a port that is not in use

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            s.sendall(msg.encode())
        logging.info(f'Message sent: {msg}')
    except Exception as e:
        logging.error(f'Error occurred while sending message: {msg}. Error: {e}')

def main():
    # Loading the csv file into a list
    with open('/home/pi/Documents/mapIndex.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    while True:
        location, cross_streets, category = get_email_data()
        if location is not None:
            logging.info(f'Location received: {location}')
            send_message("500")  # Sending "500" for each location received
            closest_address = find_closest_address(location, data)
            if closest_address:
                # For each int in the list, send a separate message to the server
                for msg in closest_address:
                    send_message(str(msg))

        # Wait for 5 seconds
        time.sleep(5)

if __name__ == "__main__":
    main()
