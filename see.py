from naoqi import ALProxy
import cv2,imutils,random,math,copy,motion,time
import numpy as np



class Detector():
	def __init__(self):
		self.board=Board()
	def detect(self,img):
		imgDebug=img.copy()

		#Get Threshold
		rlower = (0,0,100)
		rupper = (100,100,255)
		#rlower=(0,0,129)

		ylower = (0,100,100)
		yupper = (100,255,255)
		
		blower = (100,0,0)
		bupper = (255,100,100)

		rmask = cv2.inRange(img, rlower, rupper)
		ymask = cv2.inRange(img, ylower, yupper)
		thresh = cv2.bitwise_or(rmask,ymask)
		cv2.imshow("thresh",thresh)

		#Get threshold of board
		bmask = cv2.inRange(img, blower, bupper)

		kernal=np.ones((5,5),np.uint8)
		smoothed = cv2.erode(bmask,kernal,iterations=2)
		cv2.imshow("smoothed",smoothed)

		# find contours of the board + get biggest one
		bcnts = cv2.findContours(smoothed.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		bcnts = bcnts[0] if imutils.is_cv2() else bcnts[1]
		
		board_x=board_y=0
		board_h,board_w=img.shape[:2]
		if len(bcnts)>0:
			bcnts_max=0
			bcnts_i=-1
			for i,con in enumerate(bcnts):
				area = cv2.contourArea(con)
				if area>bcnts_max:
					bcnts_max=area
					bcnts_i=i
			#cv2.drawContours(imgDebug, [bcnts[bcnts_i]], -1, (0, 255, 0), 2)
			board_x,board_y,board_w,board_h= cv2.boundingRect(bcnts[bcnts_i])
		


			#"Guess" on the row widths
			row_w=[]#widths (x,y,w,h)
			#put the contour points in lists
			bcnts_y=[[],[],[],[],[],[]]
			for con in bcnts[bcnts_i]:
				y=int((float(con[0][1]-board_y)/float(board_h))*6.0)
				bcnts_y[y].append(con[0])
			row_cnts_w=[]
			for i in range(6):
				if len(bcnts_y[i])>0:
					x=min(bcnts_y[i],key=lambda x:x[0])[0]+20
					x2=max(bcnts_y[i],key=lambda x:x[0])[0]-20
					y=min(bcnts_y[i],key=lambda x:x[1])[1]+(15-(i*3))
					y2=max(bcnts_y[i],key=lambda x:x[1])[1]-5
					row_cnts_w.append((x,y,x2,y2))
					cv2.rectangle(imgDebug,(x,y),(x2,y2),(0,255,0),1)
					row_w.append((x,y,x2,y2))

		# find contours in the thresholded image
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]


		#Find the most pluasable blobies
		contours_area = []
		for con in cnts:
			area = cv2.contourArea(con)
			perimeter = cv2.arcLength(con, True)
			if perimeter == 0:
				continue
			circularity = 4*math.pi*(area/(perimeter*perimeter))
			#print(area,circularity)
			if 500 < area < 2250 and 0.5 < circularity < 1.2:
				contours_area.append(con)
		
		cv2.drawContours(imgDebug, contours_area, -1, (0, 255, 0), 2)

		#cv2.imshow("conts",imgDebug)
		#cv2.waitKey(0)

		#find the gameboard
		min_x=999999
		min_y=999999
		max_x=0
		max_y=0
		for c in contours_area:
			x,y,w,h = cv2.boundingRect(c)
			min_x=min(x,min_x)
			min_y=min(y,min_y)
			max_x=max(x+w,max_x)
			max_y=max(y+h,max_y)
		cv2.rectangle(imgDebug,(min_x,min_y),(max_x,max_y),(255,0,0),3)


		#Construct gameboard
		b=[]
		for i in range(6):
			col=[]
			for j in range(7):
				col.append(0)
			b.append(col)


		#Count number of rows
		rowc=6
		rowr=0

		#put peices into rows
		row=[[],[],[],[],[],[]]
		for c in contours_area:
			x,y,w,h = cv2.boundingRect(c)
			yy=min(max(int(round((float((y+h)-min_y)/float(max_y-min_y))*float(rowc)))-1,0),5)
			row[yy].append(c)
		
		#Delete any rows that are empty
		for i in range(6):
			for r in range(len(row)):
				if len(row[r])==0:
					del row[r]
					rowc-=1
					break;
		#find minx,maxx for each row + put them in gameboard
		y=0
		height, width, channels = img.shape
		minx=[]
		maxx=[]
		for r in row:
			minx.append(min(cv2.boundingRect(i)[0] for i in r))
			maxx.append(max(cv2.boundingRect(i)[0]+cv2.boundingRect(i)[2] for i in r))


		#find the max number of columns
		'''
		for i,r in enumerate(row):
			w=(maxx[i]-minx[i])
			#rowr=max(rowr,len(r))
			avg=0.0
			count=0.0
			for c in r:
				_,_,_w,_=cv2.boundingRect(c)
				avg+=_w+15.0
				count+=1.0
			avg=avg/count
			i+=1
			rowr=max(rowr,math.floor(w/avg))
		#rowr=min(rowr,7)
		'''
		rowr=7

		#Normalize the widths
		for i in range(rowc):
			y=0
			for r in row:
				#check if it is close to the one below/above it (assume bigger is correct)
				if y+1==rowc:#bottom - check above
					if abs(minx[y-1]-minx[y])>30 and minx[y-1]<minx[y]:
						minx[y]=minx[y-1]
					if abs(maxx[y-1]-maxx[y])>30 and maxx[y-1]>maxx[y]:
						maxx[y]=maxx[y-1]
				else:#check below
					if abs(minx[y+1]-minx[y])>30 and minx[y+1]<minx[y]:
						minx[y]=minx[y+1]-5
					if abs(maxx[y+1]-maxx[y])>30 and maxx[y+1]>maxx[y]:
						maxx[y]=maxx[y+1]+5
				y+=1
		
		#Noralize widths based on board contour
		for i in range(rowc):
			if minx[i]>row_cnts_w[i][0]:
				minx[i]=row_cnts_w[i][0]+15
			#minx[i]=max(row_cnts_w[i][0],minx[i])
			if maxx[i]<row_cnts_w[i][2]:
				maxx[i]=row_cnts_w[i][2]-15
			#maxx[i]=min(row_cnts_w[i][2],maxx[i])

		y=0
		for r in row:
			w=maxx[y]-minx[y]

			yyy=cv2.boundingRect(r[0])[1]
			cv2.rectangle(imgDebug,(minx[y],yyy),(maxx[y],yyy+30),(255,0,255),2)
			x=0
			def takex(elem):
				return cv2.boundingRect(elem)[0]
			r.sort(key=takex)
			for i in r:
				cx,cy,cw,ch=cv2.boundingRect(i)
				M = cv2.moments(i)
				xx = int(M["m10"] / M["m00"])
				yy = int(M["m01"] / M["m00"])
				xx=clamp(xx,0,width-1)
				yy=clamp(yy,0,height-1)

				_x=int((float(xx-minx[y])/float(w))*float(rowr))
				cv2.putText(imgDebug ,str(_x),((xx+1,yy+1)),0,0.5,(0,0,0),1)
				cv2.putText(imgDebug ,str(_x),((xx,yy)),0,0.5,(255,255,255),1)
				
				imgcolor=img[yy][xx]
				i=self.getimgcolor(imgcolor)
				_x=clamp(_x,0,6)
				b[y][_x]=i
				x+=1
			y+=1

		#Normalize the board - move peices down into correct columns
		for i in range(6):
			for y in range(len(b)-1):
				for x in range(len(b[0])):
					if b[y][x]!=0 and b[y+1][x]==0:
						b[y+1][x]=b[y][x]
						b[y][x]=0


		self.board.draw(b)
		cv2.imshow("debug",imgDebug)
		#cv2.waitKey(0)
		return b

	def getimgcolor(self,color):
		red=(49,65,244)
		yellow=(66,252,252)
		#red=(0,0,150)
		#yellow=(0,150,150)
		black=(255,255,255)
		white=(0,0,0)
		colorStr="black"
		colorDist=point_distance(color[0],color[1],color[2],black[0],black[1],black[2])

		colorDist=point_distance(color[0],color[1],color[2],black[0],black[1],black[2])
		colorDist2=point_distance(color[0],color[1],color[2],red[0],red[1],red[2])
		if colorDist2<colorDist:
			colorDist=colorDist2
			colorStr="red"
		colorDist2=point_distance(color[0],color[1],color[2],yellow[0],yellow[1],yellow[2])
		if colorDist2<colorDist:
			colorDist=colorDist2
			colorStr="yellow"
		colorDist2=point_distance(color[0],color[1],color[2],white[0],white[1],white[2])
		if colorDist2<colorDist:
			colorDist=colorDist2
			colorStr="white"
		if colorStr=="red" or colorStr=="yellow" and colorDist<75:
			if colorStr=="red":
				return 1
			else:
				return 2
		return 0

