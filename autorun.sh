
#!/bin/sh

sleep 5
python3 -u /home/pi/CameraSurveillance/Camera.py > /home/pi/CameraSurveillance/out.log &

# nano /etc/rc.local
# Add /home/pi/CameraSurveillance/autorun.sh

