import socket
import threading
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 400        # Number of LED pixels.
LED_PIN = 18           # GPIO pin connected to the pixels (must support PWM).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10           # DMA channel to use for generating signal
LED_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift)

SERVER_IP = '192.168.1.113'  # This should be the IP of the receiving Pi (LED CONTROLLER)
SERVER_PORT = 50000  # Choose a port that is not in use. Receving Pi (LED CONTROLLER) must be listening on the same port

# Create the strip object
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Initialize the library (must be called once before other functions)
strip.begin()

def rainbow(strip):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(20/1000.0)


def handle_client(conn, addr):
    # Define color mapping (G,R,B)
    #Can add any additional colors here and create new commands for those colors (i.e 'PURPLE': (0,255,255))
    color_map = {
        'RED': (0, 255, 0),
        'GREEN': (255,0, 0),
        'BLUE': (0, 0, 255),
        'ORANGE': (160, 255, 0),
        'YELLOW': (255, 255, 0),
        'BLK': (0, 0, 0),
        '': (255, 255, 255)  # default color when no color is sent
    }

    print(f'Connection from {addr}')
    while True:
        data = conn.recv(1024)
        if not data:
            break

        print('Received:', data.decode())
        num, color_str = data.decode().split(',')
        
        if num.isnumeric():
            num = int(num)
            color = color_map.get(color_str, (255, 255, 255))  # default color when unrecognized color is sent

            #There are 400 LEDs in the LED strip used in this map board. If the recieved num in the packet is a valid LED index
            #that LED will be lit up in the color from the recieved color command
            if 0 <= num <= 399:
                strip.setPixelColor(num, Color(*color))
                strip.show()
            #If recieved number is '500' that is the command to reset all LEDs to off
            elif num == 500:
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, Color(0,0,0))
                strip.show()
            #If recieved number is '501' that is the command for rainbow pattern
            elif num == 501:
                rainbow(strip)           
    conn.close()


def start_server():
    server_ip = SERVER_IP  # The Email Parser and Touch Screen Interface PIs should send packets to this IP address
    server_port = SERVER_PORT  # This should match the port on any senders

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, server_port))
        s.listen()
        print(f'Server listening on {server_ip}:{server_port}')
        while True:
            conn, addr = s.accept()
            # Create a new thread to handle this connection
            threading.Thread(target=handle_client, args=(conn, addr)).start()

# Start the server
start_server()