class Board():
	def __init__(self):
		"""
			board=[ [0=(0,1,2),1,2,3,4,5,6] ... [0,1..6] ]
			0=none
			1=red
			2=yellow
		"""
		self.width=320
		self.height=240
		self.image = np.zeros((self.height, self.width, 3), np.uint8)
		self.colors=[(255,255,255),(0,0,255),(0,255,255)]

	def draw(self,board):
		#clear
		self.image = np.zeros((self.height, self.width, 3), np.uint8)
		xx=85
		yy=60
		x=0
		y=0
		w=25
		for col in board:
			for b in col:
				if b==0:
					cv2.circle(self.image,(x+xx,y+yy),w/2,self.colors[b])
				else:
					cv2.circle(self.image,(x+xx,y+yy),w/2,self.colors[b],-1)
					cv2.circle(self.image,(x+xx,y+yy),w/2,(255,255,255))
				x+=w
			x=0
			y+=w
		cv2.imshow("board",self.image)


class Move():
	def __init__(self):
		self.BOARDWIDTH = 7
		self.BOARDHEIGHT = 6
	def getComputerMove(self,board, computerTile):
		potentialMoves = self.getPotentialMoves(board, computerTile, 2)
		bestMoveScore = max([potentialMoves[i] for i in range(self.BOARDWIDTH) if self.isValidMove(board, i)])
		bestMoves = []
		for i in range(len(potentialMoves)):
			if potentialMoves[i] == bestMoveScore:
				bestMoves.append(i)
		return random.choice(bestMoves)
	def getPotentialMoves(self,board, playerTile, lookAhead):
		if lookAhead == 0:
			return [0] * self.BOARDWIDTH

		potentialMoves = []

		if playerTile == 'X':
			enemyTile = 'O'
		else:
			enemyTile = 'X'

		# Returns (best move, average condition of this state)
		if self.isBoardFull(board):
			return [0] * self.BOARDWIDTH

		# Figure out the best move to make.
		potentialMoves = [0] * self.BOARDWIDTH
		for playerMove in range(self.BOARDWIDTH):
			dupeBoard = copy.deepcopy(board)
			if not self.isValidMove(dupeBoard, playerMove):
				continue
			self.makeMove(dupeBoard, playerTile, playerMove)
			if self.isWinner(dupeBoard, playerTile):
				potentialMoves[playerMove] = 1
				break
			else:
				# do other player's moves and determine best one
				if self.isBoardFull(dupeBoard):
					potentialMoves[playerMove] = 0
				else:
					for enemyMove in range(self.BOARDWIDTH):
						dupeBoard2 = copy.deepcopy(dupeBoard)
						if not self.isValidMove(dupeBoard2, enemyMove):
							continue
						self.makeMove(dupeBoard2, enemyTile, enemyMove)
						if self.isWinner(dupeBoard2, enemyTile):
							potentialMoves[playerMove] = -1
							break
						else:
							results = self.getPotentialMoves(dupeBoard2, playerTile, lookAhead - 1)
							potentialMoves[playerMove] += (sum(results) / self.BOARDWIDTH) / self.BOARDWIDTH
		return potentialMoves

	def makeMove(self,board, player, column):
		for y in range(self.BOARDHEIGHT-1, -1, -1):
			if board[column][y] == ' ':
				s = list(board[column])
				s[y]=player
				board[column] = "".join(s)
				return

	def isValidMove(self,board, move):
		if move < 0 or move >= (self.BOARDWIDTH):
			return False
		if board[move][0] != ' ':
			return False
		return True
	def isBoardFull(self,board):
		for x in range(self.BOARDWIDTH):
			for y in range(self.BOARDHEIGHT):
				if board[x][y] == ' ':
					return False
		return True
	def isWinner(self,board, tile):
		# check horizontal spaces
		for y in range(self.BOARDHEIGHT):
			for x in range(self.BOARDWIDTH - 3):
				if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
					return True
		# check vertical spaces
		for x in range(self.BOARDWIDTH):
			for y in range(self.BOARDHEIGHT - 3):
				if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
					return True

		# check / diagonal spaces
		for x in range(self.BOARDWIDTH - 3):
			for y in range(3, self.BOARDHEIGHT):
				if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
					return True

		# check \ diagonal spaces
		for x in range(self.BOARDWIDTH - 3):
			for y in range(self.BOARDHEIGHT - 3):
				if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
					return True

		return False

	def convertBoard(self,board):
		board2 = []
		for y in range(len(board)):
			t=[]
			for x in range(len(board[y])):
				if board[y][x]==0:
					t.append(' ')
				elif board[y][x]==1:
					t.append('X')
				elif board[y][x]==2:
					t.append('O')
			board2.append(t)
		return map("".join,zip(*board2))

	def drawBoard(self,board):
		print ''
		print ' ',
		for x in range(1, self.BOARDWIDTH + 1):
			print ' %s  ' % x,
		print ''

		print('+---+' + ('---+' * (self.BOARDWIDTH - 1)))

		for y in range(self.BOARDHEIGHT):
			print('|   |' + ('   |' * (self.BOARDWIDTH - 1)))

			print '|',
			for x in range(self.BOARDWIDTH):
				print ' %s |' % board[x][y],
			print()

			print('|   |' + ('   |' * (self.BOARDWIDTH - 1)))

			print('+---+' + ('---+' * (self.BOARDWIDTH - 1)))

