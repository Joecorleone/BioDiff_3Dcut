'''
TODO
improve speed:
	use digitize to fill grid !!!!!!!!!!!!!

change plot dialog:
	add logIntens option
	integrate image over area -> 1d graph next to image
'''
import wx
import os
import numpy as np
import cPickle as pickle
import biodiffPlot_lib as bdL
import biodiffPlot_util as bdU

listScanSets = {}
listScanSetsID = {}
listGrids = {}
listGridsID = {}
listCuts = {}
listCutsID = {}


# menu entries for scanSet
menu_titles_scanSet = [ "Info", "Remove"]
menu_title_scanSet_by_id = {}
for title in menu_titles_scanSet:
    menu_title_scanSet_by_id[ wx.NewId() ] = title

# menu entries for grid
menu_titles_grid = [ "Info", "Remove", "Save" ]
menu_title_grid_by_id = {}
for title in menu_titles_grid:
    menu_title_grid_by_id[ wx.NewId() ] = title
    
# menu entries for cut
menu_titles_cut = [ "Info", "Remove", "Save", "Plot", "Export"]
menu_title_cut_by_id = {}
for title in menu_titles_cut:
    menu_title_cut_by_id[ wx.NewId() ] = title
    

class MainFrame(wx.Frame):
    '''
    1. read a predefined file which holds the information about the scans to be used (not the .set file)
	(-> adds scan set to a list of scan sets)
	-> check consistency and display information
	right click: info, remove
	
    2. create a grid and fill it, or load from file (2 buttons):
	(-> creates a large object with 2 large numpy arrays)
	-> open window, to ask for name, limits/steps, which scanset should be used to populate and how many interpolation steps
	-> right click on grid: info, remove, save (cPickle)

    3. create cut on grid, or load from file (2 buttons):
	(-> smaller object)
	-> open window for limits and integration axis
	-> right click on cut: info, remove, save, plot, export
    '''
	
    def __init__(self, *args, **kwargs):
	wx.Frame.__init__(self, *args, **kwargs)#, 
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # create the menubar
	menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

	# create the statusbar
        self.statusbar = self.CreateStatusBar()
        
	
	vboxsizer = wx.BoxSizer(orient = wx.VERTICAL)
	s1panel =  Step1Panel(self)
	s2panel =  Step2Panel(self)
	s3panel =  Step3Panel(self)
	vboxsizer.Add(s1panel, 1, flag=wx.ALL|wx.EXPAND, border=5)
	vboxsizer.Add(s2panel, 1, flag=wx.ALL|wx.EXPAND, border=5)
	vboxsizer.Add(s3panel, 1, flag=wx.ALL|wx.EXPAND, border=5)


	
	self.SetAutoLayout(True)
	self.SetSizer(vboxsizer)
	self.Layout()
	#self.Fit()
   
   
   
    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Close()
        if result == wx.ID_OK:
            self.Destroy()
            
  
 
 
class Step1Panel(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		"""Create the DemoPanel."""
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		 # Step 1: read the information on scan sets
		hbox = wx.StaticBox(self, label = 'Step 1: Load scan set files')       
		hboxsizer = wx.StaticBoxSizer(hbox, orient=wx.HORIZONTAL)
			
		# left side
		vboxsizer1 = wx.BoxSizer(wx.VERTICAL)
		bt_readScanSet = wx.Button(self, -1, "Load file")	
		bt_readScanSet.Bind(wx.EVT_BUTTON, self.on_readScanSet)
		vboxsizer1.Add(bt_readScanSet, flag=wx.ALL|wx.EXPAND, border=5)
		
		hboxsizer.Add(vboxsizer1,flag=wx.CENTER)
		
		
		# right side
		vboxsizer2 = wx.BoxSizer(wx.VERTICAL)
		staticText = wx.StaticText(self, label = 'Scan set files:')
		# list box with all read scan sets, right click remove and info
		self.loadedScanSets = wx.ListCtrl(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.loadedScanSets.InsertColumn(0, 'filename')
		self.loadedScanSets.InsertColumn(1, 'scans')
		self.loadedScanSets.SetColumnWidth(0, width = 168)
		self.loadedScanSets.SetColumnWidth(1, width = 50)
		vboxsizer2.Add(staticText,0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizer2.Add(self.loadedScanSets,1, flag=wx.ALL|wx.EXPAND, border=5)
		
		# register right click
		wx.EVT_LIST_ITEM_RIGHT_CLICK( self.loadedScanSets, -1, self.RightClickCb )
		# clear variables
		self.list_item_clicked = None
		
		hboxsizer.Add(vboxsizer2,1, flag=wx.ALL|wx.EXPAND, border=5)
		
		self.SetSizer(hboxsizer,1)
		
	def on_readScanSet(self, event):	    
		dlg= wx.FileDialog(parent=self, message="Choose a scan set file", wildcard="ScanSet|*|All|*", style=wx.OPEN)
		value = dlg.ShowModal()
		filePath = dlg.GetPath()
		filename = dlg.GetFilename()
		directory = filePath.rstrip(filename)
		if value == wx.ID_OK and os.path.isfile(filePath):
			scanSet=bdL.readScanFile(filePath)
			scanSet.setDirectory(directory)
			self.addScanSet(filename,scanSet)
		dlg.Close()
			
	def addScanSet(self,scanSetName,scanSet):
		self.loadedScanSets.Append([scanSetName,scanSet.numberOfScans])
		listScanSetsID[scanSetName] = len(listScanSets)
		listScanSets[scanSetName] = scanSet
		
		
	def removeScanSet(self,scanSetName):
		self.loadedScanSets.DeleteItem(listScanSetsID[scanSetName])
		del listScanSets[scanSetName]
		del listScanSetsID[scanSetName]
	
	def showInfo(self,scanSetName):
		info = scanSetInfoDialog(self, title='Info on %s' %scanSetName, selectedScanSet = listScanSets[scanSetName])
		info.ShowModal()
		info.Close()
		return
			
	def RightClickCb( self, event ):
		# record what was clicked
		self.list_item_clicked = right_click_context = event.GetText()

		if self.list_item_clicked != '':
			### 2. Launcher creates wxMenu. ###
			menu = wx.Menu()
			for (id,title) in menu_title_scanSet_by_id.items():
				### 3. Launcher packs menu with Append. ###
				menu.Append( id, title )
				### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
				wx.EVT_MENU( menu, id, self.MenuSelectionCb )

			### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
			self.loadedScanSets.PopupMenu( menu, event.GetPoint() )
			menu.Destroy() # destroy to avoid mem leak
			
	
	def MenuSelectionCb( self, event ):
		# do something
		operation = menu_title_scanSet_by_id[ event.GetId() ]
		target    = self.list_item_clicked
		if operation == 'Info':
			self.showInfo(target)
		elif operation == 'Remove':
			self.removeScanSet(target)
			
class scanSetInfoDialog(wx.Dialog):
	def __init__(self, parent, title, selectedScanSet):
		super(scanSetInfoDialog, self).__init__(parent=parent, title=title, size=(250, 520))

		self.parent = parent
		self.panel = wx.Panel(self, wx.ID_ANY)
		scan = selectedScanSet
		vboxsizerPanel = wx.BoxSizer(orient = wx.VERTICAL)
		vboxInfo = wx.StaticBox(self.panel, -1, 'Info')
		vboxsizerInfo = wx.StaticBoxSizer(vboxInfo, orient=wx.VERTICAL)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Proposal number: %s' %scan.experimentProposal),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Experiment title: %s' %scan.experimentTitle),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Experiment remark: %s' %scan.experimentRemark),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Scan number: %s' %scan.scanNumber),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Scan command: %s' %scan.scanCommand),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Start time: %s' %scan.startTime),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'Number of scans: %s (available %i)' %(scan.numberOfScans,scan.checkFiles())),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'File path: %s' %scan.filePath),0, flag=wx.ALL|wx.EXPAND, border=5)
		
		vboxsizerPanel.Add(vboxsizerInfo,0, flag=wx.ALL|wx.EXPAND, border=5)
		#vboxsizerPanel.Add(wx.StaticText(self, -1, 'Available images: %s' %scan.filePath),0, flag=wx.ALL|wx.EXPAND, border=5)
		#self.SetSizeHints(250,300,500,600)
	
		self.panel.SetSizer(vboxsizerPanel)
		vboxsizerPanel.Fit(self)
		
