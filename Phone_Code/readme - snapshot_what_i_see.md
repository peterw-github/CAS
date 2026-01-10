# 📱 Pixel 9 Wireless Camera Automation

**Project:** `see_what_i_see_.py`

**Description:** A Python tool that wirelessly connects to a Google Pixel 9, records a 5-second wide-angle video, and automatically transfers the file to a PC without USB cables. The phone must be UNLOCKED for this program to work.

* * *

## 🚀 How It Works

1.  **Wireless Connection:** The script connects to the phone over Wi-Fi using ADB (Android Debug Bridge) on a specific Static IP.
    
2.  **File Inventory:** It scans the camera folder _before_ recording to take a "snapshot" of existing files.
    
3.  **Automated Recording:**
    
    -   Wakes the phone.
        
    -   Launches the Camera app in Video mode.
        
    -   Switches to the **0.5x Wide Lens** (using coordinate `1550, 630`).
        
    -   Records for 5 seconds.
        
    -   Taps the "Save/Tick" button (using coordinate `1850, 553`).
    
4.  **Smart Retrieval:** It scans the folder again, detects the **new** file (ignoring old or randomly named files), and pulls it to the PC.
    

* * *

## 🛠️ Prerequisites & Setup

### 1\. Computer Requirements

-   **Python 3.x**
    
-   **ADB Tools:** You must have the Android SDK Platform Tools installed.
    
    -   _Current Path:_ `D:\CAS\Phone_Code\android_sdk_platform_tools\adb.exe`
        

### 2\. Phone Configuration (Pixel 9)

The phone requires specific network settings to ensure the script can always find it.

-   **Developer Options:** Enabled (`Settings > About Phone > Tap 'Build Number' 7 times`).
    
-   **USB Debugging:** ON.
    
-   **Wireless Debugging:** ON (Optional, but good for troubleshooting).
    

### 3\. Network Configuration (Static IP)

To prevent the router from changing the phone's address, the Pixel 9 is set to a **Static IP**.

-   **Go to:** `Settings > Network > Internet > [Your Wi-Fi] > Edit (Pencil) > Advanced`
    
-   **IP Settings:** `Static`
    
-   **IP Address:** `192.168.0.235` (Target IP)
    
-   **Gateway:** `192.168.0.1`
    
-   **Subnet Mask:** `255.255.255.0` (Prefix length: 24)
    
-   **DNS:** `192.168.0.1` (or `8.8.8.8`)
    

* * *

## ⚠️ Important: The "Reboot Rule"

**If the phone runs out of battery or reboots, Wireless ADB will stop working.**

To fix this, you must perform the **"One-Time Setup"** again:

1.  Plug the phone into the PC via USB.
    
2.  Open a terminal/command prompt.
    
3.  Run: `adb tcpip 5555`
    
4.  Unplug the USB.
    
5.  The script will now work wirelessly again until the next reboot.
    

* * *

## ⚙️ Configuration Variables

If you move folders or change phones, update these variables at the top of `see_what_i_see_.py`:

Python

    # The IP address we locked in the phone settings
    PHONE_IP = "192.168.0.235"  
    
    # Where adb.exe lives on your computer
    ADB_PATH = r"D:\CAS\Phone_Code\android_sdk_platform_tools\adb.exe"
    
    # Where to save the videos on your PC
    PC_DESTINATION_FOLDER = r"D:\CAS\Phone_Code\Recordings"
    
    # Landscape Coordinates (Pixel 9 Specific)
    COORD_WIDE_LENS = "1550 630"
    COORD_SAVE_TICK = "1850 553"

* * *

## ❓ Troubleshooting

**Error: "Target machine actively refused it" or "Connection failed"**

-   **Cause:** The phone likely rebooted, or Wi-Fi was toggled off/on, resetting the ADB listener.
    
-   **Fix:** Plug in via USB and run `adb tcpip 5555`.
    

**Error: "No new file detected"**

-   **Cause:** The recording didn't save, or the "Save/Tick" button wasn't tapped correctly.
    
-   **Fix:** Check if the phone rotated. The coordinates `1550 630` are hardcoded for **Landscape** orientation. Ensure the phone is physically in landscape mode before running.
    

**Error: "Device offline"**

-   **Cause:** The phone screen might be off for too long, causing Wi-Fi to sleep.
    
-   **Fix:** Wake the screen manually or ensure the phone is charging.
    

* * *

### 📝 Coordinate Reference (Pixel 9 / Landscape)

-   **0.5x Zoom:** `1550, 630`
    
-   **Save/Tick:** `1850, 553`
    
-   **Shutter:** Volume Key (`keyevent 24`)