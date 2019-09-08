"""
{
	dataurl:url,
	fields:[
		field, field, ...
	]
}
field:
{
	name:"ttt",
	label:"ffff",
	datatype:one of str, text, short, long, float, date, time, ...
	freeze:True of False
	hidden:True of False
	width: default is 100
	cols:default is 1
}
"""
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from appPublic.dictObject import DictObject
from .datagrid.Datagrid import DataGrid
from .utils import absurl

class ScrollDataGrid(ScrollView):
	def __init__(self,**kw):
		super().__init__()
		self.grid = DataGrid()
		self.grid.size_hint = (None,1)
		# self.grid.width = 1500
		self.grid.bind(minimum_width=self.grid.setter('width'))
		self.do_scroll_y = False
		self.do_scroll_x = True
		self.add_widget(self.grid)
	
	def setupGrid(self, headers, width, height):
		r =  self.grid.setupGrid(headers,width,height)
		self.grid.width = width
		self.body = self.grid.body

	def  addRow(self, rowsData, **kwargs):
		return self.grid.addRow(rowsData,**kwargs)

	def removeRowAtIndex(self, index):
		return self.grid.removeRowAtIndex(index)

	def changeCellValueAtRow(self, rowIndex, cellIndex, cellValue):
		return self.grid.changeCellValueAtRow(rowIndex, cellIndex, cellValue)
	def removeRowById(self, widget_id):
		return self.grid.removeRowById(widget_id)
	def removeAllContent(self):
		return self.grid.removeAllContent()
	def changeRowColor(self, rowIndex, changedColor):
		return self.grid.changeRowColor(rowIndex, changedColor)
	def changeRowColorByID(self, widget_id, changedColor):
		return self.grid.changeRowColorByID(widget_id, changeColor)
		
	
class DataList(BoxLayout):
	def __init__(self,**options):
		super().__init__()
		self.options = DictObject(**options)
		self.total_cnt = 0
		self.page_rows = self.options.rows or 60
		self.cur_row = -1
		self.curpage = 0 # page start from 1
		self.freeze_grid = None
		self.normal_grid = None
		self.freeze_fields = [ f for f in self.options.fields if  f.freeze and not f.hidden ]
		self.normal_fields = [ f for f in self.options.fields if not f.freeze and not f.hidden ]
		if len(self.freeze_fields) > 0:
			self.freeze_grid = self.buildGrid(self.freeze_field,freeze=True)
			self.add_widget(self.freeze_grid)

		if len(self.normal_fields) > 0:
			self.normal_grid = self.buildGrid(self.normal_fields,freeze=False)
			self.add_widget(self.normal_grid)
		Clock.schedule_once(self.loadData, 1)
		if self.freeze_grid:
			self.freeze_grid.body.scroll_y = 1
		if self.normal_grid:
			self.normal_grid.body.scroll_y = 1
	
	def buildGrid(self,fields,freeze=False):
		if freeze:
			grid = DataGrid()
		else:
			grid = ScrollDataGrid()
		fielddescs = []
		width = 0
		height = 40
		for f in fields:
			x = {
				'text':f.label,
				'type':'Label',
				'width':f.width or 100
			}
			width = width + x['width']
			fielddescs.append(x)
		grid.setupGrid(fielddescs,width,height)
		return grid

	def addRow(self,grid,r,freeze=False):
		fds = [] 
		fields = self.freeze_fields if freeze else self.normal_fields
		for f in fields:
			v = r[f.name]
			if v is None:
				v = ''
			else:
				v = str(v)
			x = {
				'text':v,
				'type':'Label'
				}
			fds.append(x)
		grid.addRow(fds)

	def loadData(self,page):
		def showData(obj,d):
			print('callback(), **********',obj,d)
			d = DictObject(**d)
			if d is None:
				raise Exception
			self.total_cnt = d.total
			for r in d.rows:
				if self.freeze_grid is not None:	
					self.addRow(self.freeze_grid,r,freeze=True)
				self.addRow(self.normal_grid,r)
		
		url = self.options.get('dataurl') + '?page=%d&rows=%d' % (page,self.page_rows)
		parenturl = None
		if hasattr(self,'parenturl'):
			parenturl = self.parenturl
		url = absurl(url,parenturl)
		print('*****url=',url,'*******')
		d = App.get_running_app().hc.get(url,callback=showData)
		print('*****keep going*******',d)