class Camera():
	def __init__(self,ip,port=9559,cam=1,r=2):
		AL_kTopCamera = 1
		AL_kQVGA = r
		AL_kBGRColorSpace = 13
		self.videoDevice = ALProxy("ALVideoDevice", ip,port)
		self.captureDevice = self.videoDevice.subscribeCamera("test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)
		if r==1:
			self.width=320
			self.height=240
		elif r==2:
			self.width=640
			self.height=480
		elif r==3:
			self.width=1280
			self.height=920
		elif r==7:
			self.width=80
			self.height=60
		self.image = np.zeros((self.height, self.width, 3), np.uint8)


	def step(self):
		result = self.videoDevice.getImageRemote(self.captureDevice)
		if result!=None and result[6]!=None:
			values = map(ord, list(result[6]))
			#self.image=np.array(values).reshape(self.height, self.width,3)
			self.image=np.array(values,dtype=self.image.dtype).reshape(self.height, self.width,3)
	def destruct(self):
		self.videoDevice.unsubscribe(self.captureDevice)
		print "destroyed camera"


class Arms():
	def __init__(self,mp,ts):
		#Setup arms and head joint arrays
		self.LArmArr = ["LShoulderRoll", "LShoulderPitch", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]
		self.RArmArr = ["RShoulderRoll", "RShoulderPitch", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
		self.HeadArr = ["HeadYaw", "HeadPitch"]
		self.RArm1 = [-40, 50, 25, 80, 20, 0]
		self.RArm1 = [x * motion.TO_RAD for x in self.RArm1]
		self.LArm1 = [40, 50, -25, -80, -20, 0]
		self.LArm1 = [x * motion.TO_RAD for x in self.LArm1]

		self.motionProxy=mp
		self.tts=ts
		self.pFractionMaxSpeed=0.25
		self.reset()
	def reset(self):
		self.motionProxy.setStiffnesses(self.RArmArr, [1, 1, 1, 1, 1, 1])
		self.motionProxy.setStiffnesses(self.LArmArr, [1, 1, 1, 1, 1, 1])
		self.RArm1 = [-40, 50, 25, 80, 20, 0]
		self.RArm1 = [x * motion.TO_RAD for x in self.RArm1]

		self.LArm1 = [40, 50, -25, -80, -20, 0]
		self.LArm1 = [x * motion.TO_RAD for x in self.LArm1]

		#self.Head1 = [0, 20]
		#self.Head1 = [x * motion.TO_RAD for x in self.Head1]

		self.motionProxy.angleInterpolationWithSpeed(self.RArmArr, self.RArm1, self.pFractionMaxSpeed)
		self.motionProxy.angleInterpolationWithSpeed(self.LArmArr, self.LArm1, self.pFractionMaxSpeed)
		#self.motionProxy.angleInterpolationWithSpeed(self.HeadArr, self.Head1, self.pFractionMaxSpeed)
		
		names=["HeadYaw","HeadPitch"]
		angles=[0,0.226893]
		self.motionProxy.setStiffnesses(names,[1,1])
		self.motionProxy.angleInterpolationWithSpeed(names, angles, 1)
		self.motionProxy.setStiffnesses(names,[0,0])
	def request(self,column):
		self.motionProxy.setStiffnesses(self.RArmArr, [1, 1, 1, 1, 1, 1])
		self.motionProxy.setStiffnesses(self.LArmArr, [1, 1, 1, 1, 1, 1])
		#self.motionProxy.setStiffnesses(self.HeadArr, [1, 1])
		self.RArm1 = [-40, 50, 25, 80, 20, 0]
		self.LArm1 = [40, 50, -25, -80, -20, 0]

		c=["first","second","third","fourth","fifth","sixth","seventh"]
		self.tts.post.say("Please put my piece in the "+c[column-1]+" column")

		if column == 7:
			self.RArm1 = [1, 15, 0, 0, 0, 0]
		if column == 6:
			self.RArm1 = [9, 15, 0, 0, 0, 0]
		if column == 5:
			self.RArm1 = [15.5, 15, 0, 0, 0, 0]
		if column == 4:
			self.RArm1 = [18, 15, 0, 6, 0, 0]
		if column == 3:
			self.LArm1 = [-15.5, 15, 0, 0, 0, 0]
		if column == 2:
			self.LArm1 = [-10, 15, 0, 0, 0, 0]
		if column == 1:
			self.LArm1 = [-2, 15, 0, 0, 0, 0]
		#point hand
		self.LArm1 = [x * motion.TO_RAD for x in self.LArm1]
		self.RArm1 = [x * motion.TO_RAD for x in self.RArm1]
		self.motionProxy.angleInterpolationWithSpeed(self.LArmArr, self.LArm1, self.pFractionMaxSpeed)
		self.motionProxy.angleInterpolationWithSpeed(self.RArmArr, self.RArm1, self.pFractionMaxSpeed)

		self.reset()
		self.motionProxy.setStiffnesses(self.RArmArr, [0, 0, 0, 0, 0, 0])
		self.motionProxy.setStiffnesses(self.LArmArr, [0, 0, 0, 0, 0, 0])
		self.motionProxy.setStiffnesses(self.HeadArr, [0, 0])



def point_distance(x1,y1,z1,x2,y2=None,z2=None):
	if z2==None:
		return ( (x1 - z1)**2 + (x2 - y1)**2 )**0.5
	else:
		return ( (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2 )**0.5
def clamp(val,mi,ma):
	return max(mi, min(val, ma))
