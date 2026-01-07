# Voice Bridge (Gboard-to-PC)

**Voice Bridge** is a lightweight Python tool that turns your smartphone into a remote microphone for your computer. It hosts a local web server that captures text input from your phone (specifically optimized for Gboard voice typing) and instantly syncs it to your computer's clipboard.

## 🚀 Features

-   **Zero-Install on Phone:** No app required; works entirely through the mobile browser.
    
-   **Live Sync:** Text is transmitted via local Wi-Fi.
    
-   **Debounce Logic:** Includes a 2-second buffer to prevent rapid clipboard overwrites while dictating.
    
-   **Dark Mode:** The mobile interface is styled for OLED screens/night usage.
    

## 📋 Prerequisites

-   **Computer:** Python 3 installed.
    
-   **Phone:** A modern mobile browser (Chrome/Firefox) and Gboard (or any voice-to-text keyboard).
    
-   **Network:** Both devices must be connected to the **same Wi-Fi network**.
    

## 🛠️ Installation

1.  **Install Dependencies:** Open your terminal or command prompt and install the required libraries:
    
        pip install flask pyperclip
        
    
2.  **Save the Script:** Save your Python code as `server.py`.
    

## ⚡ Usage

1.  **Start the Server:** Run the script on your computer:
    
        python server.py
        
    
2.  **Connect via Phone:** The script will output a local IP address (e.g., `http://192.168.1.15:5000`). Type this address into your phone's web browser.
    
3.  **Dictate:**
    
    -   Tap the text box on your phone.
        
    -   Tap the **Microphone icon** on Gboard.
        
    -   Start speaking.
        
4.  **Paste:** Once you stop speaking for **2 seconds**, the text will sync. Press `Ctrl + V` on your computer to paste the text.
    

## ⚙️ Configuration Details

**The "Debounce" Timer** The script is currently set to a **2000ms (2 second)** delay.

-   **How it works:** The script waits for you to stop typing/speaking for 2 full seconds before sending the text to the PC.
    
-   **Why:** This prevents the PC clipboard from updating aggressively after every single word, which allows for smoother dictation of long paragraphs.
    
-   **To Change:** Edit the `setTimeout(..., 2000)` value in the HTML/JavaScript section of `server.py`.
    

## 🔧 Troubleshooting

**"I can't load the website on my phone"**

-   **Firewall:** Windows Firewall often blocks Python from accepting incoming connections.
    
    -   _Fix:_ When you first run it, a popup should appear. Ensure you check **"Allow access"** for **Private Networks**.
        
    -   _Manual Fix:_ Go to Windows Defender Firewall > Allow an app through firewall > Add `python.exe`.
        
-   **IP Address:** If the printed IP doesn't work, open Command Prompt and type `ipconfig`. Look for the IPv4 address of your Wi-Fi adapter.
    

**"The microphone button is grayed out"**

-   Modern browsers sometimes block microphone access on "insecure" (HTTP) sites. However, they usually make an exception for local IP addresses. If this happens, check your mobile browser's site settings to allow microphone access for this IP.
    

## 📄 License

Open source. Feel free to modify and hack away.

