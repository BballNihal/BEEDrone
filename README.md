Here’s your README with proper formatting while keeping all your content unchanged:  

```md
# BEEDrone Project

---

## **ARDUINO:**

### Using ESP 32 Camera module  

The webserver code and dependencies can be directly downloaded from the Arduino IDE. (I used IDE version **1.8.18**):  

1. **In Arduino IDE:**  
   - Go to **File → Preferences**, then add these to the board manager:  
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     https://arduino.esp8266.com/stable/package_esp8266com_index.json
     ```
   - Then go to **Tools → Board Manager** and install ESP32.  
   - Then go to **File → Examples → ESP32 → Camera → Camera Web Server**.  

2. **The camera module must be wired to programming mode before it can be programmed.**  
   - Schematic is available in the **Arduino folder**.  

3. **Before programming, set these options in Tools in Arduino IDE:**  
   - **Board:** ESP32 Wrover Module  
   - **Flash Mode:** QIO  
   - **Partition Scheme:** Huge App  
   - **Flash Frequency:** 40 MHz  
   - **Upload Speed:** 115200 (if it doesn’t work, decrease it)  
   - **Core Debug Level:** None  
   - **Programmer:** AVR ISP  

---

## **JETSON:**

### **Setup**  
- In the `tx2` desktop folder, there is a file called **Capstone**.  
- Inside it, there is a file called **Steps**.  
- Running the **second docker run command** should put you in the **Python 3.6.9** environment.  
- If not, run the **first docker command** and follow the steps to install all dependencies.  

- The **CapstoneN** folder on the desktop contains the models and other files.  

### **Training a Model on TX2**  

Run this in a new directory:  

```python
from roboflow import Roboflow
rf = Roboflow(api_key="q304tLQrZXRtpUb7BCw1")
project = rf.workspace("team1-0gplr").project("flower-classification-gsskn")
dataset = project.version(2).download("yolov5")
```

Then in the terminal, `cd` to the `yolov5` folder and run:  

```sh
python train.py --img 640 --batch 16 --epochs 100 --data /datasets/Flower-Classification-2/data.yaml --weights yolov5s.pt
```

- Run with `--cache False` if running into **space issues** (will take longer).  
- Alternatively, free up space on the TX2.  
- **No guarantee this will work**, might have to troubleshoot.  

---

## **PC (Python 3.11):**  

- I got everything to work on my **computer**.  
- **Worst-case scenario**, we will have to run the model off someone's PC.  
- **Probably won’t need to do this though.**  

---

## **Repository Note**  

- **Only relevant code** is included here.  
- **Trained models, dataset, and large project files** are **NOT** uploaded due to size constraints.  
```