class Step2Panel(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		"""Create the DemoPanel."""
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		# Step 2: create a grid
		hbox = wx.StaticBox(self, -1, 'Step 2: Create grids')
		hboxsizer = wx.StaticBoxSizer(hbox, orient=wx.HORIZONTAL)
		
		# left side
		vboxsizer1 = wx.BoxSizer(wx.VERTICAL)
		bt_newGrid = wx.Button(self, -1, "New grid")	
		bt_newGrid.Bind(wx.EVT_BUTTON, self.on_newGrid)
		bt_loadGrid = wx.Button(self, -1, "Load grid")	
		bt_loadGrid.Bind(wx.EVT_BUTTON, self.on_loadGrid)
		vboxsizer1.Add(bt_newGrid, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizer1.Add(bt_loadGrid, flag=wx.ALL|wx.EXPAND, border=5)
		
		hboxsizer.Add(vboxsizer1,flag=wx.CENTER)
		
		# right side
		vboxsizer2 = wx.BoxSizer(wx.VERTICAL)
		staticText = wx.StaticText(self, -1, 'Grids:')
		# list box available grids
		self.availableGrids = wx.ListCtrl(self, style=wx.LC_LIST|wx.SUNKEN_BORDER)
		vboxsizer2.Add(staticText,0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizer2.Add(self.availableGrids,1, flag=wx.ALL|wx.EXPAND, border=5)
		
		# register right click
		wx.EVT_LIST_ITEM_RIGHT_CLICK( self.availableGrids, -1, self.RightClickCb )
		# clear variables
		self.list_item_clicked = None
		
		
		hboxsizer.Add(vboxsizer2,1, flag=wx.ALL|wx.EXPAND, border=5)
		self.SetSizer(hboxsizer)
		
	def on_newGrid(self,event):
		grid = gridDialog(self, title='Create new grid')
		grid.ShowModal()
		grid.Close()
		return
            
	def on_loadGrid(self,event):
		dlg= wx.FileDialog(parent=self, message="Choose a grid file", wildcard="Grid|*.grid|All|*", style=wx.OPEN)
		value = dlg.ShowModal()
		filePath = dlg.GetPath()
		filename = dlg.GetFilename()
		if value == wx.ID_OK and os.path.isfile(filePath):
			if filename.endswith('.grid'):
				filename = filename.rstrip('.grid')
			with open(filePath, "rb") as input_file:
				newGrid = pickle.load(input_file)
				self.addGrid(filename,newGrid)
		dlg.Close()
		
	def showInfo(self,gridName):
		info = gridInfoDialog(self, title='Info on %s' %gridName, selectedGrid = listGrids[gridName])
		info.ShowModal()
		info.Close()   
		return

	def addGrid(self,gridName,histoGrid):
		self.availableGrids.Append([gridName])
		listGridsID[gridName] = len(listGrids)
		listGrids[gridName] = histoGrid
		
	def removeGrid(self,gridName):
		self.availableGrids.DeleteItem(listGridsID[gridName])
		del listGrids[gridName]
		del listGridsID[gridName]
		
	def saveGrid(self,gridName):
		dlg= wx.FileDialog(parent=self, message="Save grid", wildcard="Grid|*.grid|All|*", style=wx.SAVE)
		dlg.SetFilename('%s.grid' %gridName)
		value = dlg.ShowModal()
		filePath = dlg.GetPath()
		if value == wx.ID_OK:
			with open(filePath, 'wb') as output:
				pickle.dump(listGrids[gridName], output, pickle.HIGHEST_PROTOCOL)
		dlg.Close()
		
		
	def RightClickCb( self, event ):
		# record what was clicked
		self.list_item_clicked = right_click_context = event.GetText()

		if self.list_item_clicked != '':
			### 2. Launcher creates wxMenu. ###
			menu = wx.Menu()
			for (id,title) in menu_title_grid_by_id.items():
				### 3. Launcher packs menu with Append. ###
				menu.Append( id, title )
				### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
				wx.EVT_MENU( menu, id, self.MenuSelectionCb )

			### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
			self.availableGrids.PopupMenu( menu, event.GetPoint() )
			menu.Destroy() # destroy to avoid mem leak
		
	def MenuSelectionCb( self, event ):
		# do something
		operation = menu_title_grid_by_id[ event.GetId() ]
		target    = self.list_item_clicked
		if operation == 'Info':
			self.showInfo(target)
		elif operation == 'Remove':
			self.removeGrid(target)
		elif operation == 'Save':
			self.saveGrid(target)

class gridInfoDialog(wx.Dialog):
	def __init__(self, parent, title, selectedGrid):
		super(gridInfoDialog, self).__init__(parent=parent, title=title, size=(250, 520))

		self.parent = parent
		self.panel = wx.Panel(self, wx.ID_ANY)
		grid = selectedGrid
		vboxsizerPanel = wx.BoxSizer(orient = wx.VERTICAL)
		vboxInfo = wx.StaticBox(self.panel, -1, 'Info')
		vboxsizerInfo = wx.StaticBoxSizer(vboxInfo, orient=wx.VERTICAL)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'x-Axis: from %f to %f in %f' %(grid.minQx,grid.maxQx,grid.deltaQx)),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'y-Axis: from %f to %f in %f' %(grid.minQy,grid.maxQy,grid.deltaQy)),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'z-Axis: from %f to %f in %f' %(grid.minQz,grid.maxQz,grid.deltaQz)),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'filled with scans from:  %s' %(', '.join(grid.usedScanSets))),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'omega offset:  %f'  %grid.omegaOffset     )	,0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'interpolation:  %f' %grid.interpolationNum)	,0, flag=wx.ALL|wx.EXPAND, border=5)
		
		
		vboxsizerPanel.Add(vboxsizerInfo,0, flag=wx.ALL|wx.EXPAND, border=5)
		#vboxsizerPanel.Add(wx.StaticText(self, -1, 'Available images: %s' %scan.filePath),0, flag=wx.ALL|wx.EXPAND, border=5)
		#self.SetSizeHints(250,300,500,600)
	
		self.panel.SetSizer(vboxsizerPanel)
		vboxsizerPanel.Fit(self)
		
    
