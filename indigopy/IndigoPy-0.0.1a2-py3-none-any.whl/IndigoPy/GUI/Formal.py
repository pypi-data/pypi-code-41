import tkinter as tk


#========================================================================================================================
#=========================================================||||||=========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#=========================================================||||||=========================================================
#========================================================================================================================
#												 Abrreviation Instruction
#========================================================================================================================
'''
All the abrreviations are two-letter words and the first letter is a capital letter
Hl--Hightlight--white background and gray boundary
Sv--Scroll Vertical--with a vertical scroll bar
Sh--Scroll Horizonal--with a horizonal scroll bar
Sb--Scroll Both--with a vertical scroll bar and a horizonal scroll bar
'''
#========================================================================================================================













#========================================================================================================================
#======================================================|||||||||=========================================================
#====================================================||=========||=======================================================
#====================================================||==================================================================
#====================================================||==================================================================
#====================================================||==================================================================
#====================================================||=========||=======================================================
#======================================================|||||||||=========================================================
#========================================================================================================================
#												   Classes definition
#========================================================================================================================





#========================================================================================================================
#=====================================================||||||=============================================================
#=====================================================||||||=============================================================
#=====================================================||=================================================================
#========================================================================================================================
#Static Frame or Canvas with white background and gray boundary
#Example of arguments: width=300, height=200
#========================================================================================================================

class HlFrame(tk.Frame):
	def __init__(self,*args,**kargs):
		super(HlFrame,self).__init__(*args,**kargs)
		self.config(highlightbackground='gray',highlightthickness=1,bg='#FFF5EE')

class HlCanvas(tk.Canvas):
	def __init__(self,*args,**kargs):
		super(HlCanvas,self).__init__(*args,**kargs)
		self.config(highlightbackground='gray',highlightthickness=1,bg='#FFF5EE')




#========================================================================================================================
#=======================================================||||==||||||=====================================================
#=======================================================||====||=========================================================
#=====================================================||||====||||||=====================================================
#========================================================================================================================
#Scrolled canvas with white background and gray boundary
#Widget in the canvas can not move with the canvas, use Scrolled Frame instead 
#Example of arguments: width=300, height=200,scrollregion=(0,0,300,2000)#(left,top,right,bottom)
#========================================================================================================================


class HlSvCanvas(tk.Canvas):
	def __init__(self,root,*args,**kargs):
		self.Frame=tk.Frame(root)
		self.Frame.config(highlightbackground='gray', highlightthickness=1, bg='#FFF5EE')
		super(HlSvCanvas,self).__init__(self.Frame,*args,**kargs)
		super(HlSvCanvas,self).pack(side=tk.LEFT)
		self.sb=tk.Scrollbar(self.Frame,command=self.yview)
		self.sb.pack(side=tk.RIGHT,fill=tk.Y)
		self.config(bg='#FFF5EE',yscrollcommand=self.sb.set)
		self.propagate(0)
	def pack(self,*args,**kargs):
		self.Frame.pack(*args,**kargs)

class HlShCanvas(tk.Canvas):
	def __init__(self,root,*args,**kargs):
		self.Frame=tk.Frame(root)
		self.Frame.config(highlightbackground='gray', highlightthickness=1, bg='#FFF5EE')
		super(HlShCanvas,self).__init__(self.Frame,*args,**kargs)
		super(HlShCanvas,self).pack(side=tk.TOP)
		self.sb=tk.Scrollbar(self.Frame,orient=tk.HORIZONTAL,command=self.xview)
		self.sb.pack(side=tk.BOTTOM,fill=tk.X)
		self.config(bg='#FFF5EE',xscrollcommand=self.sb.set)
		self.propagate(0)
	def pack(self,*args,**kargs):
		self.Frame.pack(*args,**kargs)

class HlSbCanvas(tk.Canvas):
	def __init__(self,root,*args,**kargs):
		self.Frame=tk.Frame(root)
		self.Frame.config(highlightbackground='gray', highlightthickness=1, bg='#FFF5EE')
		super(HlSbCanvas,self).__init__(self.Frame,*args,**kargs)
		self.sbh=tk.Scrollbar(self.Frame,orient=tk.HORIZONTAL,command=self.xview)
		self.sbh.pack(side=tk.BOTTOM,fill=tk.X)
		self.config(bg='#FFF5EE',xscrollcommand=self.sbh.set)
		self.sbv=tk.Scrollbar(self.Frame,command=self.yview)
		self.sbv.pack(side=tk.RIGHT,fill=tk.Y)
		self.config(bg='#FFF5EE',yscrollcommand=self.sbv.set)
		super(HlSbCanvas,self).pack(side=tk.TOP)
		self.propagate(0)
	def pack(self,*args,**kargs):
		self.Frame.pack(*args,**kargs)

#========================================================================================================================
#=======================================================||||==||||||=====================================================
#=======================================================||====||||||=====================================================
#=====================================================||||====||=========================================================
#========================================================================================================================
#Scrolled Frame with white background and gray boundary
#Example of arguments: width=300, height=200   #scrollregion varied with the content of frame
#========================================================================================================================


