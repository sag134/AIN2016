import os
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
import copy
#Custom modules
import AuxiliaryFunctions as af


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.reloadResults = QPushButton('Reload',self)
        self.reloadResults.clicked.connect(self.reLoad)

        self.fname = ''
        self.openFile = QPushButton('Open', self)
        self.openFile.setShortcut('Ctrl+O')
        self.openFile.clicked.connect(self.fileBrowser)
        self.openFile2 = QPushButton('Open movie info', self)
        #self.openFile.setShortcut('Ctrl+O')
        self.openFile2.clicked.connect(self.fileBrowser2)
        self.setWindowTitle('Data Curator')
        # a figure instance to plot on
        self.figure = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        #Connecting canvas to clicks
        cid = self.figure.canvas.mpl_connect('button_press_event',self._on_press)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()     
        self.figure2 = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas2 = FigureCanvas(self.figure2)
        #Connecting canvas to clicks
        cid2 = self.figure2.canvas.mpl_connect('button_press_event',self._on_press)
        self.canvas2.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas2.setFocus()  
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        #Toggle display
        self.displayToggle = QtGui.QPushButton('Fold Change display toggle',self)
        self.displayToggle.clicked.connect(self.toggleSwitch)
        self.displayToggle.setShortcut('f')
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
        self.accept = QtGui.QCheckBox('Accept')
        self.accept.clicked.connect(self.acceptdata)
        self.accept.setShortcut('a')
        self.accept.setToolTip('Accept/Reject plot. Keyboard shortcut: <b>a</b>')
       
        self.trash = QtGui.QCheckBox('Trash')
        self.trash.clicked.connect(self.trashdata)
        self.trash.setShortcut('t')

        self.death = QtGui.QCheckBox('Death')
        self.death.clicked.connect(self.deathdata)
        self.death.setShortcut('x')       

        self.notes = QtGui.QPushButton('Notes',self)
        self.notes.clicked.connect(self.showNotes)

        #Edit Menu
        menu = QtGui.QMenu()
        delete_action = menu.addAction('Delete point',partial(self.editplot,1))
        addPeak_action = menu.addAction('Add peak point',partial(self.editplot,2))
        addInflection_action = menu.addAction('Add inflection point',partial(self.editplot,3))
        addSustain_action = menu.addAction('Add sustain point',partial(self.editplot,4))
        delete_action.setShortcut('d')
        addPeak_action.setShortcut('p')
        addInflection_action.setShortcut('i')
        addSustain_action.setShortcut('q')
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
        #self.setToolTip('Interactive display for manual data curation. <b>Email sag134@pitt.edu with any feedback</b>')
        #Calling the layout function
        self.Layout()
        self.default = [4,39,0.2,30,6,3,-0.0001,2,'final_data']
        self.show()

    def init(self):    
        self.f = False
        self.t = self.default[0:2]
        self.dlt = False
        self.addpeak = False
        self.addinflect = False
        self.addSustain = False
        self.timeOfDeath = False
        self.counter = 0; #Counter to keep track of which figure we are currently at.
        self.datainfo['key'] = self.default[8]      
        pth = self.datainfo['path']
        dapi_pth = pth.replace('FITC_RelA','DAPI_Nuclei')
        #If available, load DAPI data
        if os.path.exists(dapi_pth):
            dapi_data_info = {}
            dapi_data_info['key'] = self.datainfo['key']
            dapi_data_info['path'] = dapi_pth
            self.dapi_data = self.GetData(dapi_data_info)
        self.original_data = af.movingAverageMatrix(self.GetData(self.datainfo),3); #Original data
        self.data = copy.copy(self.original_data) #Copy of original data to work with
        self.npts = self.default[7];
        self.fdata = af.foldChange(self.original_data,[range(self.t[0]-self.npts,self.t[0]+1),range(self.t[1]-self.npts,self.t[1]+1)]); #Fold Change data
        self.accepteddata = [False for i in range(0,self.data.shape[1])];
        self.trashedData = [False for i in range(0,self.data.shape[1])]
        self.deadCellData = [False for i in range(0,self.data.shape[1])]
        self.notes = ['' for i in range(0,self.data.shape[1])];
        self.area = [[] for i in range(0,self.data.shape[1])]
        self.FCarea = [[] for i in range(0,self.data.shape[1])]
        self.ToD = [[] for i in range(0,self.data.shape[1])]
        self.points = self.findpoints(self.data);
        self.original_points = copy.copy(self.points)
        #Setting up sustain points as a list of lists
        #The list has n elements corresponding to n trajectories
        #Each list is a list of [peak,sustain] pairs
        self.sustain_points = [[] for x in range(0,self.data.shape[1])]

        self.selectionButtons = {self.accept:self.accepteddata,self.trash:self.trashedData,self.death:self.deadCellData}
        self.refreshplot()

    def reinit(self):     
        #self.points 
        tmp = self.findpoints(self.data);
        for i in range(0,len(self.points)):
            if self.points[i] == self.original_points[i]:
                self.points[i] = tmp[i]
        self.original_points = tmp
        self.t = self.default[0:2]
        self.npts = self.default[7]
        self.fdata = af.foldChange(self.original_data,[range(self.t[0]-self.npts,self.t[0]+1),range(self.t[1]-self.npts,self.t[1]+1)]);  #Fold Change data       
        self.refreshplot()

    def reLoad(self):
        path = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home'))
        results = sio.loadmat(path)
        self.accepteddata = results['accept'][0].astype(bool)
        self.points = {} 
        tmp = results['points'][0]
        counter = 0;
        for i in tmp:
            self.points[counter] = []
            for j in i:
                self.points[counter].append(tuple(j))
            counter = counter + 1; 
        counter = 0
        if 'default' in results.keys():
            typesList = [int,int,float,int,int,int,float,int,str]
            for j in range(0,len(self.default)):
                print results['default'][j]
                self.default[j] = typesList[j](results['default'][j]);
        self.t = self.default[0:2]
        self.npts = self.default[7]
        self.selectionButtons = {self.accept:self.accepteddata,self.trash:self.trashedData,self.death:self.deadCellData}
        self.refreshplot()

    def getMovieInfo(self,extrainfo):
        return sio.loadmat(extrainfo['path'])[extrainfo['key']]

    def fileBrowser(self):
        self.datainfo = {}
        self.datainfo['path'] = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home'))
        self.init()

    def fileBrowser2(self):
        extrainfo = {}
        extrainfo['path'] = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home'))
        extrainfo['key'] = 'aind'   
        movieinfo = self.getMovieInfo(extrainfo) 
        moviedict = []
        counter =  0;
        for i in range(0,movieinfo.shape[1]):
            counter = counter + 1;
            for j in range(0,movieinfo.shape[0]):
                if movieinfo[j][i]!=0:
                    moviedict.append([counter,movieinfo[j][i]])
                else:
                    break
        self.moviedict =  moviedict

    def toggleSwitch(self):
        if self.f == False:
            self.f = True
        else:
            self.f = False

        if self.f == False:
            self.data = self.original_data;
        else:
            self.data = self.fdata;
        self.refreshplot()

    def SaveStateVariables(self):
        filename = QFileDialog.getSaveFileName(self,'Save File','/home/',"*.mat")
        filename = str(filename)+'.mat'
        counter = 0
        counter1 =0
        for i in self.accepteddata:
            if i == True:
                data = self.original_data[:,counter]
                print self.points[counter]
                pts = [(self.default[0],self.points[counter][0][1]),(self.default[1],self.points[counter][1][1])]
                self.area[counter1] = af.getArea(data,pts)
                data = self.fdata[:,counter]
                self.FCarea[counter1] = af.getArea(data,pts)

                counter1 = counter1+1
            counter = counter + 1
        results = {};
        results['accept'] = numpy.asarray(self.accepteddata).astype(int);
        results['default'] =  [str(i) for i in self.default]# {i:self.default[i] for i in range(0,len(self.default)-1)}
        indices = [i for i in range(0,len(self.accepteddata)) if self.accepteddata[i]==1]
        tindices = [i for i in range(0,len(self.trashedData)) if self.trashedData[i]==1]
        dindices = [i for i in range(0,len(self.deadCellData)) if self.deadCellData[i] ==1]

        results['original_points'] = self.original_points.values()
        results['points'] = self.points.values();
        results['area'] = self.area;
        results['foldChangeArea'] = self.FCarea;
        results['trajectories'] = self.original_data[:,indices]
        results['fold_change_trajectories'] = self.fdata[:,indices]
        results['sustain_points'] = self.sustain_points
        results['trash_ID'] = numpy.asarray(self.trashedData).astype(int);
        results['TrashedTrajectories'] = self.original_data[:,tindices]
        results['IndexOfDeadCells'] = numpy.asarray(self.deadCellData).astype(int);
        results['DeadTrajectories'] = self.original_data[:,dindices]
        results['TimeOfDeath'] = self.ToD
        results['notes']=self.notes;
        sio.savemat(filename,results);
        
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
        l[7] = QtGui.QLabel("No. of pts in fold change calculation - 1")
        l[8] = QtGui.QLabel("Name of variable containing data")
        self.nm = {};
        fbox = QtGui.QFormLayout()
        for i in range(0,len(l)):
            self.nm[i] = QtGui.QLineEdit();
            self.nm[i].setText(str(self.default[i]))
            fbox.addRow(l[i],self.nm[i])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok,Qt.Horizontal,self)
        buttons.accepted.connect(self.ok)
        fbox.addWidget(buttons)
        self.msg.setLayout(fbox)
        res = self.msg.exec_()

    def ok(self):
        typesList = [int,int,float,int,int,int,float,int,str]
        for i in range(0,len(self.default)):
            self.default[i] = typesList[i](self.nm[i].text())
        self.t = self.default[0:2]
        self.npts = self.default[7]
        self.msg.close()
        self.reinit()

    def editplot(self,index):
        if index == 1: #Delete point
            self.dlt = True
        elif index ==2: #Add peak
            self.addpeak = True
        elif index==3: #Add inflection
            self.addinflect = True
        elif index==4:
            self.addSustain = True
        
    def acceptdata(self):
        if self.counter>=0:
            self.accepteddata[self.counter] = self.accept.isChecked();
            self.refreshplot()

    def trashdata(self):
        if self.counter>=0:
            self.trashedData[self.counter] = self.trash.isChecked();

    def deathdata(self):
        if self.counter>=0:
            self.timeOfDeath = True
            self.deadCellData[self.counter] = self.death.isChecked();

    def GetData(self,datainfo):
        data = sio.loadmat(datainfo['path'])
        tr =  data[datainfo['key']]
        for i in range(0,tr.shape[0]):
            for j in range(0,tr.shape[1]):
                tr[i][j] = tr[i][j] + 1e-16
        return tr

    def Layout(self):
        # set the layout        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1) #Shifting the buttons to the right.
        bttns = [self.openFile2,self.openFile,self.displayToggle,self.save,self.initialize,self.menu,self.accept,self.left,self.right]
        for bttn in bttns:
            hbox.addWidget(bttn)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(1)    
        bttns1 = [self.trash,self.death,self.notes,self.reloadResults]
        for bttn in bttns1:
            hbox1.addWidget(bttn)
        #Vertically stacking the toolbar, canvas, and buttons bar
        vbox = QtGui.QVBoxLayout()
        vel = [self.toolbar,self.canvas,self.canvas2]
        for velement in vel:
            vbox.addWidget(velement)
        vbox.addStretch(1)        
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox) #Shifting the buttons to the bottom
        self.setLayout(vbox)
        self.setGeometry(300,300,1000,1000) #Setting the window size.
        self.center() #Centering the window on the desktop

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def showNotes(self):
        self.msg1 = QtGui.QDialog()
        fbox = QtGui.QFormLayout()
        self.tmp = QtGui.QLineEdit();
        fbox.addRow('Enter Notes:',self.tmp)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok,Qt.Horizontal,self)
        buttons.accepted.connect(self.ok2)
        fbox.addWidget(buttons)
        self.msg1.setLayout(fbox)
        res = self.msg1.exec_()

    def ok2(self):
        self.notes[self.counter] = str(self.tmp.text())
        print self.notes
        self.msg1.close()

    def _on_press(self,event):         
        if self.dlt == True or self.addpeak == True or self.addinflect == True or self.addSustain == True or self.timeOfDeath == True:   
        #Step 1. Identify the clicked point. This is given by xdata      
            pts = self.points[self.counter]
            xpts = [item for sublist in pts for item in sublist] 
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

            if self.addSustain == True:
                #Identify the peak closest to the marked sustain point
                peaks = [tmp[0] for tmp in self.points[self.counter]]
                if len(peaks)>0:
                    dps = [abs(i-xdata) for i in peaks];
                    print peaks

                    ps = [peaks[j] for j in range(0,len(peaks)) if dps[j] == min(dps)]
                    self.sustain_points[self.counter].append((ps[0],xdata))
                    self.addSustain = False

            if self.addpeak == True:
                    newinflect = af.findinflection(self.data[:,self.counter],xdata,self.default[4],self.default[5],self.default[6])
                    self.points[self.counter].append((xdata,newinflect[0]))
                    self.addpeak = False

            if self.addinflect == True:
                    self.points[self.counter] = [(val[0],val[1]) if len(val)>1 else (val[0],xdata) for val in self.points[self.counter]]                    
                    self.addinflect = False 

            if self.timeOfDeath == True:
                self.ToD[self.counter] = [xdata]
                self.timeOfDeath = False

            if self.dlt == True:             
                infl = [tmp[1] for tmp in self.points[self.counter]]
                peaks = [tmp[0] for tmp in self.points[self.counter]]
                sustain = [tmp[1] for tmp in self.sustain_points[self.counter]]
                #Try and figure out whether we are deleting a peak or inflection
                if xdata in peaks:              
                #Remove the clicked point from self.points
                    newpts = [val for val in self.points[self.counter] if val[0] != xdata]
                    self.points[self.counter] = newpts
                    self.dlt = False
                elif xdata in infl:
                    print infl
                    newpts = [(val[0],val[1]) if val[1] != xdata else (val[0],) for val in self.points[self.counter]]
                    self.points[self.counter]= newpts
                    self.dlt = False
                    self.addinflect = True;
                elif xdata in sustain:
                    newpts = [val for val in self.sustain_points[self.counter] if val[1] != xdata]
                    self.sustain_points[self.counter] = newpts
                    self.dlt = False
                elif xdata in self.ToD[self.counter]:
                    self.ToD[self.counter] = []
                    self.dlt = False

            self.refreshplot()
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
        toD = self.ToD[self.counter]
        #Plot time of death
        if len(toD)>0:
            ax.scatter(toD,data[toD],s =125,c='r',marker ='v',linewidths=3,zorder=2)
        ax.scatter(peaks,data[peaks],s = 75,c='r',marker='x',linewidths = 3,zorder=2) #Plot peaks
        ax.scatter(infl,data[infl],s=75,c='k',marker='x',linewidths=3,zorder=2) #Plot inflections     
        if self.accepteddata[self.counter] == True:
            pts = self.points[self.counter]
            pts = sorted(pts,key = lambda x:x[0])
            t = self.t
            if len(t) >= len(pts):
                for i in range(0,len(pts)):
                    x1 = t[i];
                    y1 = data[x1];
                    x2 = pts[i][1];
                    y2 = data[x2];
                    x = range(int(x1),int(x2)+1)
                    y = [min(data[x2],data[x1]) for i in x]
                    ax.fill_between(x,y,data[x1:x2+1],alpha = 0.1)

        if len(self.sustain_points[self.counter])>0:
            for spts in self.sustain_points[self.counter]:
                x1 = spts[0]
                x2 = spts[1]
                y1 = data[x1]
                y2 = data[x2]
                ax.plot([x1,x2],[y1,y2],linewidth = 2,c='k')
                ax.scatter(x2,y2,s=75,c='g',marker = 'x',linewidths=3,zorder=2)
        flag_error = 0
        try:
            self.moviedict
        except AttributeError:
            flag_error = 1
        if flag_error == 1:
            prefix = ''
        else: 
            prefix = 'Movie number: '+str(self.moviedict[self.counter][0])+' Cell number: '+str(self.moviedict[self.counter][1])+' '      
        ax.set_title(prefix+'Trajectory number '+str(self.counter+1)+'/'+str(self.data.shape[1]))
        ax.set_xlim([0,self.data.shape[0]])
        self.canvas.draw()
        ax2 = self.figure2.add_subplot(111)
        ax2.hold(False)
        ax2.plot(self.dapi_data[:,self.counter],'-o')
        self.canvas2.draw()

    def PlotPrevious(self):
        #Update counter to the index of the previous figure. Unless it is pointing at the first figure. Then do nothing.
        if self.counter==0:
            return;
        else:
            self.counter = self.counter - 1;
        #Reset the radio button
        print self.accepteddata[self.counter]
        if self.counter<len(self.accepteddata):
            for button in self.selectionButtons.keys():
                print self.selectionButtons[button][self.counter]
                button.setChecked(self.selectionButtons[button][self.counter])
        self.refreshplot()

    def findpoints(self,data):
        points = {};    
        #print data.shape
        for i in range(0,data.shape[1]):
            y = data[:,i]
            base = peakutils.baseline(y, 2) #Polynomial fitting to estimate baseline        
            peak_indexes = peakutils.indexes(y-base, thres=self.default[2], min_dist=self.default[3])
            inflection_indexes = af.findinflection(y,peak_indexes,self.default[4],self.default[5],self.default[6])
            #Points are stored as (peak,inflection) pairs
            points[i] = [(peak_indexes[j],inflection_indexes[j]) for j in range(0,len(peak_indexes))]
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
            for button in self.selectionButtons.keys():
                button.setChecked(self.selectionButtons[button][self.counter])
        else:
            for button in self.selectionButtons.keys():
                button.setChecked(False)
        self.refreshplot()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Window()
    sys.exit(app.exec_())
