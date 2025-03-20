=====================================================================================================================
ARDUINO:

Using ESP 32 Camera module

The webserver code and dependencies can be directly downloaded from the arduino IDE. (i used ide version 1.8.18):

    In arduino IDE: file -> preferences, then add these to board manager:
    https://dl.espressif.com/dl/package_esp32_index.json
    https://arduino.esp8266.com/stable/package_esp8266com_index.json

    Then tools -> board manager and install esp32
    Then file -> examples -> esp32 -> camera -> camera web server


the camera module has to be wired to programming mode before can be programmed. putting schematic in arduino folder

before programming, in tools in ide, 
board: esp32 wrover module
falsh mode: QIO
partition scheme: huge app
flash freq: 40 MHz
upload speed: 115200 (if no work decrease)
core debug level: none
programmer: avr isp

=====================================================================================================================

JETSON:

In the tx2 desktop folder, there is a file called "Capstone". In it there is a file called Steps.
I believe if you run the second docker run, it should put you in the python 3.6.9 environment. 
If not, run the first docker command and follow the steps for all the dependencies.

In the CapsoneN folder in desktop is where I put the models and other files.

To train a model on the txt2, try this:

run this in a new dir:

    from roboflow import Roboflow
    rf = Roboflow(api_key="q304tLQrZXRtpUb7BCw1")
    project = rf.workspace("team1-0gplr").project("flower-classification-gsskn")
    dataset = project.version(2).download("yolov5")

Then in the terminal cd to the yolov5 folder and run:

python train.py --img 640 --batch 16 --epochs 100 --data /datasets/Flower-Classification-2/data.yaml --weights yolov5s.pt
run with --cache False if running into space issues (will take a lot longer) or try making space in the tx2. 

no guarantee this will work. might have to 

======================================================================================================================

PC (py 3.11):

I got everything to work from my computer. Worst case scenario we will have to run the model off someone's computer.
probably wont need to do this tho

======================================================================================================================

im only putting the relevant code in here. the trained models, dataset, and other project files are too big.