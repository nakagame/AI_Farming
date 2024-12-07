import gpiod
from time import sleep
import spidev


class YL69Controller:
    def __init__(self, pin=22, gpiochip="/dev/gpiochip4", spi_bus=0, spi_device=0, correction=0):
        self.pin = pin
        self.gpiochip = gpiochip
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1350000  # Adjust SPI speed if necessary
        self.correction = correction  # Calibration value
        self.chip = gpiod.Chip(self.gpiochip)  # Use specific gpiochip
        self.line = self.chip.get_line(self.pin)  # Use correct API for gpiod 1.x

        if not self.line:
            raise RuntimeError(f"Failed to find line {self.pin} on chip {self.gpiochip}")

        # Initialize GPIO
        self.line.request(consumer="YL69Controller", type=gpiod.LINE_REQ_DIR_OUT)

    def output_from_gpio(self, output):
        """
        Controls the GPIO pin output (1 or 0).
        """
        self.line.set_value(1 if output else 0)
        sleep(0.1)

    def read_adc(self, channel):
        """
        Reads raw data from the ADC via SPI.
        """
        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1")
        command = 0x68 if channel == 0 else 0x78
        ret = self.spi.xfer2([command, 0x00])
        adcout = ((ret[0] << 8) + ret[1]) & 0x3FF  # 10-bit Data
        return adcout

    def get_corrected_value(self, channel):
        """
        Returns the measured ADC value with correction applied.
        """
        raw_value = self.read_adc(channel)
        if raw_value != -1:
            return raw_value + self.correction
        return raw_value

    def close(self):
        """
        Releases GPIO and SPI resources.
        """
        self.output_from_gpio(False)
        self.spi.close()
        self.line.release()
        self.chip.close()


if __name__ == "__main__":
    sleep_time = 5  # Time between measurements

    # Set a correction value (e.g., to adjust to a reference value)
    correction_value = -98.4  # Sensor calibration
    controller = YL69Controller(pin=22, gpiochip="/dev/gpiochip4", correction=correction_value)

    try:
        controller.output_from_gpio(True)  # Initial GPIO signal
        while True:
            raw_value = controller.read_adc(0)  # Read raw ADC value
            corrected_value = controller.get_corrected_value(0)  # Apply correction
            if raw_value != -1:
                print(f"Raw Sensor Value: {raw_value}, Corrected Sensor Value: {corrected_value}")
            sleep(sleep_time)
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        controller.close()
