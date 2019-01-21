import win32gui

class Window():
	def callback(self,hwnd, extra):
		rect = win32gui.GetWindowRect(hwnd)
		x = rect[0]
		y = rect[1]
		w = rect[2] - x
		h = rect[3] - y
		txt=win32gui.GetWindowText(hwnd)
		if "CONNECT 4 BOARD" in txt:
			self.window_handle=hwnd
			self.window_x=rect[0]
			self.window_y=rect[1]
			self.window_w=rect[2]
			self.window_h=rect[3]
	def __init__(self):
		self.window_handle=-1
		self.window_x=-1
		self.window_y=-1
		self.window_w=-1
		self.window_h=-1
		win32gui.EnumWindows(self.callback, None)
	def update(self):
		rect = win32gui.GetWindowRect(self.window_handle)
		self.window_x=rect[0]
		self.window_y=rect[1]
		self.window_w=rect[2]
		self.window_h=rect[3]