class gridDialog(wx.Dialog):
	def __init__(self, parent, title):
		super(gridDialog, self).__init__(parent=parent, title=title, size=(250, 520))

		self.parent = parent
		self.panel = wx.Panel(self, wx.ID_ANY)
		vboxsizerPanel = wx.BoxSizer(orient = wx.VERTICAL)
		
		# name for grid:
		vboxsizerPanel.AddSpacer(5,5)
		vboxsizerName = wx.BoxSizer(orient=wx.HORIZONTAL)
		tx_name = wx.StaticText(self.panel, wx.ID_ANY, 'Name for grid')
		self.tx_name = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		vboxsizerName.AddSpacer(5,1)
		vboxsizerName.Add(tx_name, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vboxsizerName.AddSpacer(5,1)
		vboxsizerName.Add(self.tx_name, 1, wx.ALL|wx.EXPAND, 5)
		vboxsizerPanel.Add(vboxsizerName, 0, wx.ALL|wx.EXPAND, 5)
	
		# Define Grid:
		vboxGrid = wx.StaticBox(self.panel, -1, 'Define grid')
		vboxsizerGrid = wx.StaticBoxSizer(vboxGrid, orient=wx.VERTICAL)
		
		gridSizer       = wx.GridSizer(rows=4, cols=4, hgap=5, vgap=5)
		btnSizer        = wx.BoxSizer(wx.HORIZONTAL)
	
		tx_Empty = wx.StaticText(self.panel, wx.ID_ANY, '')
		tx_min = wx.StaticText(self.panel, wx.ID_ANY, 'min')
		tx_max = wx.StaticText(self.panel, wx.ID_ANY, 'max')
		tx_delta = wx.StaticText(self.panel, wx.ID_ANY, 'delta')
	        
	        tx_X = wx.StaticText(self.panel, wx.ID_ANY, 'x-Axis')
		self.tx_Xmin = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		self.tx_Xmax = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		self.tx_Xdelta = wx.TextCtrl(self.panel, wx.ID_ANY,'')
	
		tx_Y = wx.StaticText(self.panel, wx.ID_ANY, 'y-Axis')
		self.tx_Ymin = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		self.tx_Ymax = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		self.tx_Ydelta = wx.TextCtrl(self.panel, wx.ID_ANY,'')
	
		tx_Z = wx.StaticText(self.panel, wx.ID_ANY, 'z-Axis')
		self.tx_Zmin = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		self.tx_Zmax = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		self.tx_Zdelta = wx.TextCtrl(self.panel, wx.ID_ANY,'')
	
	
		gridSizer.Add(tx_Empty, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		# Set the TextCtrl to expand on resize
		gridSizer.Add(tx_min, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		gridSizer.Add(tx_max, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		gridSizer.Add(tx_delta, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		gridSizer.Add(tx_X, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		gridSizer.Add(self.tx_Xmin, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Xmax, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Xdelta, 0, wx.EXPAND)
		gridSizer.Add(tx_Y, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		gridSizer.Add(self.tx_Ymin, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Ymax, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Ydelta, 0, wx.EXPAND)
		gridSizer.Add(tx_Z, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		gridSizer.Add(self.tx_Zmin, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Zmax, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Zdelta, 0, wx.EXPAND)
	
		vboxsizerGrid.Add(gridSizer, 0, wx.ALL|wx.EXPAND, 5)
		vboxsizerPanel.Add(vboxsizerGrid, 0, wx.ALL|wx.EXPAND, 5)
		
		# scans overview
		vboxScans = wx.StaticBox(self.panel, -1, 'Fill grid with scans')
		vboxsizerScans = wx.StaticBoxSizer(vboxScans, orient=wx.VERTICAL)
		 
		vboxsizerCheckBoxes = wx.BoxSizer(orient=wx.VERTICAL)
		#text = wx.StaticText(self.panel, wx.ID_ANY, 'huhu')
		if len(listScanSets)>0:
			self.checkBoxesScans = []
			for i,(scanName,scanSet) in enumerate(listScanSets.iteritems()):
				checkBoxScan = wx.CheckBox(self.panel, 1 ,label = '%s with %i scans' %(scanName,scanSet.numberOfScans))
				self.checkBoxesScans.append(checkBoxScan)
				vboxsizerCheckBoxes.Add(checkBoxScan, 0, wx.ALL|wx.EXPAND, 5)
		else:
			vboxsizerCheckBoxes.Add(wx.StaticText(self.panel, wx.ID_ANY, 'No scans have been loaded yet!'))
		vboxsizerScans.Add(vboxsizerCheckBoxes, 0, wx.ALL|wx.EXPAND, 5)
		vboxsizerPanel.Add(vboxsizerScans, 0, wx.ALL|wx.EXPAND, 5)
		
		# additional options
		vboxOptions = wx.StaticBox(self.panel, -1, 'Additional options')
		vboxsizerOptions = wx.StaticBoxSizer(vboxOptions, orient=wx.VERTICAL)
		
		# 1. omega Offset
		hboxsizerOffset = wx.BoxSizer(orient=wx.HORIZONTAL)
		hboxsizerOffset.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Omega offset'),0,wx.ALIGN_CENTER_VERTICAL,5)
		self.numtextOmega = bdU.NumericTextfield(self.panel, -1, '0',allowFloat=True)
		hboxsizerOffset.Add(self.numtextOmega, 0, wx.ALL|wx.EXPAND, 5)
		vboxsizerOptions.Add(hboxsizerOffset, 0, wx.ALL|wx.EXPAND, 5)
		
		# 2. interpolate
		hboxsizerInterpolate = wx.BoxSizer(orient=wx.HORIZONTAL)
		hboxsizerInterpolate.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Interpolations steps'),0,wx.ALIGN_CENTER_VERTICAL,5)
		self.spinctrlInterpolate = wx.SpinCtrl(self.panel, -1, '0', min=0, max=20)
		hboxsizerInterpolate.Add(self.spinctrlInterpolate, 0, wx.ALL|wx.EXPAND, 5)
		vboxsizerOptions.Add(hboxsizerInterpolate, 0, wx.ALL|wx.EXPAND, 5)
		
		# 3. check for shifts
		self.checkBoxShifts = wx.CheckBox(self.panel, 1 ,label = 'Correct shifts of detector image')
		self.checkBoxShifts.SetValue(False)
		vboxsizerOptions.Add(self.checkBoxShifts, 0, wx.ALL|wx.EXPAND, 5)
		vboxsizerPanel.Add(vboxsizerOptions, 0, wx.ALL|wx.EXPAND, 5)
		
		# Buttons
		okBtn = wx.Button(self.panel, wx.ID_ANY, 'OK')
		cancelBtn = wx.Button(self.panel, wx.ID_ANY, 'Cancel')
		self.Bind(wx.EVT_BUTTON, self.on_OK, okBtn)
		self.Bind(wx.EVT_BUTTON, self.on_Cancel, cancelBtn)
		btnSizer.Add(okBtn, 0, wx.ALL, 5)
		btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
			
		vboxsizerPanel.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)
	
		# SetSizeHints(minW, minH, maxW, maxH)
		self.SetSizeHints(250,300,500,600)
	
		self.panel.SetSizer(vboxsizerPanel)
		vboxsizerPanel.Fit(self)
		
	def on_OK(self, event):
		minQx   = None if self.tx_Xmin.GetValue()   == '' else float(self.tx_Xmin.GetValue())
		maxQx   = None if self.tx_Xmax.GetValue()   == '' else float(self.tx_Xmax.GetValue())
		deltaQx = None if self.tx_Xdelta.GetValue() == '' else float(self.tx_Xdelta.GetValue())
		minQy   = None if self.tx_Ymin.GetValue()   == '' else float(self.tx_Ymin.GetValue())
		maxQy   = None if self.tx_Ymax.GetValue()   == '' else float(self.tx_Ymax.GetValue())
		deltaQy = None if self.tx_Ydelta.GetValue() == '' else float(self.tx_Ydelta.GetValue())
		minQz   = None if self.tx_Zmin.GetValue()   == '' else float(self.tx_Zmin.GetValue())
		maxQz   = None if self.tx_Zmax.GetValue()   == '' else float(self.tx_Zmax.GetValue())
		deltaQz = None if self.tx_Zdelta.GetValue() == '' else float(self.tx_Zdelta.GetValue())
		
		if self.tx_name.GetValue() == '':
			print 'Specify a name!'
			return
		else:
			gridName = self.tx_name.GetValue()
					
		if (minQx is None or maxQx is None or deltaQx is None or
			minQy is None or maxQy is None or deltaQy is None or
			minQz is None or maxQz is None or deltaQz is None):
			print 'Fill all text fields!'
			return
		
		shiftedImages = self.checkBoxShifts.GetValue()
		print shiftedImages
		
				
		if len(listScanSets)>0:
                    selectedScanSets = []
                    scanNames = []
                    for checkBox,(scanName,scanSet) in zip(self.checkBoxesScans,listScanSets.iteritems()):
                        if checkBox.GetValue():
                            selectedScanSets.append(scanSet)
                            scanNames.append(scanName)
                    if len(selectedScanSets)>0:
                        omega_offset = self.numtextOmega.GetFloatValue()
                        kincident, omegas, imagefiles = bdL.getKiOmegasAndFiles(selectedScanSets,omega_offset)
                        QstarArray = bdL.createScanPattern(kincident,imagefiles[0])
                        numInterpol = self.spinctrlInterpolate.GetValue() #number of additional interpolation steps
                        histoGrid = bdL.grid(minQx,maxQx,deltaQx,minQy,maxQy,deltaQy,minQz,maxQz,deltaQz,scanNames,omega_offset,float(numInterpol))
                                                        
                        pulse_dlg = None#wx.ProgressDialog(title="Filling Grid", message="with scan:", maximum=100, style = wx.PD_AUTO_HIDE|wx.PD_APP_MODAL|wx.PD_REMAINING_TIME)
                        histoGrid.fillGrid(kincident,omegas,imagefiles,QstarArray,numInterpol,shiftedImages,pulse_dlg,verbose =True)
                        #pulse_dlg.Close()
                        
                        self.parent.addGrid(gridName,histoGrid)
                        
                        self.Close()
                        return gridName
                    else: 
                            print 'Select at least one scan set!'
                            return 
		else:
			# show warning, that no scansets were selected
			pass
		
	
		
		## Some stuff happens
		#for i in range(10):
		#wx.MilliSleep(250)
		#
			
	def on_Cancel(self, event):
		self.Close()
		

	
		
    
    
class Step3Panel(wx.Panel):
	def __init__(self, parent, *args, **kwargs):
		"""Create the DemoPanel."""
		wx.Panel.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		# Step 3: create a cut
		hbox = wx.StaticBox(self, -1, 'Step 3: Create cuts')
		hboxsizer = wx.StaticBoxSizer(hbox, orient=wx.HORIZONTAL)

		# left side
		vboxsizer1 = wx.BoxSizer(wx.VERTICAL)
		bt_newCut = wx.Button(self, -1, "New cut")	
		bt_newCut.Bind(wx.EVT_BUTTON, self.on_newCut)
		bt_loadCut = wx.Button(self, -1, "Load cut")	
		bt_loadCut.Bind(wx.EVT_BUTTON, self.on_loadCut)
		vboxsizer1.Add(bt_newCut, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizer1.Add(bt_loadCut, flag=wx.ALL|wx.EXPAND, border=5)
		
		hboxsizer.Add(vboxsizer1,flag=wx.CENTER)
		
		# right side
		vboxsizer2 = wx.BoxSizer(wx.VERTICAL)
		staticText = wx.StaticText(self, -1, 'Cuts:')
		# list box with all created cuts, right click remove and info
		self.availableCuts = wx.ListCtrl(self, style=wx.LC_LIST|wx.SUNKEN_BORDER)
		vboxsizer2.Add(staticText,0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizer2.Add(self.availableCuts,1, flag=wx.ALL|wx.EXPAND, border=5)
		
		# register right click
		wx.EVT_LIST_ITEM_RIGHT_CLICK( self.availableCuts, -1, self.RightClickCb )
		# clear variables
		self.list_item_clicked = None
		
		hboxsizer.Add(vboxsizer2,1, flag=wx.ALL|wx.EXPAND, border=5)
		
		self.SetSizer(hboxsizer,1)

	
	def on_newCut(self,event):
		grid = cutDialog(self, title='Create new cut')
		grid.ShowModal()
		grid.Close()   
		return
	
	def on_loadCut(self,event):
		dlg= wx.FileDialog(parent=self, message="Choose a cut file", wildcard="Cut|*.cut|All|*", style=wx.OPEN)
		value = dlg.ShowModal()
		filePath = dlg.GetPath()
		filename = dlg.GetFilename()
		if value == wx.ID_OK and os.path.isfile(filePath):
			if filename.endswith('.cut'):
				filename = filename.rstrip('.cut')
			with open(filePath, "rb") as input_file:
				newCut = pickle.load(input_file)
				self.addCut(filename,newCut) 
		dlg.Close()
		
	def showInfo(self,cutName):
		info = cutInfoDialog(self, title='Info on %s' %cutName, selectedCut = listCuts[cutName])
		info.ShowModal()
		info.Close()   
		return
    
	def addCut(self,cutName,cut):
		self.availableCuts.Append([cutName])
		listCutsID[cutName] = len(listCuts)
		listCuts[cutName] = cut

	def removeCut(self,cutName):
		self.availableCuts.DeleteItem(listCutsID[cutName])
		del listCuts[cutName]
		del listCutsID[cutName]
		
	def saveCut(self,cutName):
		dlg= wx.FileDialog(parent=self, message="Save cut", wildcard="Cut|*.cut|All|*", style=wx.SAVE)
		dlg.SetFilename('%s.cut' %cutName)
		value = dlg.ShowModal()
		filePath = dlg.GetPath()
		if value == wx.ID_OK:
			with open(filePath, 'wb') as output:
				pickle.dump(listCuts[cutName], output, pickle.HIGHEST_PROTOCOL)
		dlg.Close()
		
	def exportCut(self,cutName):
		dlg= wx.FileDialog(parent=self, message="Export cut as a map", wildcard="Map|*.map|All|*", style=wx.SAVE)
		dlg.SetFilename('%s.map' %cutName)
		value = dlg.ShowModal()
		filePath = dlg.GetPath()
		if value == wx.ID_OK:
			
			pulse_dlg = wx.ProgressDialog(title="Saving cut", message=" ", maximum=100, style = wx.PD_AUTO_HIDE|wx.PD_APP_MODAL|wx.PD_REMAINING_TIME)
			bdL.createOutputFile(listCuts[cutName],filePath,True,pulse_dlg)
			pulse_dlg.Close()
		dlg.Close()
			
	def plotCut(self,cutName):
		plot = plotDialog(self, title='Plot cut %s' %cutName, selectedCut = listCuts[cutName])
		plot.ShowModal()
		plot.Close()   
		return
	
	def RightClickCb( self, event ):
		# record what was clicked
		self.list_item_clicked = right_click_context = event.GetText()
		
		if self.list_item_clicked != '':
			### 2. Launcher creates wxMenu. ###
			menu = wx.Menu()
			for (id,title) in menu_title_cut_by_id.items():
				### 3. Launcher packs menu with Append. ###
				menu.Append( id, title )
				### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
				wx.EVT_MENU( menu, id, self.MenuSelectionCb )

			### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
			self.availableCuts.PopupMenu( menu, event.GetPoint() )
			menu.Destroy() # destroy to avoid mem leak

	def MenuSelectionCb( self, event ):
		# do something
		operation = menu_title_cut_by_id[ event.GetId() ]
		target    = self.list_item_clicked
		if operation == 'Info':
			self.showInfo(target)
		elif operation == 'Remove':
			self.removeCut(target)
		elif operation == 'Save':
			self.saveCut(target)
		elif operation == 'Plot':
			self.plotCut(target)
		elif operation == 'Export':
			self.exportCut(target)


	
class cutInfoDialog(wx.Dialog):
	def __init__(self, parent, title, selectedCut):
		super(cutInfoDialog, self).__init__(parent=parent, title=title, size=(250, 520))

		self.parent = parent
		self.panel = wx.Panel(self, wx.ID_ANY)
		cut = selectedCut
		vboxsizerPanel = wx.BoxSizer(orient = wx.VERTICAL)
		vboxInfo = wx.StaticBox(self.panel, -1, 'Info')
		vboxsizerInfo = wx.StaticBoxSizer(vboxInfo, orient=wx.VERTICAL)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'type: %s' %(cut.cutType)),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'first axis: from %f to %f' %(cut.axis1min,cut.axis1max)),0, flag=wx.ALL|wx.EXPAND, border=5)
		vboxsizerInfo.Add(wx.StaticText(self.panel, -1, 'second axis: from %f to %f' %(cut.axis2min,cut.axis2max)),0, flag=wx.ALL|wx.EXPAND, border=5)

		vboxsizerPanel.Add(vboxsizerInfo,0, flag=wx.ALL|wx.EXPAND, border=5)
		#vboxsizerPanel.Add(wx.StaticText(self, -1, 'Available images: %s' %scan.filePath),0, flag=wx.ALL|wx.EXPAND, border=5)
		#self.SetSizeHints(250,300,500,600)
	
		self.panel.SetSizer(vboxsizerPanel)
		vboxsizerPanel.Fit(self)

########################################################################
class IntegratingCutTab(wx.Panel):
    """
    Tab holding the widgets for creating a cut integrating over a specified axis
    """
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        gridSizer       = wx.GridSizer(rows=4, cols=3, hgap=5, vgap=5)
        #column names
	tx_integrate = wx.StaticText(self, wx.ID_ANY, 'integrate')
	tx_min = wx.StaticText(self, wx.ID_ANY, 'min')
	tx_max = wx.StaticText(self, wx.ID_ANY, 'max')		
	
	self.rb_xaxis = wx.RadioButton(self, -1, label = 'x-Axis', style=wx.RB_GROUP)
	self.tx_Xmin = wx.TextCtrl(self, wx.ID_ANY,'')
	self.tx_Xmax = wx.TextCtrl(self, wx.ID_ANY,'')
	
	self.rb_yaxis = wx.RadioButton(self, -1, 'y-Axis')
	self.tx_Ymin = wx.TextCtrl(self, wx.ID_ANY,'')
	self.tx_Ymax = wx.TextCtrl(self, wx.ID_ANY,'')
		
	self.rb_zaxis = wx.RadioButton(self, -1, 'z-Axis')
	self.tx_Zmin = wx.TextCtrl(self, wx.ID_ANY,'')
	self.tx_Zmax = wx.TextCtrl(self, wx.ID_ANY,'')

	gridSizer.Add(tx_integrate, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
	gridSizer.Add(tx_min, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
	gridSizer.Add(tx_max, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
	
	gridSizer.Add(self.rb_xaxis, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
	gridSizer.Add(self.tx_Xmin, 0, wx.EXPAND)
	gridSizer.Add(self.tx_Xmax, 0, wx.EXPAND)		
	
	gridSizer.Add(self.rb_yaxis, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
	gridSizer.Add(self.tx_Ymin, 0, wx.EXPAND)
	gridSizer.Add(self.tx_Ymax, 0, wx.EXPAND)		
	
	gridSizer.Add(self.rb_zaxis, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
	gridSizer.Add(self.tx_Zmin, 0, wx.EXPAND)
	gridSizer.Add(self.tx_Zmax, 0, wx.EXPAND)

	self.SetSizer(gridSizer)
	
	
class SlidingCutTab(wx.Panel):
	"""
	Tab holding the widgets for creating a cut sliding along a specified axis
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		gridSizer       = wx.GridSizer(rows=4, cols=4, hgap=5, vgap=5)
		#column names
		tx_integrate = wx.StaticText(self, wx.ID_ANY, 'sliding')
		tx_min  = wx.StaticText(self, wx.ID_ANY, 'min')
		tx_max  = wx.StaticText(self, wx.ID_ANY, 'max')		
		tx_step = wx.StaticText(self, wx.ID_ANY, 'step')		
		
		self.rb_xaxis = wx.RadioButton(self, -1, label = 'x-Axis', style=wx.RB_GROUP)
		self.Bind(wx.EVT_RADIOBUTTON, self.switchSlidingAxis, self.rb_xaxis)
		self.tx_Xmin  = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Xmax  = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Xstep = wx.TextCtrl(self, wx.ID_ANY,'')
		
		self.rb_yaxis = wx.RadioButton(self, -1, 'y-Axis')
		self.Bind(wx.EVT_RADIOBUTTON, self.switchSlidingAxis, self.rb_yaxis)
		self.tx_Ymin  = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Ymax  = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Ystep = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Ystep.Enable(False)
			
		self.rb_zaxis = wx.RadioButton(self, -1, 'z-Axis')
		self.Bind(wx.EVT_RADIOBUTTON, self.switchSlidingAxis, self.rb_zaxis)
		self.tx_Zmin  = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Zmax  = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Zstep = wx.TextCtrl(self, wx.ID_ANY,'')
		self.tx_Zstep.Enable(False)

		gridSizer.Add(tx_integrate, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		gridSizer.Add(tx_min,  0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		gridSizer.Add(tx_max,  0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		gridSizer.Add(tx_step, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)
		
		gridSizer.Add(self.rb_xaxis, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
		gridSizer.Add(self.tx_Xmin, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Xmax, 0, wx.EXPAND)	
		gridSizer.Add(self.tx_Xstep, 0, wx.EXPAND)
		
		gridSizer.Add(self.rb_yaxis, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
		gridSizer.Add(self.tx_Ymin, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Ymax, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Ystep, 0, wx.EXPAND)
		
		gridSizer.Add(self.rb_zaxis, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
		gridSizer.Add(self.tx_Zmin, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Zmax, 0, wx.EXPAND)
		gridSizer.Add(self.tx_Zstep, 0, wx.EXPAND)

		self.SetSizer(gridSizer)
	
	def switchSlidingAxis(self,event):
		if self.rb_xaxis.GetValue():
			self.tx_Xstep.Enable(True)
			self.tx_Ystep.Enable(False)
			self.tx_Zstep.Enable(False)
		elif self.rb_yaxis.GetValue():
			self.tx_Xstep.Enable(False)
			self.tx_Ystep.Enable(True)
			self.tx_Zstep.Enable(False)
		elif self.rb_zaxis.GetValue():
			self.tx_Xstep.Enable(False)
			self.tx_Ystep.Enable(False)
			self.tx_Zstep.Enable(True)
			

######################################################################
class TabsWidget(wx.Notebook):
    """
    Widget derived from the Notebook class, holding the tabs
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             #wx.BK_DEFAULT
                             wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )

        # Create the first tab and add it to the notebook
        self.tabIntegratingCut = IntegratingCutTab(self)
        self.AddPage(self.tabIntegratingCut, "Integrating")

        # Create and add the second tab
        self.tabSlidingCut = SlidingCutTab(self)
        self.AddPage(self.tabSlidingCut, "Sliding")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()
		

class cutDialog(wx.Dialog):
	def __init__(self, parent, title):
		super(cutDialog, self).__init__(parent=parent, title=title, size=(250, 520))

		self.parent = parent
		self.panel = wx.Panel(self, wx.ID_ANY)
		vboxsizerPanel = wx.BoxSizer(orient = wx.VERTICAL)
		
		# name for cut:
		vboxsizerPanel.AddSpacer(5,5)
		vboxsizerName = wx.BoxSizer(orient=wx.HORIZONTAL)
		tx_name = wx.StaticText(self.panel, wx.ID_ANY, 'Name for cut')
		self.tx_name = wx.TextCtrl(self.panel, wx.ID_ANY,'')
		vboxsizerName.AddSpacer(5,1)
		vboxsizerName.Add(tx_name, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vboxsizerName.AddSpacer(5,1)
		vboxsizerName.Add(self.tx_name, 1, wx.ALL|wx.EXPAND, 5)
		vboxsizerPanel.Add(vboxsizerName, 0, wx.ALL|wx.EXPAND, 5)
		
		# select grid:
		vboxGrid = wx.StaticBox(self.panel, -1, 'Select grid')
		vboxsizerGrid = wx.StaticBoxSizer(vboxGrid, orient=wx.VERTICAL)
		
		if len(listGrids)>0:
			self.radioButtonsGrids = []
			firstRB = True
			for gridName in listGrids:
				if firstRB:
					rb_grid = wx.RadioButton(self.panel, -1, label = gridName, style=wx.RB_GROUP)
					vboxsizerGrid.Add(rb_grid)
					self.radioButtonsGrids.append(rb_grid)
					firstRB = False
				else:
					rb_grid = wx.RadioButton(self.panel, -1, label = gridName)
					vboxsizerGrid.Add(rb_grid)
					self.radioButtonsGrids.append(rb_grid)
		else:
			vboxsizerGrid.Add(wx.StaticText(self.panel, wx.ID_ANY, 'No grid available!'), 0, wx.ALL|wx.EXPAND, 5)
		
		vboxsizerPanel.Add(vboxsizerGrid, 0, wx.ALL|wx.EXPAND, 5)
		
		
		# Define Cut:
		vboxCut = wx.StaticBox(self.panel, -1, 'Define cut')
		vboxsizerCut = wx.StaticBoxSizer(vboxCut, orient=wx.VERTICAL)
		
		# insert textfiles in tabs
		self.tabsWidget = TabsWidget(self.panel)		
		vboxsizerCut.Add(self.tabsWidget, 1, wx.ALL|wx.EXPAND, 5)
		
		
		btnSizer        = wx.BoxSizer(wx.HORIZONTAL)
	
		vboxsizerPanel.Add(vboxsizerCut, 0, wx.ALL|wx.EXPAND, 5)
		
		# Buttons
		okBtn = wx.Button(self.panel, wx.ID_ANY, 'OK')
		cancelBtn = wx.Button(self.panel, wx.ID_ANY, 'Cancel')
		self.Bind(wx.EVT_BUTTON, self.on_OK, okBtn)
		self.Bind(wx.EVT_BUTTON, self.on_Cancel, cancelBtn)
		btnSizer.Add(okBtn, 0, wx.ALL, 5)
		btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
			
		vboxsizerPanel.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)
		


		# SetSizeHints(minW, minH, maxW, maxH)
		self.SetSizeHints(250,200,500,600)
	
		self.panel.SetSizer(vboxsizerPanel)
		vboxsizerPanel.Fit(self)
	
	
	def SetValIntegrate(self, event):
		state1 = str(self.rb_xaxis.GetValue())
		state2 = str(self.rb_yaxis.GetValue())
		state3 = str(self.rb_zaxis.GetValue())
		#self.statusbar.SetStatusText(state1,0)
		#self.statusbar.SetStatusText(state2,1)
		#self.statusbar.SetStatusText(state3,2)
		
	def on_OK(self, event):
		activeTab = self.tabsWidget.GetSelection()
		# tab 0: integrating, tab 1: sliding
		#print activeTab
		tabs = {0: self.tabsWidget.tabIntegratingCut, 1: self.tabsWidget.tabSlidingCut}
		minQx   = None if tabs[activeTab].tx_Xmin.GetValue()   == '' else float(tabs[activeTab].tx_Xmin.GetValue())
		maxQx   = None if tabs[activeTab].tx_Xmax.GetValue()   == '' else float(tabs[activeTab].tx_Xmax.GetValue())
		minQy   = None if tabs[activeTab].tx_Ymin.GetValue()   == '' else float(tabs[activeTab].tx_Ymin.GetValue())
		maxQy   = None if tabs[activeTab].tx_Ymax.GetValue()   == '' else float(tabs[activeTab].tx_Ymax.GetValue())
		minQz   = None if tabs[activeTab].tx_Zmin.GetValue()   == '' else float(tabs[activeTab].tx_Zmin.GetValue())
		maxQz   = None if tabs[activeTab].tx_Zmax.GetValue()   == '' else float(tabs[activeTab].tx_Zmax.GetValue())
		
		
				
		if self.tx_name.GetValue() == '':
			print 'Specify a name!'
			return
		else:
			cutName = self.tx_name.GetValue()
					
				
		if len(listGrids)>0:
			
			for radioButton,(gridName,grid) in zip(self.radioButtonsGrids,listGrids.iteritems()):
				if radioButton.GetValue():
					selectedGrid = grid
			
			if activeTab == 0:
				if self.tabsWidget.tabIntegratingCut.rb_xaxis.GetValue():
					integrateAxis = 'x'
					axis1 = 'Qy'
					axis2 = 'Qz'
				elif self.tabsWidget.tabIntegratingCut.rb_yaxis.GetValue():
					integrateAxis = 'y'
					axis1 = 'Qx'
					axis2 = 'Qz'
				elif self.tabsWidget.tabIntegratingCut.rb_zaxis.GetValue():
					integrateAxis = 'z'
					axis1 = 'Qx'
					axis2 = 'Qy'
				
				cut = bdL.createIntegratingCut(selectedGrid,minQx,maxQx,minQy,maxQy,minQz,maxQz,integrateAxis)
				cut.setAxisLabels(axis1,axis2)
			
				
			elif activeTab == 1:
				tabSlidingCut = self.tabsWidget.tabSlidingCut
				if tabSlidingCut.rb_xaxis.GetValue():
					slidingAxis = 'x'
					axis1 = 'Qy'
					axis2 = 'Qz'
					axis3 = 'Qx'
					slidingStep = None if tabSlidingCut.tx_Xstep.GetValue()  == '' else float(tabSlidingCut.tx_Xstep.GetValue())
				elif tabSlidingCut.rb_yaxis.GetValue():
					slidingAxis = 'y'
					axis1 = 'Qx'
					axis2 = 'Qz'
					axis3 = 'Qy'
					slidingStep = None if tabSlidingCut.tx_Ystep.GetValue()  == '' else float(tabSlidingCut.tx_Ystep.GetValue())
				elif tabSlidingCut.rb_zaxis.GetValue():
					slidingAxis = 'z'
					axis1 = 'Qx'
					axis2 = 'Qy'
					axis3 = 'Qz'
					slidingStep = None if tabSlidingCut.tx_Zstep.GetValue()  == '' else float(tabSlidingCut.tx_Zstep.GetValue())
				
				cut = bdL.createSlidingCut(selectedGrid,minQx,maxQx,minQy,maxQy,minQz,maxQz,slidingAxis,slidingStep)
				cut.setAxisLabels(axis1,axis2,axis3)
				
			self.parent.addCut(cutName,cut)
				
			self.Close()
			
		else:
			# show warning, that no scansets were selected
			pass
    
	def on_Cancel(self, event):
		self.Close()

class plotDialog(wx.Dialog):
	def __init__(self, parent, title, selectedCut):
		super(plotDialog, self).__init__(parent=parent, title=title, size=(1250, 1520))

		self.parent = parent
		self.cut = selectedCut
		
		self.colorPlot = None
		self.colorBar = None
		
		hboxsizerPanel = wx.BoxSizer(orient = wx.HORIZONTAL)
		
		self.leftPanel = wx.Panel(self, wx.ID_ANY)	
		vboxsizerPanel = wx.BoxSizer(orient = wx.VERTICAL)
		
		# Intensity limits
		vboxLimits = wx.StaticBox(self.leftPanel, -1, 'Select intensity limits')
		vboxsizerLimits = wx.StaticBoxSizer(vboxLimits, orient=wx.VERTICAL)
		
		vboxsizerLower = wx.BoxSizer(orient=wx.HORIZONTAL)
		tx_lower = wx.StaticText(self.leftPanel, wx.ID_ANY, 'Lower limit')
		self.tx_lower = wx.TextCtrl(self.leftPanel, wx.ID_ANY,'')
		vboxsizerLower.AddSpacer(5,1)
		vboxsizerLower.Add(tx_lower, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vboxsizerLower.AddSpacer(5,1)
		vboxsizerLower.Add(self.tx_lower, 0, wx.EXPAND)
		vboxsizerLimits.Add(vboxsizerLower, 0, wx.EXPAND)
		
		vboxsizerUpper = wx.BoxSizer(orient=wx.HORIZONTAL)
		tx_upper = wx.StaticText(self.leftPanel, wx.ID_ANY, 'Upper limit')
		self.tx_upper = wx.TextCtrl(self.leftPanel, wx.ID_ANY,'')
		vboxsizerUpper.AddSpacer(5,1)
		vboxsizerUpper.Add(tx_upper, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		vboxsizerUpper.AddSpacer(5,1)
		vboxsizerUpper.Add(self.tx_upper, 0, wx.EXPAND)
		vboxsizerLimits.Add(vboxsizerUpper, 0, wx.EXPAND)
		
		vboxsizerPanel.Add(vboxsizerLimits, 0,wx.ALL| wx.EXPAND,5)
		
		# Buttons
		btnSizer        = wx.BoxSizer(wx.HORIZONTAL)
		plotBtn = wx.Button(self.leftPanel, wx.ID_ANY, 'Plot')
		plotBtn.SetDefault()
		closeBtn = wx.Button(self.leftPanel, wx.ID_ANY, 'Close')
		self.Bind(wx.EVT_BUTTON, self.on_Plot, plotBtn)
		self.Bind(wx.EVT_BUTTON, self.on_Close, closeBtn)
		btnSizer.Add(closeBtn, 0, wx.ALL, 5)
		btnSizer.Add(plotBtn, 0, wx.ALL, 5)
			
		vboxsizerPanel.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)
	
		self.leftPanel.SetSizer(vboxsizerPanel,1)
		vboxsizerPanel.Fit(self.leftPanel)
		hboxsizerPanel.Add(self.leftPanel, 0,wx.ALL| wx.EXPAND,5)
		
		
		self.matplotPanel = MatplotPanel(self)
		hboxsizerPanel.Add(self.matplotPanel, 1,wx.ALL| wx.EXPAND,5)

		if self.cut.cutType == 'slidingCut':
			# add additional slider for switching between plots
			sliderPanel = wx.BoxSizer(orient = wx.VERTICAL)
			sliderPanel.AddStretchSpacer(prop=0.2)
			tx_Axis = wx.StaticText(self, wx.ID_ANY, self.cut.axis3)
			sliderPanel.Add(tx_Axis,0.1, wx.ALIGN_CENTER)
			self.sld = wx.Slider(self, -1, value = 0, minValue = 0, maxValue = len(self.cut.slidingAxis)-1, pos = wx.DefaultPosition,
				size = (-1, 250), style = wx.SL_AUTOTICKS | wx.SL_VERTICAL | wx.SL_INVERSE | wx.SL_RIGHT)
			self.sld.SetTickFreq(1)
			sliderPanel.Add(self.sld, 1, wx.ALIGN_CENTER)
			self.Bind(wx.EVT_SLIDER, self.on_sliderUpdate, self.sld)
			self.tx_sliderValue = wx.StaticText(self, wx.ID_ANY, '[%f,\n%f)' %(self.cut.slidingAxis[0][0],self.cut.slidingAxis[0][1]))
			sliderPanel.Add(self.tx_sliderValue,1, wx.ALIGN_CENTER)
			sliderPanel.AddStretchSpacer(prop=0.1)
			hboxsizerPanel.Add(sliderPanel, 0,wx.ALL| wx.EXPAND,5)
			
		self.SetSizer(hboxsizerPanel)
		self.SetSizeHints(1200,800,1200,800)

		# initialize the first plot
		if self.cut.cutType == 'slidingCut':
			self.plot(self.cut.intensityMap[0])
		else:
			self.plot(self.cut.intensityMap)

	def on_sliderUpdate(self, event):
		pos1 = self.sld.GetValue()
		Imin   = None if self.tx_lower.GetValue()   == '' else float(self.tx_lower.GetValue())
		Imax   = None if self.tx_upper.GetValue()   == '' else float(self.tx_upper.GetValue())
		self.tx_sliderValue.SetLabel('[%f,\n%f)' %(self.cut.slidingAxis[pos1][0],self.cut.slidingAxis[pos1][1]))
		self.plot(self.cut.intensityMap[pos1],Imin,Imax)
		
	def on_Plot(self, event):
		Imin   = None if self.tx_lower.GetValue()   == '' else float(self.tx_lower.GetValue())
		Imax   = None if self.tx_upper.GetValue()   == '' else float(self.tx_upper.GetValue())
		if self.cut.cutType == 'slidingCut':
			pos1 = self.sld.GetValue()
			self.plot(self.cut.intensityMap[pos1],Imin,Imax)
		else:
			self.plot(self.cut.intensityMap   ,Imin,Imax)
		
		
	
	def on_Close(self, event):
		self.Close()
		
		
	def plot(self,Data,Imin=None,Imax=None):
		
		if Imin is None:
			Imin = Data.min()
		if Imax is None:
			Imax = Data.max()
		
		if self.colorPlot is None and self.colorBar is None:
			self.colorPlot, self.colorBar = bdL.twoDplot(Data,self.cut.extent,Imin,Imax,self.matplotPanel,axis1Label=self.cut.axis1,axis2Label=self.cut.axis2)
			self.matplotPanel.canvas.draw()
		else:
			self.colorPlot.set_clim(vmin= Imin,vmax = Imax)
			self.colorPlot.set_data(Data)
			self.colorBar.update_bruteforce(self.colorPlot)
			self.matplotPanel.canvas.draw()


from matplotlib.figure import Figure
from pylab import rcParams
rcParams['figure.figsize'] = 9, 6
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as NavigationToolbar

class MatplotPanel(wx.Panel):

	def __init__(self, parent):     
		wx.Panel.__init__(self, parent,-1,size=(50,50))

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer,1)

		self.figure = Figure()
		
		self.axes = self.figure.gca()
		#self.axes = self.figure.add_subplot(111)
		self.canvas = FigureCanvas(self, -1, self.figure)
		self.toolbar = NavigationToolbar(self.canvas)
	
		self.sizer.Add(self.canvas, 1, wx.RIGHT | wx.TOP | wx.GROW)
		self.sizer.Add(self.toolbar, 0, wx.EXPAND)

		self.sizer.Fit(self)
		


            
app = wx.App(redirect=True)
mainFrame = MainFrame(None,title="BiodiffPlot",pos=(150,150), size=(355,520))
mainFrame.Show()
app.MainLoop()
