import spidev                       
import time                         
import sys                          


class OPTICAL:
    def __init__(self) -> None:
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000 
        self.sleep = 5

    def run_optical_sensor(self):
        while True:
            resp = self.spi.xfer2([0x68, 0x00])                 
            volume = ((resp[0] << 8) + resp[1]) & 0x3FF    
            print(f"Optical Sensor: {volume}")                                  
            time.sleep(self.sleep)                                  
                

if __name__ == "__main__":
    os = OPTICAL()
    os.run_optical_sensor()