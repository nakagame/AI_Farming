from threading import Thread
from humidSensor import YL69Controller
from opticalSensor import OPTICAL
from time import sleep


def run_humid_sensor():
    sleep_time = 5  # NOTE: Change sleep time
    correction_value = -98.4  # SensorA - calibration
    controller = YL69Controller(pin=22, correction=correction_value)

    try:
        controller.output_from_gpio(True)
        while True:
            raw_value = controller.read_adc(0)  # measured Value
            corrected_value = controller.get_corrected_value(0)  # the measured value with correction
            if raw_value != -1:
                print(f"Raw Sensor Value: {raw_value}, Corrected Sensor Value: {corrected_value}")
            sleep(sleep_time)
    except KeyboardInterrupt:
        print("Humidity sensor program interrupted.")
    finally:
        controller.close()


def run_optical_sensor():
    optical_sensor = OPTICAL()
    optical_sensor.run_optical_sensor()


if __name__ == "__main__":
    try:
        # Start both sensors in separate threads
        humid_thread = Thread(target=run_humid_sensor, daemon=True)
        optical_thread = Thread(target=run_optical_sensor, daemon=True)

        humid_thread.start()
        optical_thread.start()

        # Keep the main thread running to allow threads to work
        while True:
            sleep(1)

    except KeyboardInterrupt:
        print("Main program interrupted.")
