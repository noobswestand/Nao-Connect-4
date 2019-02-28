import tkinter as tk
from tkColorChooser import askcolor
from threading import Thread,Lock
from PIL import Image, ImageTk
import main,cv2
from functools import partial


RED_UPPER = [100,100,255] #bgr
RED_LOWER = [0,0,100]

YELLOW_UPPER = [100,255,255]
YELLOW_LOWER = [0,100,100]

BLUE_UPPER = [255,100,100]
BLUE_LOWER = [100,0,0]

COLORS=[["red",RED_LOWER,RED_UPPER],["yellow",YELLOW_LOWER,YELLOW_UPPER],["blue",BLUE_LOWER,BLUE_UPPER]]


class Interface():
	def __init__(self,image):
		global COLORS
		self.main_window = tk.Tk()

		self.label = tk.Label(self.main_window)
		self.label.bind('<Button-1>',self.imgClick)
		self.label.pack()
		self.updateImg(image)

		self.buttoncolors=[]
		self.slidercolors=[]
		for i in COLORS:
			frame=tk.Frame()

			action_with_arg = partial(self.getColor, i[0])
			btn=tk.Button(frame,text=i[0], command=action_with_arg)
			self.buttoncolors.append(btn)
			btn.pack()
			

			frameChild=tk.Frame(frame)
			label=tk.Label(frameChild,text="Max")
			label.pack()
			label=tk.Label(frameChild,text="")
			label.pack()
			label=tk.Label(frameChild,text="Min")
			label.pack()
			frameChild.pack(side=tk.LEFT)

			tmp=[]
			for ii in range(3):
				frameChild=tk.Frame(frame,bg=i[0])

				#labels
				if ii==0:
					txt="blue"
				if ii==1:
					txt="green"
				if ii==2:
					txt="red"
				label=tk.Label(frameChild,text=txt,bg=i[0])
				label.pack(side=tk.TOP)

				#min
				action_with_arg = partial(self.setColorMin, i[0],COLORS[ii][0])
				slider0=tk.Scale(frameChild,from_=0,to=255,orient=tk.HORIZONTAL,bg=i[0],command=action_with_arg)
				slider0.pack(side=tk.BOTTOM)
				
				#max
				action_with_arg = partial(self.setColorMax, i[0],COLORS[ii][0])
				slider1=tk.Scale(frameChild,from_=0,to=255,orient=tk.HORIZONTAL,bg=i[0],command=action_with_arg)
				slider1.pack(side=tk.BOTTOM)
				
				slider0.set(i[1][ii])
				slider1.set(i[2][ii])

				frameChild.pack(side=tk.LEFT)
				tmp.append([slider0,slider1])

			self.slidercolors.append(tmp)

			frame.pack()





		
		self.button_select='none'
		self.button_on=0
		self.button_colors=[]

	def start(self):
		tk.mainloop()

	def setColorMin(self,color,color2,value):
		for i in COLORS:
			if i[0]==color:
				if color2=="blue":
					i[1][2]=value
				if color2=="yellow":
					i[1][1]=value
				if color2=="red":
					i[1][0]=value
		main.update_colors((COLORS[0][1],COLORS[0][2]),(COLORS[1][1],COLORS[1][2]),(COLORS[2][1],COLORS[2][2]))
	def setColorMax(self,color,color2,value):
		for j,i in enumerate(COLORS):
			if i[0]==color:
				if color2=="blue":
					self.slidercolors[j][2][0].configure(to=value)
					i[2][2]=value
				if color2=="yellow":
					self.slidercolors[j][1][0].configure(to=value)
					i[2][1]=value				
				if color2=="red":
					self.slidercolors[j][0][0].configure(to=value)
					i[2][0]=value
		main.update_colors((COLORS[0][1],COLORS[0][2]),(COLORS[1][1],COLORS[1][2]),(COLORS[2][1],COLORS[2][2]))
	
	def updateSliders(self):
		for j,i in enumerate(COLORS):
			#red
			self.slidercolors[j][0][0].set(i[1][0])
			self.slidercolors[j][0][1].set(i[2][0])
			
			#green
			self.slidercolors[j][1][0].set(i[1][1])
			self.slidercolors[j][1][1].set(i[2][1])
			
			#blue
			self.slidercolors[j][2][0].set(i[1][2])
			self.slidercolors[j][2][1].set(i[2][2])
			


	def colorReset(self):
		for i in self.buttoncolors:
			i.configure(bg='white')
		self.button_select='none'
		self.button_on=0
		self.button_colors=[]
	def getColor(self,color):
		if self.button_select=='none':
			self.button_select=color
			print("SELECT 5 {0} COLORS".format(color))
			for i in self.buttoncolors:
				if i['text']==color:
					i.configure(bg='green')
		else:
			self.colorReset()

	def imgClick(self,event):
		global COLORS
		if self.button_select!='none':
			self.button_on+=1
			self.button_colors.append(self.image.getpixel((event.x,event.y)))
			if self.button_on<5:
				print "Select {0} more colors".format(5-self.button_on)
			elif self.button_on==5:
				for i in COLORS:
					if i[0]==self.button_select:
						r_max=0
						r_min=255
						b_max=0
						b_min=255
						g_max=0
						g_min=255
						for color in self.button_colors:
							r_max=max(r_max,color[2])
							g_max=max(g_max,color[1])
							b_max=max(b_max,color[0])

							r_min=min(r_min,color[2])
							g_min=min(g_min,color[1])
							b_min=min(b_min,color[0])
						
						i[2]=[r_max,g_max,b_max]
						i[1]=[r_min,g_min,b_min]

				main.update_colors((COLORS[0][1],COLORS[0][2]),(COLORS[1][1],COLORS[1][2]),(COLORS[2][1],COLORS[2][2]))
				print "Done calibrating {0}".format(self.button_select)
				self.colorReset()
				self.updateSliders()

	def updateImg(self,image):
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		im_pil = Image.fromarray(image)
		photo = ImageTk.PhotoImage(im_pil)
		self.image = im_pil.convert('RGB')
		self.label.image=photo
		self.label.configure(image=photo)
		


image=cv2.imread("sample.png")
ui=Interface(image)



thread = Thread(target = main.main,args=(ui,"10.255.3.76"))
thread.setDaemon(True)
thread.start()


ui.start()

