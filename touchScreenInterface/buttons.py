import csv
import tkinter as tk
from tkinter import ttk
import socket

# Define a color state variable
color_state = 'RED'

def send_message(msg):
    global color_state  # Use the global color_state

    # Server IP and port
    server_ip = '192.168.1.113'  # This should be the IP of the receiving Pi
    server_port = 50000  # Choose a port that is not in use

    # Append the color state to the message
    msg = msg + ',' + color_state

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        s.sendall(msg.encode())

def button_action(nums):
    # split the numbers and send each one
    for num in nums.split(","):
        send_message(num.strip())

def change_color_state(new_color_state):
    global color_state
    color_state = new_color_state

def main():
    # read CSV
    with open('map1.csv', 'r') as file:
        reader = csv.reader(file)
        data = {rows[0]:rows[1] for rows in reader}

    root = tk.Tk()
    root.title("CSV Buttons")
    root.attributes('-fullscreen', True)  # make it start in fullscreen

    # create main frame and canvas
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    my_canvas = tk.Canvas(main_frame)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # create a custom style for the buttons
    style = ttk.Style()
    style.configure("Red.TButton", foreground="red")
    style.configure("Blue.TButton", foreground="blue")
    style.configure("Green.TButton", foreground="green")

    # add the color buttons
# add the color buttons
    red_button = ttk.Button(main_frame, text="RED", command=lambda: change_color_state('RED'), style="Red.TButton")
    red_button.pack(side=tk.TOP)
    blue_button = ttk.Button(main_frame, text="BLUE", command=lambda: change_color_state('BLUE'), style="Blue.TButton")
    blue_button.pack(side=tk.TOP)
    green_button = ttk.Button(main_frame, text="GREEN", command=lambda: change_color_state('GREEN'), style="Green.TButton")
    green_button.pack(side=tk.TOP)

    # rest of the code...
    # read CSV
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # create a custom style for the buttons

    # create a custom style for the scrollbar
    style.configure("Custom.Vertical.TScrollbar", width=110)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=my_canvas.yview, style="Custom.Vertical.TScrollbar")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # configure the canvas
    my_canvas.configure(yscrollcommand=scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    second_frame = ttk.Frame(my_canvas)

    # add second_frame to canvas
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    # add buttons dynamically based on csv content
    for i, (key, value) in enumerate(data.items()):
        if i == 0:
            button = ttk.Button(second_frame, text=key, command=lambda value=value: button_action(value), style="Red.TButton")
        else:
            # button = ttk.Button(second_frame, text=key, command=lambda value=value: button_action(value), padx=20, pady=20)
            button = ttk.Button(second_frame, text=key, command=lambda value=value: button_action(value))
        button.grid(row=i//3, column=i%3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)

    # Use grid_configure to make buttons expand and be centered
    for i in range(3):
        second_frame.grid_columnconfigure(i, weight=1)
        second_frame.grid_rowconfigure(i, weight=1)

    # Add an 'Exit' button
    exit_button = ttk.Button(second_frame, text="Exit", command=root.destroy, style="Red.TButton")
    exit_button.grid(row=len(data)//3+1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
