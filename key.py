import os
import keyboard
while True:
	if keyboard.is_pressed('space'):  # if key 'q' is pressed 
		try:
			os.mkdir("./stopped")
			print("PRESSED Space")
		except Exception as e:
			pass