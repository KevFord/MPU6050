import machine
import time
import ssd1306
import array

from machine import I2C, Pin
from time import sleep
from ssd1306 import SSD1306_I2C
from micropython import const

# Defines for MPU6050:
WHO_AM_I     = const(0x75)
PWR_MGMT_1   = const(0x6B) # Write 0x1 to wake the MPU6050.
SMPLRT_DIV   = const(0x19) # Write 0x7 to set clock division to 8, meaning a 1khz update frequency.
ACCEL_CONFIG = const(0x1C) 
ACCEL_XOUT_H = const(0x3B)
ACCEL_XOUT_L = const(0x3C)
ACCEL_YOUT_H = const(0x3D)
ACCEL_YOUT_L = const(0x3E)
ACCEL_ZOUT_H = const(0x3F)
ACCEL_ZOUT_L = const(0x40)

CALIBRATION_ITERATIONS = const(1)

# OLED address:
SSD1306 = const(0x3C)
# MPU6050 address:
MPU = const(0x68)

# Create I2C object:
hi2c1 = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16))

# OLED object:
oled = SSD1306_I2C(128, 64, hi2c1)

# Buffer object used for writing and reading data from MPU:
buf = bytearray(6) # Array of 6 elements.

# Pin for calibrating the MPU:
touch_btn = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Global variables for calibration:
x_cal = 0
y_cal = 0
z_cal = 0
calibrate = 1

# Function that prints the "text" string at x and y:
def print_to_oled(text, x, y) :
    oled.fill(0)
    oled.text(text, x, y)
    oled.show()
    
# Interrupt when button is presset:
def callback(pin) :
    global calibrate
    calibrate = 1

# Wakes the MPU and checks the connection:
def MPU6050_Init() :
    
    # Wake the MPU:
    hi2c1.writeto_mem(MPU, PWR_MGMT_1, buf) 
    buf[0] = 0x01

    # Check connection:
    hi2c1.readfrom_mem_into(MPU, WHO_AM_I, buf)
    if buf[0] != 104 :
        print_to_oled("WHO_AM_I", 0, 0)
        time.sleep(5)
    else :
        print_to_oled("Init OK", 0, 0)
        time.sleep(1)
    
    # Set the sample rate:
    buf[0] = 0x07
    hi2c1.writeto_mem(MPU, SMPLRT_DIV, buf)
    
    # Small delay to ensure the user has time to see.
    time.sleep(1)

# Prints the raw values to the OLED display :
def MPU6050_Display_Values(x, y, z) :
    oled.fill(0)
    oled.text("X = ", 0, 0)
    oled.text(x, 30, 0)
    oled.text("Y = ", 0, 10)
    oled.text(y, 30, 10)
    oled.text("Z = ", 0, 20)
    oled.text(z, 30, 20)
    oled.show()
    time.sleep(0.2)

def MPU6050_Read_Accel_Raw_X() :
    
    hi2c1.readfrom_mem_into(MPU, ACCEL_XOUT_H, buf)
    
    x_axsis = (int)((buf[0]) << 8 | buf[1]) 
    x_axsis_str = str(x_axsis)
    
    return x_axsis

def MPU6050_Read_Accel_Raw_Y() :
    
    hi2c1.readfrom_mem_into(MPU, ACCEL_XOUT_H, buf)

    y_axsis = (int)((buf[2]) << 8 | buf[3])
    
    return y_axsis

def MPU6050_Read_Accel_Raw_Z() :
    
    hi2c1.readfrom_mem_into(MPU, ACCEL_XOUT_H, buf)

    z_axsis = (int)((buf[4]) << 8 | buf[5])
    
    return z_axsis
    
def MPU6050_Calibrate() :
    
    global CALIBRATION_ITERATIONS
    list = [CALIBRATION_ITERATIONS]
    length = len(list)
    
    x_values = [CALIBRATION_ITERATIONS]
    y_values = [CALIBRATION_ITERATIONS]
    z_values = [CALIBRATION_ITERATIONS]
    
    x_mean = 0
    y_mean = 0
    z_mean = 0
    
    global x_cal
    global y_cal
    global z_cal
    
    for i in range(length) :
        x_values[i] = MPU6050_Read_Accel_Raw_X()
        y_values[i] = MPU6050_Read_Accel_Raw_Y()
        z_values[i] = MPU6050_Read_Accel_Raw_Z()
        x_mean += x_values[i]
        y_mean += y_values[i]
        z_mean += z_values[i]
        
    x_cal = x_mean / CALIBRATION_ITERATIONS
    y_cal = y_mean / CALIBRATION_ITERATIONS
    z_cal = z_mean / CALIBRATION_ITERATIONS
    
    if x_cal == 0 :
        x_cal = 1
    if y_cal == 0 :
        y_cal = 1
    if z_cal == 0 :
        z_cal = 1
        
    print_to_oled("Calibrating...", 0, 0)
    time.sleep(1)
    
# Setup interrupt:
touch_btn.irq(trigger = Pin.IRQ_RISING, handler = callback)

# Function call area:
MPU6050_Init()

while True :
    if calibrate == 1:
        MPU6050_Calibrate()
        calibrate = 0
        
    x_str = str(MPU6050_Read_Accel_Raw_X() / x_cal)
    y_str = str(MPU6050_Read_Accel_Raw_X() / y_cal)
    z_str = str(MPU6050_Read_Accel_Raw_X() / z_cal)
    
    MPU6050_Display_Values(x_str, y_str, z_str)