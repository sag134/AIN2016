import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import peakutils
from peakutils.plot import plot as pplot
def movingAverageMatrix(matrix,n):
    new_matrix = np.zeros((matrix.shape[0]-(n-1),matrix.shape[1]))
    for i in range(0,matrix.shape[1]):
        new_matrix[:,i] = movingAverage(matrix[:,i],n)
    return new_matrix

def movingAverage(a, n) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def foldChange(A,timePoints):
    #This function inputs a T x N matrix A, where each column is a trajectory. The values in timePoints are used to compute fold changes. 
    #Time points is a list of lists, i.e [[t1,t2,t3],[t4,t5,t6]] The trajectory portion between t1 and t4 is divided by the average of
    # t1,t2,t3; the trajectory portion between t4 and end is divided by the average of t4,t5,t6
    m = A.shape[1]   #No. of trajectories
    B = np.zeros(A.shape)
    nseg = len(timePoints)
    B[0:timePoints[0][0],:] = A[0:timePoints[0][0],:]
    for i in range(0,nseg):
        tpts = timePoints[i]
        if i<nseg-1:
            tpts_next = timePoints[i+1]
        else:
            tpts_next = np.array([A.shape[0]])
        base = A[tpts,:]
        mean = np.mean(base,0)       
        B[tpts[0]:tpts_next[0],:] = np.divide(A[tpts[0]:tpts_next[0],:],mean)
    return B

def getArea(data,points):
    area = []
    for pt in points:
        pt = (int(pt[0]),int(pt[1]))
        if len(pt) !=2:
            print 'error in getArea()'
            return
        else:
            y = data[pt[0]:pt[1]+1]
            n = len(range(pt[0],pt[1]+1))
            #print n
            x = data[pt[0]]*np.ones([1,n])[0]
            #print y
            #print x
            a = sum(y-x)
            area.append(a)
    return area

def findinflection(x,peak,mindistance,npts,thresh):
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
    m = np.zeros(n);
    counter = 0;
    inflect = np.zeros(len(peak))
    for j in peak:
        for i in range(j+mindistance,int(n-npts)):
            y = x[i:i+npts]
            a = np.polyfit(np.array(range(i-1,i+npts-1)), y, 1)
            m[i] = a[0]
            if m[i]>=thresh and m[i-1]<0 and i != j:
                break
        if j+mindistance >= (n-npts):
            i = n-1;
        inflect[counter] = int(i);
        counter = counter + 1;
    return inflect

def findpoints(data,default):
    points = {};    
    for i in range(0,data.shape[1]):
        y = data[:,i]
        base = peakutils.baseline(y, 2) #Polynomial fitting to estimate baseline        
        peak_indexes = peakutils.indexes(y-base, thres=default[2], min_dist=default[3])
        inflection_indexes = findinflection(y,peak_indexes,default[4],default[5],default[6])
        #Points are stored as (peak,inflection) pairs
        points[i] = [(peak_indexes[j],inflection_indexes[j]) for j in range(0,len(peak_indexes))]
    return points

def test_findpoints():
    default = [4,39,0.4,30,6,3,-0.0001,'final_data']
    pth = '/shared/LabUserFiles/Sanjana/CellProfilerResults/MATLAB/Repeats/FilteredLength/matlab_2016_2_23/Intensity_MedianIntensity_FITC_RelA/' + 'Condition_4_2016_2_23_Intensity_MedianIntensity_FITC_RelA.mat'
    testY = sio.loadmat(pth)
    data = testY['final_data'][:,3]
    data = data.reshape((data.shape[0],1))
    f = plt.figure()
    plt.plot(data) 
    plt.scatter(range(0,len(data)),data)
    pts = findpoints(data,default)
    for i in pts[0]:
        for j in i:
            plt.scatter(j,data[j],s=125)
    plt.show()
    
def test_getArea():
    data = [1,2,3,2,1,1,1,2,1]
    points = [(0,4),(6,8)]
    print '\n',getArea(data,points)
    data = [0,1,2,2,1,0, 0, 0, 2, 3, 4, 3, 2]
    points = {0:[1,4],1:[8,12]}
    points = [(1,4),(8,12)]
    print '\n',getArea(data,points)



def test_foldChange():
    A = np.array([[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18],[19,20,21],[22,23,24]])
    timePoints = [[1,2],[5,6]]
    B = foldChange(A,timePoints)
    print '\nA',A
    print '\ntimePoints',timePoints
    print '\nB',B

def test_movingAverage():
    a = [10,2,13,4,15,6,17,8,19]
    b = movingAverage(a,3)
    print 'a',a
    print 'b',b
    a  = range(0,10)
    b = movingAverage(a,4)
    print '\na',a
    print 'b',b

#test_foldChange()
#test_movingAverage()
test_getArea()
#test_findpoints()


