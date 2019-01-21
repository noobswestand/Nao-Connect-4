import see,cv2,time
from naoqi import ALProxy

ip="192.168.43.105"
port=9559

touch=ALProxy("ALTouch", ip, port)
motionProxy=ALProxy("ALMotion", ip, port)
tts = ALProxy("ALTextToSpeech",ip,port)

#Snap head to begin
arms=see.Arms(motionProxy,tts)

cam=see.Camera(ip,port)
move=see.Move()
detector=see.Detector()


#image=cv2.imread('sample8.png',cv2.IMREAD_COLOR)
#detector=see.Detector()
#detector.detect(image)

'''
import window,imutils
from PIL import ImageGrab
import numpy as np
detector=see.Detector()
_window=window.Window()

while True:
	_window.update()
	x,y,w,h=_window.window_x,_window.window_y,_window.window_w,_window.window_h
	img=ImageGrab.grab(bbox=(x,y,w,h))
	img_np=np.array(img)
	img_np = imutils.resize(img_np)
	img_np = cv2.cvtColor(img_np,cv2.COLOR_BGR2RGB)
	frame=cv2.cvtColor(img_np,cv2.COLOR_BGR2GRAY)

	#cv2.imshow("test",img_np)
	detector.detect(img_np)

	if cv2.waitKey(1) == 27:
		break
'''


#States
'''
	0=asking the player to move
	1=waiting for player
	2=asking to place piece
	3=waiting for player to place own peice
'''
'''
	red=O
	yellow=X
'''
goFirst=True
color="yellow"
red="O"
yellow="X"
requested=0
firstMove=0


if goFirst==True:
	#requested=2
	#firstMove=2
	color="red"


tts.say("Welcome to connect 4!")
tts.say("I am the "+color+" color!")
tts.say("Let's begin")


try:
	while True:
		cam.step()
		image=cam.image
		board=move.convertBoard(detector.detect(image))
		
		if requested==0:
			#Check to see if someone won
			if move.isWinner(board,yellow)==True:
				tts.say("I won!")
				break;

			tts.say("Okay. Your turn")
			requested=1
		if requested==1:
			status=touch.getStatus()
			if status[12][1]==True or status[13][1]==True:
				tts.say("My turn")
				requested=2

		if requested==2:
			if move.isWinner(board,red)==True:
				tts.say("You won!")
				break;
			nextMove=move.getComputerMove(board,yellow)+1
			if firstMove>0 and goFirst==True:
				if firstMove==2:
					nextMove=1
				else:
					nextMove=7
				firstMove-=1
			print nextMove
			arms.request(nextMove)
			requested=3
		if requested==3:
			status=touch.getStatus()
			if status[12][1]==True or status[13][1]==True:
				requested=0


		if cv2.waitKey(33) == 27:
			cv2.destroyAllWindows()
			break
except Exception as e:
	print e

cam.destruct()
