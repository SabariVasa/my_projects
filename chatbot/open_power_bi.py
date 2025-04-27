import subprocess
import time
import pyautogui

import os

power_bi_path = "C:\\Users\\DELL\\Microsoft\\Power BI Desktop Store App\\bin"


# Open Power BI Desktop
subprocess.Popen(power_bi_path)

# Wait for Power BI to launch (adjust time if needed)
time.sleep(10)

# Simulate 'Ctrl + N' to create a new blank report
pyautogui.hotkey('ctrl', 'n')

# Wait for the new file to open
time.sleep(5)

# Simulate 'Get Data' shortcut (Alt + D, Enter)
pyautogui.hotkey('alt', 'd')
time.sleep(2)
pyautogui.press('enter')

# Wait for 'Get Data' window
time.sleep(5)

# Type the static file path and press Enter
static_file_path = r"C:\Users\DELL\Downloads"  # Change to your actual file path
pyautogui.write(static_file_path)
time.sleep(2)
pyautogui.press('enter')

print("Power BI opened and data file loaded successfully!")
