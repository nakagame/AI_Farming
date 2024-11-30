import RPi.GPIO as GPIO
from time import sleep
import spidev


class YL69Controller:
    def __init__(self, pin=22, spi_bus=0, spi_device=0, correction=0):
        self.pin = pin
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1350000  #Adjust SPI speed if necessary
        self.correction = correction  #calibration
        self._initialize_gpio()

    def _initialize_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        GPIO.setup(self.pin, GPIO.OUT)

    def output_from_gpio(self, output):
        GPIO.output(self.pin, output)
        sleep(0.1)

    def read_adc(self, channel):
        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1")
        command = 0x68 if channel == 0 else 0x78
        ret = self.spi.xfer2([command, 0x00])
        adcout = ((ret[0] << 8) + ret[1]) & 0x3FF  # NOTE: 10bit Data
        return adcout

    def get_corrected_value(self, channel):
        """
        Returns the measured value with correction applied
        """
        raw_value = self.read_adc(channel)
        if raw_value != -1:
            return raw_value + self.correction
        return raw_value

    def close(self):
        self.output_from_gpio(False)
        self.spi.close()
        GPIO.cleanup()


if __name__ == "__main__":
    sleep_time = 5  # NOTE: Change sleep time

    # NOTE: Set a correction value (e.g., to adjust to a reference value of 500)
    correction_value = -98.4  # SensorA - calibration
    controller = YL69Controller(pin=22, correction=correction_value)

    try:
        controller.output_from_gpio(True)
        while True:
            raw_value = controller.read_adc(0)  # measured Value
            corrected_value = controller.get_corrected_value(0)  # the measured value with correction
            if raw_value != -1:
                print(f"Raw Sensor Value: {raw_value}, Corrected Sensor Value: {corrected_value}")
                break
            sleep(sleep_time)
    except KeyboardInterrupt:
        # NOTE: Quit::Ctrl+C
        print("Program interrupted by user.")
    finally:
        controller.close()
