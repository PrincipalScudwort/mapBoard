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

def sparkle(strip):
    """Fast and sparkly red, white, and blue pattern."""
    for i in range(100):  # number of sparkles
        i = random.randint(0, strip.numPixels()-1)
        if i % 3 == 0:
            strip.setPixelColor(i, Color(255,0,0))  # red
        elif i % 3 == 1:
            strip.setPixelColor(i, Color(255,255,255))  # white
        else:
            strip.setPixelColor(i, Color(0,0,255))  # blue
        strip.show()
        time.sleep(0.01)  # fast change
        strip.setPixelColor(i, Color(0,0,0))  # turn off

def handle_client(conn, addr):
    # Define color mapping
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


            if 0 <= num <= 399:
                strip.setPixelColor(num, Color(*color))
                strip.show()
            elif num == 500:
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, Color(0,0,0))
                strip.show()
            elif num == 501:
                rainbow(strip)

            elif num == 502:
                sparkle(strip)
                    
    conn.close()


def start_server():
    server_ip = '192.168.1.113'  # This should be the IP of the receiving Pi
    server_port = 50000  # This should match the port on the sending Pi

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
