import numpy as np
import scipy.optimize as optimize
import warnings
warnings.simplefilter("ignore", optimize.OptimizeWarning)

# Get the velocity and delay values based on the current source...
# ...use for the simple locator
def getVelDelay(sourceTag):
    sources={'testing':{'Vp':5.0,'Vs':2.9,'Dp':0,'Ds':0,'tResThresh':0.5}}
    if sourceTag in sources.keys():
        return sources[sourceTag]
    else:
        return '$pass'

# Function to calculate the arrival times
# ti=function((xi,yi,zi,vi,di),x0,y0,t0)
# ti=t0+(Dist+Vel*Delay)/Vel
def simpleLocatorFunc(data,x0,y0,z0,t0):
    return t0+((((data[:,0]-x0)**2+(data[:,1]-y0)**2+(data[:,2]-z0)**2)**0.5)+data[:,3]*data[:,4])/data[:,3]

# Gather the information to be sent to the location minimization function
def getPickData(pickSet,staMeta,vdInfo):
    # Form array to be able to send to the 0 dimensional travel time function
    data,stas=[],[] #[xi,yi,zi,vi,ti],[]
    for aPick in pickSet:
        # Ensure that this pick has station metadata present
        idx=np.where(staMeta[:,0]==aPick[0])[0]
        if len(idx)<1:
            continue
        aStaX,aStaY,aStaZ=staMeta[idx[0],1:4].astype(float)
        # Assign appropriate velocity values        
        if aPick[1]=='P':
            aVel=vdInfo['Vp']
            aDelay=vdInfo['Dp']
        elif aPick[1]=='S':
            aVel=vdInfo['Vs']
            aDelay=vdInfo['Ds']
        else:
            continue
        aTime=float(aPick[2]) ## Give more sig digs?... rough approximation anyways
        data.append([aStaX,aStaY,aStaZ,aVel,aDelay,aTime])
        stas.append(aPick[0])
    return np.array(data),np.array(stas,dtype=str)

# Locate event using a straight ray path, and non-linear least squares curve fitting
# Also assign residual coloring to the stations
def simpleLocator(pickSet,staMeta,mapCurEve,staSort,sourceTag):
    vdInfo=getVelDelay(sourceTag)
    # If there was no vpInfo defined, pass these updates
    if vdInfo=='$pass':
        return '$pass','$pass','$pass'
    # Use only P and S picks
    if len(pickSet)>=4:
        pickSet=pickSet[np.where((pickSet[:,1]=='P')|(pickSet[:,1]=='S'))]
    # Set up the pen assignment arrays
    traceBgPenAssign={'noStaData':[sta for sta in staSort if sta not in staMeta[:,0]]}
    if len(staSort)==0:
        mapStaPenAssign={'noTraceData':[row[0] for row in staMeta]}
    else:
        mapStaPenAssign={'noTraceData':[row[0] for row in staMeta if row[0] not in staSort]}
    mapStaPenAssign['goodMap']=list(np.unique(pickSet[:,0]))
    data,stas=getPickData(pickSet,staMeta,vdInfo)    
    # If there are too few picks, do not try to locate
    if len(data)<4:
        return np.empty((0,5)),traceBgPenAssign,mapStaPenAssign
    # Compute value to take away from the very large travel times (easier on the curve fitting)
    Tref=np.min(pickSet[:,2].astype(float))
    data[:,5]-=Tref
    # Solve for event origin parameters
    try:
        params, pcov = optimize.curve_fit(simpleLocatorFunc, data[:,:5], data[:,5],(0,0,0,0))
        x0,y0,z0,t0=params
    except:
        print 'simpleLocator failed'
        return np.empty((0,5)),traceBgPenAssign,mapStaPenAssign
    # Get the residual values...
    # ...predicted arrival times
    ti=simpleLocatorFunc(data[:,:5],x0,y0,z0,t0)
    # Get the difference with the actual arrival times
    resids=np.abs(ti-data[:,5])
    poorResidStas=np.unique(stas[np.where(resids>=vdInfo['tResThresh'])])
    goodResidStas=np.unique(stas[np.where(resids<vdInfo['tResThresh'])])
    # Add the good/bad stations to proper pen assignments
    mapStaPenAssign['poorMap']=list(poorResidStas)
    mapStaPenAssign['goodMap']=list(goodResidStas)
    # Add back the time offset
    t0=Tref+t0
    return np.array([[0,x0,y0,z0,t0]]),traceBgPenAssign,mapStaPenAssign