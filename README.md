# SST Drive Data Logger User Guide

Script to pull basic info on Intel/Solidigm and displays to the terminal and/or saves to a log file.

Link to SST User Guide (listed under "Documents"): <https://www.solidigm.com/support-page/drivers-downloads/ka-00085.html>

## Set-up

1. Have Solidigm Storage Tool (SST) installed: [link to SST download page](https://www.solidigm.com/support-page/drivers-downloads/ka-00085.html)
2. Use [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=en-US&gl=US) NOT the "Command Prompt" exe
   1. If using Windows 11 this maybe installed already and is named, simply, "Terminal"
3. Have Python installed [Download the latest version for Windows](https://www.python.org/downloads/)
   1. Verify that Python is installed: `python --version` or `py --version`
      1. You should have Python 3.8 or higher installed

## Running the script

1. Open the "Terminal" app in Admin mode (i.e. `Run as administrator`)
2. Navigate to the directory of [sst_drive_data_logger_py3.py](sst_drive_data_logger_py3.py)
   1. In the command line prompt type: `cd <FOLDER_PATH_TO_sst_drive_data_logger_py3.py>`
3. Run the script with the following command: `python sst_drive_data_logger_py3.py` or `py sst_drive_data_logger_py3.py`

## Some insights

Where to start?

Start here

```python
def main():
    """The main function of the program."""
    log_to_terminal = DriveDataToTerminal()
    write_to_log_file = DriveDataToLogFile()
    text = TerminalTextColorsAndStyles()
    logging.info("Starting SST Drive Data Logger...")
    log_to_terminal.run()
    write_to_log_file.run()
```

This is where most of the magic happens...

```python
import json  # To convert a dictionary to a JSON string
import os  # To execute shell commands

# cli: sst show -output json -ssd
sst_show_ssd_output: dict = json.loads(
    os.popen("sst show -output json -ssd").read()
    )

for drive_id, drive_data in sst_show_ssd_output.items():
    print("Drive ID:", drive_id)
    print("Model Number:", drive_data["ModelNumber"])
    print("Serial Number:", drive_data["SerialNumber"])
    print("Capacity:", drive_data["Capacity"])
    print("Device Status:", drive_data["DeviceStatus"])
```
