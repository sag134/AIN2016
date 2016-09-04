#While performing trajectory analysis, it is often desirable to test the ability of 
#an algorithm to pick up specific features in a specific type of trajectory.
#To this end, we present here a drawing tool, so as to be able to draw a test trajectory with certain properties,
#as opposed to searching for specific examples of it in experimental data.

import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio

class TestEnvironment():
	def __init__(self):
		self.x = []
		self.y = []	

	def DrawTraj(self,interpolate=True,n_sample=100,add_noise=0,noise_percent=0):
		#interpolate is a boolean option. if True, then the test points are connected
		#to get an interpolated trajectory, which is then sampled uniformly.
		#if sample is false, we only interpolate
		#Collect points
		self.figure = plt.figure()
		self.ax = self.figure.add_subplot(111)
		cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)
		cid2 = self.figure.canvas.mpl_connect('key_press_event', self.press)
		plt.show()

	def press(self,event):
		if event.key == 'x':
			mdict = {'x':self.pts,'y':self.y_new}
			sio.savemat('test_traj',mdict,appendmat = True)

	def onclick(self,event):
		axes = self.ax
		#Collect mouse click info
		self.x.append(event.xdata)
		self.y.append(event.ydata)
		#Get current axes
		ymin, ymax = axes.get_ylim()
		xmin, xmax = axes.get_xlim()
		self.ax.cla()
		#Plot mouse click
		self.ax.scatter(self.x,self.y,25)
		#Rest axes
		axes.set_xlim([xmin,xmax])
		axes.set_ylim([ymin,ymax])	

		a = min(self.x)
		b = max(self.x)
		self.pts = np.linspace(a,b,200)
		s_i = np.argsort(self.x)
		s_x = [self.x[i] for i in s_i]
		s_y = [self.y[i] for i in s_i]
		self.y_new = np.interp(self.pts,s_x,s_y)
		self.ax.plot(self.pts,self.y_new,'-+k',linewidth=2)
		self.figure.canvas.draw()
		plt.show()

if __name__ == "__main__":
	a = TestEnvironment()
	a.DrawTraj()
	b = a.__dict__
	#print b['x']

