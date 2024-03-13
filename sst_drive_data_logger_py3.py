# This script uses Python 3 to run `py .\sst_drive_data_logger_py3.py`
import csv  # To write to a CSV file for logging drive data
import ctypes  # To run as administrator: ctypes.windll.shell32.ShellExecute
import json  # To convert a dictionary to a JSON string
import logging  # To log messages to the console
import os  # To execute shell commands
import subprocess  # To run shell commands
import sys  # To exit the program
import time  # To use time.sleep

# format for logging messages to the console
FORMAT = '[%(asctime)s]-[%(funcName)s]-[%(levelname)s] - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=FORMAT
)  # configure logging messages to the console with the format specified above


class BootDriveInformation:
    """A class that contains the information of the boot drive."""

    def __init__(self) -> None:
        text = TerminalTextColorsAndStyles()
        self.SERIAL_NUMBER: str = "21314E804991"
        logging.info("Boot Drive Serial Number: " +
                     text.yellow +
                     self.SERIAL_NUMBER +
                     text.reset)
        logging.info("This drive will be skipped in terminal and logging")

    def get_serial_number(self) -> int:
        """Return the serial number of the boot drive."""
        return self.SERIAL_NUMBER


class SstRunner:
    """
    A class that handles SST commands and ensures that the program can run
    """

    def __init__(self) -> None:
        self._check_program_is_in_admin_mode()
        self.sst_show_ssd_output: dict = json.loads(
            os.popen("sst show -output json -ssd").read())

    def get_sst_show_ssd_output(self) -> dict:
        """Return the output of the `sst show -output json -ssd` command."""
        return self.sst_show_ssd_output

    def _check_program_is_in_admin_mode(self) -> None:
        """Check if the program is running in admin mode."""
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.info("Please run this script in admin mode.")
            self._exit_program()

    def _exit_program(self) -> None:
        """
        Log a message to the console that the program is exiting
        and exits the program.
        """
        logging.info(
            self.text.red +
            "Exiting program" +
            self.text.reset
        )
        for i in range(3, 0, -1):  # Exit the program with a countdown seconds
            print("Exiting in {} seconds...".format(int(i)))
            time.sleep(1)

        sys.exit(0)  # exit the program (0 means success - no errors)


class DriveDataToTerminal:
    """A class that logs the drive data of the SSDs in the
    system to the console and to a log file.
    """

    def __init__(self):
        self.text = TerminalTextColorsAndStyles()
        self.bootDrive = BootDriveInformation()
        self.sst_show_ssd_output = SstRunner().get_sst_show_ssd_output()

    def run(self) -> None:
        """Run the DriveDataToTerminal."""
        self._print_drive_data_to_screen()

    def _print_drive_data_to_screen(self) -> None:
        """Log the drive data of the SSDs in the system."""
        print()  # Add a newline for readability
        for drive_id, drive_data in self.sst_show_ssd_output.items():
            if drive_id == self.bootDrive.get_serial_number():
                continue  # Skip this drive and go to the next iteration

            print("Index:", drive_data["Index"])
            print("Serial Number (SN):",
                  self._highlight_manufacturer_date_and_counter(
                      drive_data["SerialNumber"])
                  )
            print("Model Number (MN):", drive_data["ModelNumber"])
            print("Firmware Version:", drive_data["Firmware"])
            print("Device Status:", self._drive_health_check(
                drive_data["DeviceStatus"])
            )
            print()  # Add a newline for readability

    def _highlight_manufacturer_date_and_counter(self,
                                                 serialNumber: str) -> str:
        """
        Highlight the manufacturer date and counter of the serial number.

        Args:
            serialNumber (str): The serial number of the drive to highlight

        Returns:
            str: The highlighted manufacturer date and counter
                of the serial number

        Source: https://npsg-wiki.elements.local/display/NCAT/Serial+Number#SerialNumber-Decoding
        """
        vendor_site = serialNumber[0:2]  # VS
        product_identifier = serialNumber[2:4]  # PP
        year_workweek_day = serialNumber[4:8]  # YWWD
        counter = serialNumber[8:12]  # SSSS
        drives_capacity = serialNumber[12:15]  # NNN
        form_factor = serialNumber[15]  # F
        case_serial_indicator = serialNumber[16:18]  # GN
        highlighted_serial_number = (
            vendor_site +
            product_identifier +
            self.text.fgRed_bgDefault_bold + year_workweek_day + self.text.reset +
            self.text.fgCyan_bgDefault_bold + counter + self.text.reset +
            drives_capacity +
            form_factor +
            case_serial_indicator)

        return highlighted_serial_number

    def _drive_health_check(self, device_status: str) -> str:
        """
        Return green text if the drive is healthy, else return red text.

        Args:
            device_status (str): The status of the drive

        Returns:
            str: The status of the drive with the appropriate color
        """
        colored_text: str = self.text.fgWhite_bgRed_bold +\
            device_status +\
            self.text.reset

        if device_status == "Healthy":
            colored_text = self.text.fgWhite_bgGreen_bold +\
                device_status +\
                self.text.reset

        return colored_text


