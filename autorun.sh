
#!/bin/sh

sleep 5
python3 -u /home/pi/PiSecurityCamera/Camera.py > /home/pi/PiSecurityCamera/out.log &

# nano /etc/rc.local
# Add /home/pi/PiSecurityCamera/autorun.sh

