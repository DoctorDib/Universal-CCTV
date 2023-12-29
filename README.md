# Universal CCTV: Your Personal Surveillance Revolution

Welcome to *Universal CCTV*, an open-source project that empowers you to effortlessly transform any PC, laptop, or Raspberry Pi with a camera into a sophisticated CCTV IP device, offering seamless streaming and recording capabilities.

## Features That Redefine Security:
- Record high-quality videos with ease.
- Stream your camera feed effortlessly over the network.
- Effortlessly view and manage snapshots and recordings within the client interface.

*Compatible with*: Windows, Linux, and Raspberry Pi (Pi camera)

## Effortless Setup for Every Device

### Configuring Your Preferences
Tailoring your preferences is a breeze with *Universal CCTV*. Just follow these steps:
1. Create a new file named `config_custom.json` in the project directory.
1. Mimic the structure of `config_main.readonly.json` and include only the fields/items you wish to customize.

### Raspberry Pi Bliss
#### Our Recommended and Tested Configuration Formats:
- Recording: `h264`
- Streaming: `h264`
- Thumbnails: `jpeg`
- Snapshots: `jpeg`

### Linux: Overcoming Licensing Hurdles
Setting up on non-Windows machines may present some challenges due to licensing issues. Dive deeper into this topic [here](https://www.reddit.com/r/davinciresolve/comments/y4ytkl/why_no_mp4h264_support_on_linux/).

To navigate these challenges:
1. Install the H264 decoder by following these instructions: [Install H264 Decoder on Ubuntu](https://linuxhint.com/install-h264-decoder-ubuntu/)
1. Install Anaconda on Linux with this guide: [Install Anaconda on Ubuntu](https://phoenixnap.com/kb/how-to-install-anaconda-ubuntu-18-04-or-20-04)
1. Create a dedicated environment: `conda create --name UniversalCamera python=3`
1. Activate the environment: `conda activate UniversalCamera`
1. Install essential pip packages: `pip install -r requirements.txt`
1. Secure your setup with necessary Conda packages: `conda install --file condapackage.txt`
Optional:
1. Elevate your experience with VLC for on-device viewing: `sudo apt-get install vlc`

#### Our Recommended and Tested Configuration Formats:
- Codec: `avc1`
- Recording: `mp4`
- Streaming: `jpeg`
- Thumbnails: `jpeg`
- Snapshots: `jpeg`

### Windows: A Seamless Experience
#### Our Recommended and Tested Configuration Formats:
- Codec: `avc1`
- Recording: `mp4`
- Streaming: `jpeg`
- Thumbnails: `jpeg`
- Snapshots: `jpeg`

### Mac: Uncharted Territory
*Not tested / no support*

# Initiating the Surveillance Symphony
Initiating the *Universal CCTV* application is a breeze. Simply execute `python main.py` and witness the transformation of your device into a surveillance powerhouse.

## Crafting the Client Experience
In your terminal, execute `npm run build` to refine the client interface. This step is crucial after any client modifications to ensure a seamlessly integrated and visually appealing user experience.

## Seamless Development Environment

### Server/Python Development
Immerse yourself in the development process with a simple command: `python main.py` in your terminal.

### Client Development: The Art of Refinement
Embark on your client development journey with the following initial setup:
1. Navigate to the Client directory.
2. Execute `npm install -d`.

For an immersive development experience:
1. Open a terminal.
1. Navigate to the Client directory.
1. Execute `npm run start`.
1. Access in web `localhost:3000` 
*Note*: Be sure to use port `3000` as that is the development site if you wish to see live changes.

*Note*: Before committing any client changes, ensure you run `npm run build` to incorporate the changes into the source control.

Remember to choose a camera resolution compatible with your webcam. I learned the hard way that silent failures in writing to a file can often be traced back to a resolution mismatch. In my case, my camera was only compatible with 1440x1080 and not 1920x1080.