class DriveDataToLogFile:
    """
    A class that logs the drive data of the SSDs in the system a log file.
    """

    def __init__(self):
        self.bootDrive = BootDriveInformation()
        self.text = TerminalTextColorsAndStyles()
        self.sst_show_ssd_output = SstRunner().get_sst_show_ssd_output()
        self.DESKTOP = os.path.normpath(
            os.path.join(os.path.join(
                os.environ['USERPROFILE']),
                "OneDrive - NANDPS",
                'Desktop'
            )
        )  # Provide path, regardless of OS, to desktop location
        self.log_file_name = "Nutanix_SST_Drive_Log.csv"
        self.headers = [
            "Model",
            "Serial",
            "Firmware",
            "Device_Status"
        ]

    def run(self) -> None:
        """Run the DriveDataToLogFile."""
        self._create_log_files()  # Create the log files if they do not exist
        logging.info(
            "Writing to log file: " +
            self.text.yellow +
            self._get_log_file_path()
            + self.text.reset
        )

        for drive_id, drive_data in self.sst_show_ssd_output.items():
            if drive_id == self.bootDrive.get_serial_number():
                continue
            self._write_to_log_file(
                self._get_log_file_path(),
                drive_data
            )

        logging.info("Drive's basic properties written to log file.")

    def _get_log_file_path(self) -> str:
        """Return the path to the log file."""
        return os.path.join(self.DESKTOP, self.log_file_name)

    def _create_log_file_if_not_exists(self, file_path: str) -> None:
        """
        Create the log file if it does not exist; otherwise, do nothing.

        Args:
            - file_path (str): The path to the log file.
        """
        if not os.path.isfile(file_path):
            logging.info(
                self.text.bold +
                "Initializing log file, Writing headers." +
                self.text.reset
            )
            logging.info("Log file created")
            with open(file_path, 'a', newline='') as file_handle:
                csv_writer = csv.writer(file_handle)
                csv_writer.writerow(self.headers)

    def _create_log_files(self) -> None:
        """Create the log file if they do not exist."""
        self._create_log_file_if_not_exists(
            self._get_log_file_path())

    def _write_to_log_file(
            self,
            log_file_path: str,
            sst_json_output: dict) -> None:
        """
        Write the device information to the log file.

        args:
            - log_file_path (str): The path to the log file.
            - sst_json_output (dict): SST JSON output as a dictionary.
        """
        with open(log_file_path, 'a', newline='') as file_handle:
            csv_writer = csv.writer(file_handle)
            try:
                data_row: list = [
                    sst_json_output["SerialNumber"],
                    sst_json_output["ModelNumber"],
                    sst_json_output["Firmware"],
                    sst_json_output["DeviceStatus"]
                ]
                csv_writer.writerow(data_row)
            except Exception as e:
                logging.error("Error writing to log file: {}".format(str(e)))
                logging.warning("Log may have not been updated")


class TerminalTextColorsAndStyles:
    """A class that contains terminal text colors and styles."""
    # Cyan text with default background and bold
    fgCyan_bgDefault_bold: str = "\033[36;49;1m"
    # Red text with default background and bold
    fgRed_bgDefault_bold: str = "\033[31;49;1m"
    # White text with default background and bold
    fgWhite_bgDefault_bold: str = "\033[37;49;1m"
    # White text with green background and bold
    fgWhite_bgGreen_bold: str = "\033[37;42;1m"
    # White text with red background and bold
    fgWhite_bgRed_bold: str = "\033[37;41;1m"
    green: str = "\033[92m"  # Green text
    red: str = "\033[91m"  # Red text
    reset: str = "\033[0m"  # Reset text color and style
    yellow: str = "\033[93m"  # Yellow text
    bold: str = "\033[39;49;1m"  # Bold text


def main():
    """The main function of the program."""
    log_to_terminal = DriveDataToTerminal()
    write_to_log_file = DriveDataToLogFile()
    text = TerminalTextColorsAndStyles()
    logging.info("Starting SST Drive Data Logger...")
    log_to_terminal.run()
    write_to_log_file.run()

    while True:
        host_power_off = input(
            text.yellow +
            "Would you like to power off the system? " +
            text.reset +
            text.green + "Yes " + text.reset +
            "(y)" + " or " +
            text.red + "No " + text.reset +
            "(n): "
        )
        if host_power_off.lower() == "y":
            logging.info(
                text.fgRed_bgDefault_bold +
                "Shutting down the system..." +
                text.reset
            )
            time.sleep(2)
            subprocess.run(["shutdown", "/s", "/t", "0"])
            break
        elif host_power_off.lower() == "n":
            logging.info(text.yellow +
                         "System will not be powered off." +
                         text.reset
                         )
            logging.info(text.yellow + "Exiting program..." + text.reset)
            break
        else:
            logging.warning(
                "Invalid input" + ". " + "Please enter " + text.green +
                "Yes " + text.reset + "(y)" + " or " + text.red + "No " +
                text.reset + "(n): "
            )


if __name__ == "__main__":
    main()
