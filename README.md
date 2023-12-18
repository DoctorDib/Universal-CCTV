PiSecurityCamera
======
One way of protecting my mtorbike from bad drivers or theives!

Why I made it?
------
3rd December 2018... the day of the "strong wind". So I was minding my own business, watching Ant man and wasp until suddenly I heard my motion sensor motorbike alarm go off. I decided to look out of my window to find my motorbike balancing on a black BMW. I rushed outside to find my motoribke laying (left side up) on the floor. At the time everything was going fine, he admitted that it was his fault (with a couple of blames here and there), how he tried to shift to the left allowing the 4x4 to squeeze passed on a **SINGLE lane road**.

I recieved an email from my insurance company a couple of days later saying that the **183KG** motorbike **"blew over in adverse weather conditions"** (**12mph wind** at the time).

I came to the conclusion that I need to make some CCTV for my motorbike, to cover both theft and idiotic drivers.


What I used
------
Hardware:
 - Raspberry Pi 3 b+
 - 30GB SD card
 - Raspberry Pi Camera Module (first version)
 - Raspberry Pi Camera Fish eye Wide Angle Night Vision Camera Module (current version)

Software: 
 - Raspbian Stretch with desktop
 - Python 3







https://linuxhint.com/install-h264-decoder-ubuntu/


Make sure the chosen resolution is compatible with your chosen webcam... spent ages figuring out why it silentely fails writing to a file.
my camera was only compatible for 1440x1080 and not 1920x1080