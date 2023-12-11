# mapBoard
system to control a mapboard representation of a fire district that has individually addressable LEDs to visualize the streets and directions
DEMONSTRATION: https://youtu.be/FvZrN3xapdo?si=dUIu3jxZL_uSa9R8

Each folder represents the script that is running on an indiviudal raspberry pi to make up the entire system. This approach was chosen to make the entire system more modular and isolate any potential faults. 
For example, if the raspberry pi that parses the real time dispatch reports were to fail, the raspberry pi that serves as the LED controller can still communicate with the touch screen controller and that part of the system will continue to work. 
Also any additional means to communicate with the LED controller pi can be added to the network. For example, you could create a phone app to control the lights and it would not require any hardware or software changes.
Any device on the same network can communicate with the LED controller pi as long as it knows the ip address and the port that the LED controller pi is listening on. 
Instead of having the system spread across 3 raspberry pis to seperately parse the real time dispatch, manage the touch screen controller and control the LEDs, in theory the seperate scripts can be combined
and a single computer can handle all aspects of the system. This would probably require greater processing power than what a single raspberry pi 4 offers. 

