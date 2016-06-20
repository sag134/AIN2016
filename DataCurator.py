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

class Window(QtGui.QWidget):
    def __init__(self,datainfo, parent=None):
        super(Window, self).__init__(parent)
        self.dlt = False
        self.addpeak = False
        self.addinflect = False
        self.counter = -1; #Counter to keep track of which figure we are currently at.
        self.accepteddata = [];
        self.data = self.GetData(datainfo);
        print self.data.shape
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
        #Window tool tip
        self.setToolTip('Interactive display for manual data curation. <b>Email sag134@pitt.edu with any feedback</b>')
       	#Calling the layout function
       	self.Layout()
       	self.show()

    def editplot(self,index):
    	if index == 1:
    		self.dlt = True
    	elif index ==2:
    		self.addpeak = True
    	elif index==3:
    		self.addinflect = True
		
    def acceptdata(self):
    	if self.counter>=0:
	    	if self.counter<len(self.accepteddata):
	    		#We are modifying a previous choice
	    		self.accepteddata[self.counter] = self.accept.isChecked()
	    	elif self.counter==len(self.accepteddata):
	    		self.accepteddata.append(self.accept.isChecked())
	    	else:
	    		tmp = [False for i in range(0,-len(self.accepteddata)+self.counter)]
	    		tmp.append(self.accept.isChecked())
	    		self.accepteddata = self.accepteddata + tmp;
    	print self.accepteddata

    def GetData(self,datainfo):
    	data = sio.loadmat(datainfo['path'])
    	tr =  data[datainfo['key']]
    	return tr

    def Layout(self):
        # set the layout        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1) #Shifting the buttons to the right.
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
    	#thisline = event.artist
    	#xdata = thisline.get_xdata()
    	#ydata = thisline.get_ydata()
    	#ind = event.ind
    	if self.dlt == True or self.addpeak == True or self.addinflect == True:	    	
	    	pts = self.points[self.counter]
	    	xpts = [item for sublist in pts for item in sublist] 
	    	if self.addpeak == True:
	    		data = range(1,self.data.shape[0]+1)
	    		xdata = [x for x in data if abs(x-event.xdata)<0.5]
	    		if len(xdata)>1:
	    			df = [abs(i-event.xdata) for i in xdata];
	    			coord = [i for i in range(0,len(xdata)) if df[i] == min(df)];
	    			xdata = coord[0];

	    		self.points[self.counter][0].append(list(xdata)[0])
	    		self.refreshplot()
	    		self.addpeak = False

	    	if self.addinflect == True:
	    		data = range(1,self.data.shape[0]+1)
	    		xdata = [x for x in data if abs(x-event.xdata)<0.5]
	    		if len(xdata)>1:
	    			df = [abs(i-event.xdata) for i in xdata];
	    			coord = [i for i in range(0,len(xdata)) if df[i] == min(df)];
	    			xdata = coord[0];

	    		self.points[self.counter][1].append(list(xdata)[0])
	    		self.refreshplot()
	    		self.addinflect = False	

	    	if self.dlt == True:
	    		data = range(1,self.data.shape[0]+1)
	    		xdata = [x for x in data if abs(x-event.xdata)<0.5]
	    		print xdata
	    		if len(xdata)>1:
	    			df = [abs(i-event.xdata) for i in xdata];
	    			coord = [i for i in range(0,len(xdata)) if df[i] == min(df)];
	    			xdata = coord[0];
	    		#Check if this point is in self.points
	    		print xdata
	    		pts = [val for sublist in self.points[self.counter] for val in sublist]
	    		if xdata in pts:	    		
	    		#Remove the clicked point from self.points
		    		newpts = [list(y for y in x if y != xdata) for x in self.points[self.counter]]
		    		print newpts
		    		self.points[self.counter] = newpts
		    		self.refreshplot()
		    		self.dlt = False


    #def displaymessage(self,message):
    #	w = QtGui.QWidget()
    #	msg = QtGui.QMessageBox(w,'Message',message)
    #	w.show()

    def refreshplot(self):
    	data = self.data[:,self.counter]
    	ax = self.figure.add_subplot(111)
    	ax.hold(False)
    	ax.plot(data,'-o',picker=0.5,zorder=1)
    	ax.hold(True)
    	pts = self.points[self.counter]
    	peaks = pts[0];
    	infl = pts[1];
    	ax.scatter(peaks,data[peaks],s = 75,c='r',marker='x',linewidths = 3,zorder=2)
    	ax.scatter(infl,data[infl],s=75,c='k',marker='x',linewidths=3,zorder=2)		
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
		data = self.data[:,self.counter]
		# create an axis
		ax = self.figure.add_subplot(111)
		# discards the old graph
		ax.hold(False)
		# plot data	
		ax.plot(data,'-o',picker=0.5,zorder=1)
		# refresh canvas
		ax.hold(True)
		pts = self.points[self.counter]
		peaks = pts[0];
		infl = pts[1];
		ax.scatter(peaks,data[peaks],s = 75,c='r',marker='x',linewidths = 3,zorder=2)
		ax.scatter(infl,data[infl],s=75,c='k',marker='x',linewidths=3,zorder=2)		
		self.canvas.draw()

    def findpoints(self,data):
		points = {};  	
		print data.shape
		for i in range(0,data.shape[1]):
			y = data[:,i]
			base = peakutils.baseline(y, 2) #Polynomial fitting to estimate baseline		
			peak_indexes = peakutils.indexes(y-base, thres=0.4, min_dist=30)
			truncated_y = y[10:]
			truncated_x = numpy.array(range(0,len(y)))[10:]
			truncated_base = base[10:]
			inflection_indexes = peakutils.indexes(-truncated_y-truncated_base, thres=0.4, min_dist=30)
			points[i]=[list(peak_indexes),list([10+x for x in inflection_indexes])]
		
		return points

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
		data = self.data[:,self.counter]
		# create an axis
		ax = self.figure.add_subplot(111)
		# discards the old graph
		ax.hold(False)
		# plot data
		ax.plot(data,'-o',picker=0.5,zorder=1)
		ax.hold(True)
		pts = self.points[self.counter]
		peaks = pts[0];
		infl = pts[1];
		ax.scatter(peaks,data[peaks],s = 75,c='r',marker='x',linewidths = 3,zorder=2)
		ax.scatter(infl,data[infl],s=75,c='k',marker='x',linewidths=3,zorder=2)
		#ax.scatter(results['truncated_x'][results['inflection_indexes']],results['truncated_y'][results['inflection_indexes']],s = 60,c='k',marker='x',linewidths = 3,zorder=2)
		# refresh canvas
		self.canvas.draw()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    datainfo = {};
    datainfo['path'] = './Tr.mat';
    datainfo['key'] = 'tr'
    main = Window(datainfo)
    print main.accepteddata;
    sys.exit(app.exec_())
