import sys
from PyQt4 import QtGui,QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import scipy.io as sio
import numpy
import peakutils
from peakutils.plot import plot as pplot
from functools import partial
from PyQt4.QtGui import *
from PyQt4.QtCore import *




class Window(QtGui.QWidget):
    def __init__(self,datainfo, parent=None):
        super(Window, self).__init__(parent)
        self.default = [5,39,0.4,30,6,3,0]
        self.t = self.default[0:2]
        self.dlt = False
        self.addpeak = False
        self.addinflect = False
        self.counter = -1; #Counter to keep track of which figure we are currently at.
        self.data = self.GetData(datainfo);
        self.accepteddata = [False for i in range(0,self.data.shape[1])];
        self.area = [[] for i in range(0,self.data.shape[1])]
        #print self.data.shape
        self.setWindowTitle('Data Curator')
        self.points = self.findpoints(self.data);
        # a figure instance to plot on
        self.figure = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        #Connecting canvas to clicks
       	cid = self.figure.canvas.mpl_connect('button_press_event',self._on_press)
       	self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
       	self.canvas.setFocus()        
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        # Left and right buttons to scroll through images
        self.left = QtGui.QPushButton('previous',self)
        self.left.clicked.connect(self.PlotPrevious)
        self.left.setToolTip('Click here to go to the <b>previous</b> plot. Keyboard shortcut: <b>left arrow key</b>')
        self.left.setShortcut('Left')
        self.right = QtGui.QPushButton('next',self)
        self.right.clicked.connect(self.PlotNext)
        self.right.setToolTip('Click here to go to the <b>next</b> plot. Keyboard shortcut: <b>right arrow key</b>')
        self.right.setShortcut('Right')
        #Accept radio button.
        self.accept = QtGui.QRadioButton('Accept')
        self.accept.clicked.connect(self.acceptdata)
        self.accept.setShortcut('a')
        self.accept.setToolTip('Accept/Reject plot. Keyboard shortcut: <b>a</b>')
        #Edit Menu
        menu = QtGui.QMenu()
        menu.addAction('Delete point',partial(self.editplot,1))
     	menu.addAction('Add peak point',partial(self.editplot,2))
        menu.addAction('Add inflection point',partial(self.editplot,3))
        self.menu = QtGui.QPushButton('Edit',self)
        self.menu.setMenu(menu)
        self.menu.setShortcut('e')
        self.menu.setToolTip('Options to edit figure. Keyboard shortcut: <b>e</b>')        
        #Save button
        self.save = QtGui.QPushButton('Save',self)
        self.save.setShortcut('s')
        self.save.setToolTip('Remember to save your work. Keyboard shortcut: <b>s</b>')
        self.save.clicked.connect(self.SaveStateVariables)
        #Initial parameters
        self.initialize = QtGui.QPushButton('Initialize',self)
        #self.initialize.setShortcut('i')
        #self.initialize.setToolTip('set initial parameters.')
        self.initialize.clicked.connect(self.showdialog)
        #self.initialize.clicked.connect(self.setInit)
        #Window tool tip
        self.setToolTip('Interactive display for manual data curation. <b>Email sag134@pitt.edu with any feedback</b>')
       	#Calling the layout function
       	self.Layout()
       	self.show()

    def SaveStateVariables(self):
    	results = {};
    	results['accept'] = self.accepteddata;
    	results['points'] = self.points.values();
    	results['area'] = self.area;
    	sio.savemat('results.mat',results);
    	
    def showdialog(self):
		self.msg = QtGui.QDialog()
		#msg.setIcon(QtGui.QMessageBox.Information)
		#msg.setText("Initialize parameters here")
		l = {};
		l[0] = QtGui.QLabel("time point 1")
		l[1] = QtGui.QLabel("time point 2")
		l[2] = QtGui.QLabel("peak height threshold")
		l[3] = QtGui.QLabel("Min distance between peaks")
		l[4] = QtGui.QLabel("Min distance between a peak and its inflection")
		l[5] = QtGui.QLabel("No. of pts used to fit line (inflection calculation)")
		l[6] = QtGui.QLabel("Angle threshold (inflection calculation)")		
		self.nm = {};
		fbox = QtGui.QFormLayout()
		for i in range(0,7):
			self.nm[i] = QtGui.QLineEdit();
			self.nm[i].setText(str(self.default[i]))
			fbox.addRow(l[i],self.nm[i])

		buttons = QDialogButtonBox(QDialogButtonBox.Ok,Qt.Horizontal,self)
		buttons.accepted.connect(self.ok)
		fbox.addWidget(buttons)
		self.msg.setLayout(fbox)
		res = self.msg.exec_()

    def ok(self):
    	for i in range(0,len(self.default)):
    		self.default[i] = float(self.nm[i].text())
		self.t = self.default[0:2]
    	self.msg.close()

    def editplot(self,index):
    	if index == 1: #Delete point
    		self.dlt = True
    	elif index ==2: #Add peak
    		self.addpeak = True
    	elif index==3: #Add inflection
    		self.addinflect = True
		
    def acceptdata(self):
    	if self.counter>=0:
    		self.accepteddata[self.counter] = self.accept.isChecked();
    		self.refreshplot()

    def GetData(self,datainfo):
    	data = sio.loadmat(datainfo['path'])
    	tr =  data[datainfo['key']]
    	return tr

    def Layout(self):
        # set the layout        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1) #Shifting the buttons to the right.
        hbox.addWidget(self.save)
        hbox.addWidget(self.initialize)
        hbox.addWidget(self.menu)
        hbox.addWidget(self.accept)
        hbox.addWidget(self.left)
        hbox.addWidget(self.right)
        vbox = QtGui.QVBoxLayout()
        #Vertically stacking the toolbar, canvas, and buttons bar
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        vbox.addStretch(1)
        vbox.addLayout(hbox) #Shifting the buttons to the bottom
        self.setLayout(vbox)
        self.setGeometry(300,300,500,500) #Setting the window size.
        self.center() #Centering the window on the desktop

    def _on_press(self,event):
    	if self.dlt == True or self.addpeak == True or self.addinflect == True:	    	
	    	pts = self.points[self.counter]
	    	xpts = [item for sublist in pts for item in sublist] 
	    	if self.addpeak == True:
	    		data = range(0,self.data.shape[0])
	    		xdata = [x for x in data if abs(x-event.xdata)<0.5]
	    		if len(xdata)>0:
		    		if len(xdata)>1:
		    			df = [abs(i-event.xdata) for i in xdata];
		    			coord = [i for i in range(0,len(xdata)) if df[i] == min(df)];
		    			print "coord",coord
		    			xdata = xdata[coord[0]];
		    		else:
		    			xdata = xdata[0]
	    			newinflect = self.findinflection(self.data[:,self.counter],xdata,self.default[4],self.default[5],self.default[6])
	    			self.points[self.counter].append((xdata,newinflect[0]))
		    		self.refreshplot()
		    		self.addpeak = False

	    	if self.addinflect == True:
	    		data = range(1,self.data.shape[0]+1)
	    		xdata = [x for x in data if abs(x-event.xdata)<0.5]
	    		if len(xdata)>0:
		    		if len(xdata)>1:
		    			df = [abs(i-event.xdata) for i in xdata];
		    			coord = [i for i in range(0,len(xdata)) if df[i] == min(df)];
		    			xdata = xdata[coord[0]];
		    		else:
		    			xdata = xdata[0]
		    		self.points[self.counter] = [(val[0],val[1]) if len(val)>1 else (val[0],xdata) for val in self.points[self.counter]]
		    		self.refreshplot()
		    		self.addinflect = False	

	    	if self.dlt == True:
	    		data = range(1,self.data.shape[0]+1)
	    		xdata = [x for x in data if abs(x-event.xdata)<0.5]
	    		if len(xdata)>1:
	    			df = [abs(i-event.xdata) for i in xdata];
	    			coord = [i for i in range(0,len(xdata)) if df[i] == min(df)];
	    			xdata = xdata[coord[0]];
	    		else:
	    			xdata = xdata[0];	    		
	    		infl = [tmp[1] for tmp in self.points[self.counter]]
	    		peaks = [tmp[0] for tmp in self.points[self.counter]]
	    		#Try and figure out whether we are deleting a peak or inflection
	    		if xdata in peaks:	    		
	    		#Remove the clicked point from self.points
		    		newpts = [val for val in self.points[self.counter] if val[0] != xdata]
		    		self.points[self.counter] = newpts
		    		self.refreshplot()
		    		self.dlt = False
		    	elif xdata in infl:
		    		newpts = [(val[0],val[1]) if val[1] != xdata else (val[0],) for val in self.points[self.counter]]
		    		self.points[self.counter]= newpts
		    		self.refreshplot()
		    		self.dlt = False
		    		self.addinflect = True;
		print self.points[self.counter]

    def refreshplot(self):
    	data = self.data[:,self.counter]
    	ax = self.figure.add_subplot(111)
    	ax.hold(False)
    	ax.plot(data,'-o',picker=0.5,zorder=1)
    	ax.hold(True)
    	pts = self.points[self.counter]
    	peaks = [tmp[0] for tmp in pts];
    	infl = [tmp[1] for tmp in pts if len(tmp)>1];
    	ax.scatter(peaks,data[peaks],s = 75,c='r',marker='x',linewidths = 3,zorder=2)
    	ax.scatter(infl,data[infl],s=75,c='k',marker='x',linewidths=3,zorder=2)		
    	if self.accepteddata[self.counter] == True:
	    	pts = self.points[self.counter]
	    	t = self.t
	    	tmp = [];
	    	if len(t) == len(pts):
	    		for i in range(0,len(t)):
	    			x1 = t[i];
	    			y1 = data[x1];
	    			x2 = pts[i][1];
	    			y2 = data[x2];
	    			x = range(int(x1),int(x2)+1)
	    			y = [min(data[x2],data[x1]) for i in x]
	    			ax.fill_between(x,y,data[x1:x2+1],alpha = 0.1)
	    			tmp.append((sum(data[x1:x2+2])-sum(y)))
			self.area[self.counter] = tmp
			print self.area[self.counter]
    	self.canvas.draw()

    def center(self):
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

    def PlotPrevious(self):
		#Update counter to the index of the previous figure. Unless it is pointing at the first figure. Then do nothing.
		if self.counter==0:
			return;
		else:
			self.counter = self.counter - 1;
		#Reset the radio button
		if self.counter<len(self.accepteddata):
			self.accept.setChecked(self.accepteddata[self.counter])
		self.refreshplot()

    def findpoints(self,data):
		points = {};  	
		print data.shape
		for i in range(0,data.shape[1]):
			y = data[:,i]
			base = peakutils.baseline(y, 2) #Polynomial fitting to estimate baseline		
			peak_indexes = peakutils.indexes(y-base, thres=self.default[2], min_dist=self.default[3])
			inflection_indexes = self.findinflection(y,peak_indexes,self.default[4],self.default[5],self.default[6])
			#Points are stored as (peak,inflection) pairs
			points[i] = [(peak_indexes[j],inflection_indexes[j]) for j in range(0,len(peak_indexes))]
		return points

    def findinflection(self,x,peak,mindistance,npts,thresh):
		#Find one inflection per peak
		try:
			for i in peak:
				dummy = 1;
		except TypeError:
			try:
				dummy = peak+1;
				peak = [];
				peak.append(dummy-1)
			except:
				print('TypeError in findinflection')
				return
		n = x.shape[0]
		m = numpy.zeros(n);
		counter = 0;
		inflect = numpy.zeros(len(peak))
		for j in peak:
			for i in range(j+mindistance,int(n-npts)):
				y = x[i:i+npts]
				a = numpy.polyfit(numpy.array(range(i-1,i+npts-1)), y, 1)
				m[i] = a[0]
				if m[i]>=thresh and m[i-1]<0 and i != j:
					#print i
					break
			inflect[counter] = int(i);
			counter = counter + 1;
		return inflect

    def PlotNext(self):
		#Update counter to the index of the previous figure. Unless it is pointing at the first figure. Then do nothing.
		if self.counter==self.data.shape[1]-1:
			return;
		else:
			self.counter = self.counter + 1;
		print self.counter
		#Reset the radio button
		if self.counter<len(self.accepteddata):
			self.accept.setChecked(self.accepteddata[self.counter])		
		else:
			self.accept.setChecked(False)
		self.refreshplot()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    datainfo = {};
    datainfo['path'] = './Tr.mat';
    datainfo['key'] = 'tr'
    main = Window(datainfo)
    sys.exit(app.exec_())