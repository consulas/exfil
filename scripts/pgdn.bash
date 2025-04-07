#!/bin/bash
# sudo apt-get install xdotool

# Wait for 5 seconds to allow the user to focus the desired window
sleep 5

# Infinite loop to send Page Down every 250 milliseconds
while true; do
    xdotool key Page_Down
    sleep 0.25
done