class HlSvFrame(tk.Frame):
	def __init__(self,root,*args,**kargs):
		self.Frame=tk.Frame(root)
		self.Frame.config(highlightbackground='gray', highlightthickness=1, bg='#FFF5EE')
		self.canvas=tk.Canvas(self.Frame,*args,**kargs)
		self.sb=tk.Scrollbar(self.Frame,command=self.canvas.yview)
		self.sb.pack(side=tk.RIGHT,fill=tk.Y)
		self.canvas.pack(sid=tk.LEFT)
		self.canvas.config(bg='#FFF5EE',yscrollcommand=self.sb.set)
		self.canvas.propagate(0)
		def adjust(event):
		    self.canvas.config(scrollregion=(0,0,self.canvas.winfo_width(),event.height))
		    self.canvas.coords(self.win,(self.canvas.winfo_width()/2,(event.height)/2))
		super(HlSvFrame,self).__init__(self.canvas,*args,**kargs)
		super(HlSvFrame,self).pack()
		self.win=self.canvas.create_window((self.canvas.winfo_width()/2,self.canvas.winfo_height()/2), window=self)
		self.bind("<Configure>",adjust)

	def pack(self,*args,**kargs):
		self.Frame.pack(*args,**kargs)

	def config(self,*args,**kargs):
		try:
			self.canvas.config(height=kargs['height'])
		except:
			1
		try:
			self.canvas.config(width=kargs['width'])
		except:
			1
		super(HlSvFrame,self).config(*args,**kargs)




class HlShFrame(tk.Frame):
	def __init__(self,root,*args,**kargs):
		self.Frame=tk.Frame(root)
		self.Frame.config(highlightbackground='gray', highlightthickness=1, bg='#FFF5EE')
		self.canvas=tk.Canvas(self.Frame,*args,**kargs)
		self.sb=tk.Scrollbar(self.Frame,orient=tk.HORIZONTAL,command=self.canvas.xview)
		self.sb.pack(side=tk.BOTTOM,fill=tk.X)
		self.canvas.pack(sid=tk.TOP)
		self.canvas.config(bg='#FFF5EE',xscrollcommand=self.sb.set)
		self.canvas.propagate(0)
		def adjust(event):
		    self.canvas.config(scrollregion=(0,0,event.width,self.canvas.winfo_height()))
		    self.canvas.coords(self.win,(event.width/2, self.canvas.winfo_height()/2))
		super(HlShFrame,self).__init__(self.canvas,*args,**kargs)
		super(HlShFrame,self).pack()
		self.win=self.canvas.create_window((self.canvas.winfo_width()/2,self.canvas.winfo_height()/2), window=self)
		self.bind("<Configure>",adjust)

	def pack(self,*args,**kargs):
		self.Frame.pack(*args,**kargs)

	def config(self,*args,**kargs):
		try:
			self.canvas.config(height=kargs['height'])
		except:
			1
		try:
			self.canvas.config(width=kargs['width'])
		except:
			1
		super(HlShFrame,self).config(*args,**kargs)


class HlSbFrame(tk.Frame):
	def __init__(self,root,*args,**kargs):
		self.Frame=tk.Frame(root)
		self.Frame.config(highlightbackground='gray', highlightthickness=1, bg='#FFF5EE')
		self.canvas=tk.Canvas(self.Frame,*args,**kargs)

		self.sb=tk.Scrollbar(self.Frame,orient=tk.HORIZONTAL,command=self.canvas.xview)
		self.sb.pack(side=tk.BOTTOM,fill=tk.X)
		self.canvas.config(bg='#FFF5EE',xscrollcommand=self.sb.set)
		self.sb=tk.Scrollbar(self.Frame,command=self.canvas.yview)
		self.sb.pack(side=tk.RIGHT,fill=tk.Y)
		self.canvas.config(bg='#FFF5EE',yscrollcommand=self.sb.set)

		self.canvas.pack(sid=tk.TOP)
		self.canvas.propagate(0)
		def adjust(event):
		    self.canvas.config(scrollregion=(0,0,event.width,event.height))
		    self.canvas.coords(self.win,(event.width/2, event.height/2))
		super(HlSbFrame,self).__init__(self.canvas,*args,**kargs)
		super(HlSbFrame,self).pack()
		self.win=self.canvas.create_window((self.canvas.winfo_width()/2,self.canvas.winfo_height()/2), window=self)
		self.bind("<Configure>",adjust)

	def pack(self,*args,**kargs):
		self.Frame.pack(*args,**kargs)

	def config(self,*args,**kargs):
		try:
			self.canvas.config(height=kargs['height'])
		except:
			1
		try:
			self.canvas.config(width=kargs['width'])
		except:
			1
		super(HlSbFrame,self).config(*args,**kargs)


#========================================================================================================================
#=======================================================||||==||||||=====================================================
#=======================================================||====||||||=====================================================
#=====================================================||||====||=========================================================
#========================================================================================================================
#Scrolled Frame with white background and gray boundary
#Example of arguments: width=300, height=200   #scrollregion varied with the content of frame
#========================================================================================================================














#========================================================================================================================
#=====================================================||||||||||||||=====================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#===========================================================||===========================================================
#========================================================================================================================
#														Test Programme
#========================================================================================================================
root=tk.Tk()
a=HlSbFrame(root, width=300, height=200)
a.pack(side=tk.RIGHT)
'''
coord = 10, 50, 500, 500
arc = a.create_arc(coord, start=0, extent=150, fill="blue")
'''

b=tk.Label(a,text='''aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
	bbb
	c
	d
	e
	f
	g
	h
	i
	j
	k
	l
	m
	n
	o
	p
	q
	r
	sgggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg
	t
	u
	v
	w
	x
	y
	z
	''')
b.pack(side=tk.LEFT,fill=tk.X)

def test():
	a.config(height=400)
tk.Button(root,text='test',command=test).pack()

tk.mainloop()
#========================================================================================================================
