from gpiozero import LED
from gpiozero import Button
from time import sleep
import os
import requests
import json
from RPi import GPIO
import Adafruit_CharLCD as LCD

red_led = LED(19)
green_led = LED(26)
button = Button(13)
lcd_rs = 25
lcd_rw = 6
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
lcd_contrast = 21
GPIO.setup(lcd_contrast, GPIO.OUT)
GPIO.output(lcd_contrast, False)
GPIO.setup(lcd_rw, GPIO.OUT)
GPIO.output(lcd_rw, False)

lcd.enable_display(True)

def reset_lcd(lcd):
	lcd.clear()
	lcd.home()

def identify():
	reset_lcd(lcd)
	path = "data/picture.jpg"
	take_picture(path)
	lcd.message("Sending picture\nto server")
	response = send_picture("IP_ADRESS:8080/IoT2022/faceRecognition", path)
	response_json = json.loads(response.text)
	reset_lcd(lcd)
	print(response_json)
	
	if(response_json["status"] == "success"):
		if(not response_json["name"]):
			lcd.message("Face not\nrecognized")
			sleep(5)
			reset_lcd(lcd)
		else:
			lcd.message(response_json["name"]+"\n")
			if response_json["access"]:
				red_led.off()
				green_led.on()
				lcd.message("Access granted")
				sleep(5)
				green_led.off()
				reset_lcd(lcd)
			else:
				green_led.off()
				red_led.on()
				lcd.message("Access denied")
				sleep(5)
				red_led.off()
				reset_lcd(lcd)
	elif(response_json.status == "error"):
		lcd.message("Error")
		lcd.set_cursor(1,2)
		lcd.message("Code : "+response_json["code"])
		sleep(5)
		reset_lcd(lcd)

		
def take_picture(output_path):
	lcd.message("Taking picture\nStand still")
	os.system(f"libcamera-jpeg -o {output_path}")
	reset_lcd(lcd)
	
	
def send_picture(url, path):
	try:
		files = {'file': ('picture.jpg', open(path, 'rb'), 'image/jpg')}
		with requests.Session() as s:
			response = s.post(url=url, files=files)
		return response
	except Exception as e:
		return '{"status":"error","code":"Unknown face"}'

while True:
	reset_lcd(lcd)
	lcd.message("Press the button\nto identify")
	button.wait_for_press()
	sleep(0.05)
	button.wait_for_release()
	sleep(0.05)
	identify()
