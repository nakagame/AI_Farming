import os
import glob
from time import sleep


BASE_DIR = "/sys/bus/w1/devices"
TEMP_FILE = "w1_slave"
DIR_HEAD = "28-"
TEMP_RATE = 1000


def read_temp_raw(temp_file):
    if not os.path.isfile(temp_file): return None
    f = open(temp_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(temp_file):
    lines = read_temp_raw(temp_file)
    if lines is None: return None

    if len(lines) < 2: return None
    if lines[0].strip()[-3:] != 'YES': return None

    t_pos = lines[1].find('t=')
    if t_pos < 0: return None

    t_str = lines[1][t_pos+2:]
    try:
        t_val = float(t_str) / TEMP_RATE
        return t_val
    except Exception:
        return None


def main():
    base_subdir = BASE_DIR + "/" + DIR_HEAD + "*"
    ds_dirs = glob.glob(base_subdir)
    if len(ds_dirs) == 0:
        print(f"Error1: 0.0 :: {ds_dirs}")
    else:
        temp_file = ds_dirs[0] + "/" + TEMP_FILE
        temp_val = read_temp(temp_file)
        
        if temp_val is None: print("Error2: 0.0 :: Can't measure temperarute...")
        else: print(temp_val)


if __name__ == '__main__':
    try:
        while True:
            main()
            sleep(1) # NOTE: Moderate sleep time

    except KeyboardInterrupt:
        print("Main program interrupted.")