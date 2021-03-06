from PyQt5 import QtWidgets
import numpy as np
import scipy.optimize as optimize
from scipy import signal
from scipy.spatial.distance import cdist
import warnings
warnings.simplefilter("ignore", optimize.OptimizeWarning)

# Get the velocity and delay values based on the current source...
# ...used for the simple locator (see simpleLocatorFunc for the equation, units in km and s)
# ...Vp=P-velocity,Vs=S-velocity,Dp=P-delay,Ds=S-delay
# ...tResThresh is the time residual which is residual value beyond which is considered poor
def getVelDelay(sourceTag):
    sources={'testing':{'Vp':5.0,'Vs':2.9,'Dp':0,'Ds':0,'tResThresh':0.5},
             'NX':{'Vp':6.19,'Vs':3.57,'Dp':0.74,'Ds':1.13,'tResThresh':1.0},
            }
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
def getPickData(pickSet,staLoc,vdInfo):
    # Form array to be able to send to the 0 dimensional travel time function
    data,stas=[],[] #[xi,yi,zi,vi,ti],[]
    for aPick in pickSet:
        # Ensure that this pick has station metadata present
        idx=np.where(staLoc[:,0]==aPick[0])[0]
        if len(idx)<1:
            continue
        aStaX,aStaY,aStaZ=staLoc[idx[0],1:4].astype(float)
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
def simpleLocator(pickSet,staLoc,mapCurEve,staSort,sourceTag):
    vdInfo=getVelDelay(sourceTag)
    # If there was no vpInfo defined, pass these updates
    if vdInfo=='$pass':
        return '$pass','$pass','$pass'
    # Use only P and S picks
    if len(pickSet)>=4:
        pickSet=pickSet[np.where((pickSet[:,1]=='P')|(pickSet[:,1]=='S'))]
    # Set up the pen assignment arrays
    traceBgPenAssign={'noStaData':[sta for sta in staSort if sta not in staLoc[:,0]]}
    if len(staSort)==0:
        mapStaPenAssign={'noTraceData':[row[0] for row in staLoc]}
    else:
        mapStaPenAssign={'noTraceData':[row[0] for row in staLoc if row[0] not in staSort]}
    mapStaPenAssign['goodMap']=list(np.unique(pickSet[:,0]))
    data,stas=getPickData(pickSet,staLoc,vdInfo)    
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
        print('simpleLocator failed')
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
    
# Function to calculate PS delay with a given hypocentral distance (all units in km, and seconds)
def calcPSarrivalTimes(vdInfo,hypDist):
    tp=(hypDist+vdInfo['Vp']*vdInfo['Dp'])/vdInfo['Vp']
    ts=(hypDist+vdInfo['Vs']*vdInfo['Ds'])/vdInfo['Vs']
    return tp,ts  
    
# Calculate the hypocentral distance given a PS delay
def calcHypDist_viaDelayPS(vdInfo,delayPS):
    hyp=vdInfo['Vp']*vdInfo['Vs']*(delayPS+vdInfo['Dp']-vdInfo['Ds'])/(vdInfo['Vp']-vdInfo['Vs'])
    hyp=np.clip(hyp,0,np.max(hyp))
    return hyp 

# For each pick give it a pIdx, dIdx, and probability (many trios are formed for each pick)
def getOriginInfo(vdInfo,pickSet,staLoc,probSpread,tDelta,maxSampShift):
    maxSampShift+=1 # makes it easier for array generation, starts from zero
    # Make a dictionary of the station locations
    staLocDict={}
    for entry in staLoc:
        staLocDict[entry[0]]=entry[1:].astype(float)
    # Sort by pick type (so the P-picks are processed first)
    pickSet=pickSet[np.argsort(pickSet[:,1])]
    # Form arrays to be used for all picks...
    # ...for station locations
    locs=np.ones((maxSampShift,len(pickSet),3)).astype(float)
    # ...ps delay indicies
    dIdxs=np.arange(0,maxSampShift).reshape(maxSampShift,1)
    # ...hypocentral distances
    hypDists=calcHypDist_viaDelayPS(vdInfo,dIdxs*tDelta).reshape(maxSampShift,1)
    tp=calcPSarrivalTimes(vdInfo,hypDists)[0].T[0]
    # Increase the shape to account for the number of picks
    hypDists=hypDists*np.ones((maxSampShift,len(pickSet)))
    dIdxs=dIdxs*np.ones((maxSampShift,len(pickSet)),dtype=int)
    pIdxs=np.ones((maxSampShift,len(pickSet)),dtype=int)
    probs=np.ones((maxSampShift,len(pickSet)),dtype=float)
    origTimes=np.ones((maxSampShift,len(pickSet)),dtype=float)
    stas=np.ones((maxSampShift,len(pickSet)),dtype='a5')
    # Digitize the pick times
    pickTimes=pickSet[:,2].astype(float)
    minT,maxT=np.min(pickTimes),np.max(pickTimes)
    tBins=np.arange(minT-(0.5+len(probSpread)/2+maxSampShift)*tDelta,
                    maxT+(0.5+len(probSpread)/2)*tDelta,tDelta)
    pickIdxs=np.digitize(pickTimes,tBins)
    for j,sta,phase,xIdx in zip(range(len(pickSet)),pickSet[:,0],pickSet[:,1],pickIdxs):
        # Get the station location for later reference
        aLoc=staLocDict[sta]
        if phase=='P':
            pIdx=np.ones(maxSampShift,dtype=int)*xIdx
        else:
            pIdx=np.arange(xIdx,xIdx-maxSampShift,-1,dtype=int)
        # Calculate the origin times
        origTime=tBins[pIdx]-0.5*tDelta-tp
        # Assign these values to proper location
        locs[:,j,:]=aLoc
        pIdxs[:,j]=pIdx
        origTimes[:,j]=origTime
        stas[:,j]=sta
    # Create the origin info, for the high probability
    originInfo={}#'t':outInfo[:,0],'sta':np.array(stas,dtype=str),'dist':outInfo[:,1],'probE':outInfo[:,2],
                #'pIdx':outInfo[:,3].astype(int),'dIdx':outInfo[:,4].astype(int),'loc':outInfo[:,5:8]}
    # Assign probabilities for each of these values based on the probSpread
    for tIdxShift,tProb in zip(np.arange(len(probSpread))-len(probSpread)/2,probSpread):
        for key,entry in [['t',origTimes],['sta',stas],['dist',hypDists],
                          ['prob',probs],['pIdx',pIdxs],['dIdx',dIdxs],['loc',locs]]:
            # Reshape so one long list of trios
            if key=='loc':
                shape=entry.shape
                entry=entry.reshape(shape[0]*shape[1],shape[2])
            else:
                entry=entry.flatten()
            # If the values is dependent on the probSpread, change it
            if key=='prob':
                entry[:]*=tProb
            elif key=='t':
                entry[:]+=tIdxShift*tDelta
            elif key=='pIdx':
                entry[:]+=tIdxShift
            # Add the entry if not already there...
            if key not in originInfo.keys():
                originInfo[key]=entry
            # ...otherwise concatenate
            else:
                originInfo[key]=np.concatenate((originInfo[key],entry))
    return originInfo
    
# Make a subset of rings which can be used later to stack the probabilities (and another base for the ROI)
def getStackRings(roi,vdInfo,maxHypDist,maxVertDist,maxDelayPS,timeDelta):
    # Figure out which boundaries should be applied
    ringBounds=[]
    for aDelay in np.arange(0,maxDelayPS+timeDelta,timeDelta):
        aHyp=calcHypDist_viaDelayPS(vdInfo,aDelay)
        if aHyp<0:
            aHyp=0
        if aHyp in ringBounds:
            continue
        ringBounds.append(aHyp)
    halfRingWidth=(ringBounds[-1]-ringBounds[-2])/2.0
    ringBounds.append(halfRingWidth*2+ringBounds[-1])
    ringBounds=np.array(ringBounds,dtype=float)-halfRingWidth
    # Create the base map
    gridSpace=halfRingWidth/2.0 # Choose this ratio for wanted ring resolution
    baseX,baseY,baseZ=np.meshgrid(np.arange(roi[0],roi[1],gridSpace),
                                  np.arange(roi[2],roi[3],gridSpace),
                                  np.arange(roi[4],roi[5],gridSpace))
    baseProb=np.zeros(baseX.shape)
    # Create the station rings, centered on zero
    usedMaxDist=maxHypDist-maxHypDist%gridSpace+gridSpace
    usedMaxVert=maxVertDist-maxVertDist%gridSpace+gridSpace
    layX,layY,layZ=np.meshgrid(np.arange(-usedMaxDist,usedMaxDist+0.1*gridSpace,gridSpace),
                               np.arange(-usedMaxDist,usedMaxDist+0.1*gridSpace,gridSpace),
                               np.arange(-usedMaxVert,usedMaxVert+0.1*gridSpace,gridSpace))
    layD=(layX**2+layY**2+layZ**2)**0.5
    rings=[]
    for i in range(len(ringBounds)-1):
        rings.append(np.array((layD>=ringBounds[i])&(layD<ringBounds[i+1]),dtype=np.uint8))
    return rings,ringBounds,baseX,baseY,baseZ,baseProb,halfRingWidth

# Assign specific layer indicies to the originInfo, as well as how they would fit into the baseLayer    
def assignLayerInfo(originInfo,ringLay,ringBounds,baseX,baseY,baseZ,baseProb):
    # Assign which layer
    layIdx=np.digitize(originInfo['dist'],ringBounds)-1
    originInfo['layIdx']=layIdx
    # Figure out all the shift/trim for each station
    shapeBase=baseX.shape
    shapeLay=ringLay[0].shape
    centerLayIdx=np.array(shapeLay)/2
    unqStas,staIdxs=np.unique(originInfo['sta'],return_index=True)
    staPosDict={}
    for aSta,aStaIdx in zip(unqStas,staIdxs):
        # Calculate where the station is centered on the base layer
        sX,sY,sZ=originInfo['loc'][aStaIdx]
        argPos=np.argmin((baseX.flatten()-sX)**2+(baseY.flatten()-sY)**2+(baseZ.flatten()-sZ)**2)
        xArg,yArg,zArg=np.unravel_index(argPos,shapeBase)
        # Figure out what bounds to use to trim
        # These naming conventions based on plan view of the rings
        topArg=np.min([(shapeBase[0])-xArg,centerLayIdx[0]])
        botArg=np.min([xArg,centerLayIdx[0]])
        rightArg=np.min([(shapeBase[1])-yArg,centerLayIdx[1]])
        leftArg=np.min([yArg,centerLayIdx[1]])
        outArg=np.min([(shapeBase[2])-zArg,centerLayIdx[2]])
        inArg=np.min([zArg,centerLayIdx[2]])
        # Contains the position within the base array, and how far up/down/left/right/out/in should be used
        staPosDict[aSta]=np.array([xArg,yArg,zArg,botArg,topArg,leftArg,rightArg,inArg,outArg],dtype=int)
    # Assign these to each origin entry
    gridShifts=[]
    for aSta in originInfo['sta']:
        gridShifts.append(staPosDict[aSta])
    originInfo['gridShift']=gridShifts
    return originInfo

def stackDetectAlgorithm(originInfo,rings,baseX,baseY,baseZ,base,timeDelta,
                         featAvgIdxLen,maxTT,eveProbMinSum,vdInfo,maxEveCount=999999):
    outTimes,outLocs,outProbs,outArgs=[],[],[],[]
    # Get the center index of the ring arrays
    lcx,lcy,lcz=np.array(rings[0].shape)/2 # Array length is odd, so this will yield the center index
    # Make a list of all timestamps, with the feature interval (timeDelta) as a spacing
    queryTimes=np.arange(np.min(originInfo['t'])-0.5*timeDelta,
                         np.max(originInfo['t'])+timeDelta,timeDelta)
    # Make list of stations which are used in this time range, and a reference index for each station
    segmentStas=np.unique(originInfo['sta'])
    refInfo={}
    for aSta in segmentStas:
        refIdx=list(originInfo['sta']).index(aSta)
        tp,ts=calcPSarrivalTimes(vdInfo,originInfo['dist'][refIdx])
        refpIdx=originInfo['pIdx'][refIdx]-int(np.round(tp/timeDelta))
        refOrig=originInfo['t'][refIdx]-int(np.round(tp/timeDelta))
        refInfo[aSta]=[refIdx,refOrig,refpIdx]
    # Now scan through all of these times, removing the duplicates...
    # ... each pass the maximums over a sweeping window of length "maxTT" is extracted, and any indices on the two diagonals...
    # ... and two verticals are removed from the other potential events - and then their probability is updated
    search=True
    seenArgs=np.zeros(len(originInfo['t']))
    # Only scan through queryTimes which actually have trios
    origArgs=np.digitize(originInfo['t'],queryTimes)
    unqOrigArgs=np.unique(origArgs)-1
    while search:
        # For each segment of times, find the location of the maximum probability (and get its index)
        eveProbs,eveLocs,eveTimes,usedOrigArgs=[],[],[],[]
        for i in unqOrigArgs:
            t1,t2=queryTimes[i],queryTimes[i+1]
            aEveTime=(t1+t2)/2.0
            wantArgs=np.where((originInfo['t']>t1)&(originInfo['t']<=t2)&(seenArgs==0))[0]
            stack=np.copy(base)
            for anArg in wantArgs:
                # p has entries: cx,cy,cz,bot,top,left,right,in,out
                p,layIdx,prob=originInfo['gridShift'][anArg],originInfo['layIdx'][anArg],originInfo['prob'][anArg]
                stack[p[0]-p[3]:p[0]+p[4],p[1]-p[5]:p[1]+p[6],p[2]-p[7]:p[2]+p[8]]+=(
                    prob*rings[layIdx][lcx-p[3]:lcx+p[4],lcy-p[5]:lcy+p[6],lcz-p[7]:lcz+p[8]])
            argMaxX,argMaxY,argMaxZ=np.unravel_index(np.argmax(stack.flatten()),stack.shape)
            aEveProb=stack[argMaxX,argMaxY,argMaxZ]
            # If there were no events during this time, skip
            if aEveProb<eveProbMinSum:
                continue
            # If there was more than one entry at this value, then get the median position
            if len(np.where(stack==aEveProb)[0])>1:
                argXs,argYs,argZs=np.unravel_index(np.where(stack.flatten()==aEveProb)[0],stack.shape)
                # Since grid spacing is equal in all directions, can take median of index
                argMaxX,argMaxY,argMaxZ=int(np.round(np.median(argXs))),int(np.round(np.median(argYs))),int(np.round(np.median(argZs)))
            aEveX,aEveY,aEveZ=baseX[argMaxX,argMaxY,argMaxZ],baseY[argMaxX,argMaxY,argMaxZ],baseZ[argMaxX,argMaxY,argMaxZ]
            # Given this maximum location, figure out which originInfo rows were used
            aUsedOrigArg=[]
            for anArg in wantArgs:
                p,layIdx=originInfo['gridShift'][anArg],originInfo['layIdx'][anArg]
                # If the ring layers do not cover the entire stack area... 
                # ...check first to see if current ring could stack at the potential event location
                cutRing=rings[layIdx][lcx-p[3]:lcx+p[4],lcy-p[5]:lcy+p[6],lcz-p[7]:lcz+p[8]]
                if np.sum(np.array([argMaxX,argMaxY,argMaxZ])>=cutRing.shape)>0:
                    continue
                # ... then check if used at potential event location.
                if cutRing[argMaxX-(p[0]-p[3]),argMaxY-(p[1]-p[5]),argMaxZ-(p[2]-p[7])]==1:
                    aUsedOrigArg.append(anArg)
            usedOrigArgs.append(np.array(aUsedOrigArg,dtype=int))
            eveProbs.append(aEveProb)
            eveLocs.append([aEveX,aEveY,aEveZ])
            eveTimes.append(aEveTime)
        # If there are no more peaks to review, break
        if len(eveProbs)==0:
            search=False
            break
        eveProbs,eveLocs,eveTimes=np.array(eveProbs),np.array(eveLocs),np.array(eveTimes)
        # Collect all maximums, with the +/- maxTT bounding them
        collectPeaks=True
        peakIdxs=[]
        copyEveProbs=np.copy(eveProbs) # Used as a padding array for this "search" iteration
        while collectPeaks:
            maxArg=np.argmax(copyEveProbs)
            # If the peak was seen, swap it and any nearby peaks to be zero
            nearbyArgs=np.where(np.abs(eveTimes-eveTimes[maxArg])<maxTT)
            copyEveProbs[nearbyArgs]=0
            if np.max(copyEveProbs)<eveProbMinSum:
                collectPeaks=False
            # This peak however still requires to be a local maximum (in the unaltered array)...
            # ... as to not ruin the chance of a larger peak close to an even larger peak (which... 
            # ... was already added to peakIdxs during this "search" iteration)
            if eveProbs[maxArg]<np.max(eveProbs[nearbyArgs]):
                continue
            peakIdxs.append(maxArg)
        peakIdxs=np.array(peakIdxs)
        # For each peak, look at the surrounding origin entries to see if they should be ignored later
        for aPeakArg in peakIdxs:
            # Collect nearby (in time) origin information (no need to scan all origin entries)
            aEveTime=eveTimes[aPeakArg]
            aEveLoc=eveLocs[aPeakArg]
            oArgs=np.where(np.abs(aEveTime-originInfo['t'])<maxTT)[0]
            # Collect the diagonal and vertical value from the peak for each station...
            peakDiags=[originInfo['pIdx'][anArg]+originInfo['dIdx'][anArg] for anArg in usedOrigArgs[aPeakArg]]
            peakVerts=[originInfo['pIdx'][anArg] for anArg in usedOrigArgs[aPeakArg]]
            peakStas=[originInfo['sta'][anArg] for anArg in usedOrigArgs[aPeakArg]]
            # ... including the theoretical peakDiags, and peakVerts if the station was not helpful in the stack
            for aSta in [sta for sta in segmentStas if sta not in peakStas]:
                # Find out what the pIdx would have been
                refIdx,refOrig,refpIdx=refInfo[aSta] # Get the reference origin time and pIdx (dIdx=0)
                staXYZ=originInfo['loc'][refIdx]     # Calculate the P and S travel times
                aDist=np.sum((aEveLoc-staXYZ)**2)**0.5
                tp,ts=calcPSarrivalTimes(vdInfo,aDist)
                psDelayIdx=int(np.round((ts-tp)/timeDelta))
                pIdx=int(np.round((aEveTime+tp-refOrig)/timeDelta))+refpIdx # Get P-index relative to reference
                peakDiags.append(pIdx+psDelayIdx)
                peakVerts.append(pIdx)
                peakStas.append(aSta)
            peakDiags,peakVerts,peakStas=np.array(peakDiags),np.array(peakVerts),np.array(peakStas)
            # Collect the diagonals and vertical index values from other times near the peak...
            # ... For varying S-wave (fix-P), and S-weights being high on P-wave
            oDiags=np.array([originInfo['pIdx'][anArg]+originInfo['dIdx'][anArg] for anArg in oArgs])
            # ... For varying P-wave (fix-S), and P-weights being high on S-wave
            oVerts=np.array([originInfo['pIdx'][anArg] for anArg in oArgs])
            oStas=np.array([originInfo['sta'][anArg] for anArg in oArgs])
            # For each station... (should only be one observation per station for a given peak - as rings do not overlap)
            for i,aSta in enumerate(peakStas):
                # ...Look at the difference between the diagonals  
                peakDiag,peakVert=peakDiags[i],peakVerts[i]
                ## NOTE: Two of these lines no longer apply ##
                ## FIXME ##
                staDupArgs=(np.where((oStas==aSta)&
                                     ((np.abs(oDiags-peakDiag)<=(featAvgIdxLen))|      # Varying S-wave (fix P)
                                      (np.abs(oVerts-peakDiag)<=(featAvgIdxLen))|      # P-weights being high on S-wave
                                      (np.abs(oVerts-peakVert)<=(featAvgIdxLen))|      # Varying P-wave (fix-S)
                                      (np.abs(oDiags-peakVert)<=(featAvgIdxLen)))))[0] # S-weights being high on P-wave
                # ...convert back to the main arrays indices, and set them as "seen"
                seenArgs[oArgs[staDupArgs]]=1
            # Finally add this information to the event detections
            outTimes.append(eveTimes[aPeakArg])
            outLocs.append(eveLocs[aPeakArg])
            outProbs.append(eveProbs[aPeakArg])
            outArgs.append(usedOrigArgs[aPeakArg])
            if len(outTimes)>=maxEveCount:
                search=False
                break
    eveDetections={'t':np.array(outTimes),'loc':np.array(outLocs),'prob':np.array(outProbs),'originArgs':outArgs}
    return eveDetections
    
# Create the ROI from the staLoc...
# ...uses min,max locations of stations for X,Y
# ...uses a given distance for the vertical spread
def defaultROI(staLoc,maxVertDist):
    mins=np.min(staLoc[:,1:].astype(float),axis=0).reshape(1,3)
    maxs=np.max(staLoc[:,1:].astype(float),axis=0).reshape(1,3)
    roi=np.vstack((mins,maxs)).T.flatten()
    roi[4]-=0.1*maxVertDist
    roi[5]+=maxVertDist
    return roi

# Locate any number of events in the given window, using a stacking method
# ...tDelta is the origin time precision
# ...tIdxSpread infers how many extra time indicies before/after pick to spread the probability
# ...eveProbMinSum is the minimum summed event probability to declare as an event
# ...maxVertDist is the maximum vertical distance (km) to be used for stacking
# ...maxEveCount, if this number of events is reached - the association will stop
# ...nullBuffer, how many extra indicies to null out trios on either side of diagonals/straight
def stackLocate(pickSet,staLoc,sourceTag,tDelta=0.5,tIdxSpread=1,
                eveProbMinSum=3.0,maxVertDist=10,
                maxEveCount=999999,nullBuffer=0):
    print('Initiating stack locate')
    # Get the basic velocity info
    vdInfo=getVelDelay(sourceTag)
    if vdInfo=='$pass':
        print('No simple velocity information supplied (see getVelDelay in Locate.py)')
        return np.empty((0,5))
    keepArgs=np.ones(len(pickSet)).astype(bool)
    # Remove any picks no station metadata
    for i,entry in enumerate(pickSet):
        if entry[0] not in staLoc[:,0]:
            keepArgs[i]=False
    pickSet=pickSet[keepArgs]
    # Use only P and S picks
    if len(pickSet)>=4:
        pickSet=pickSet[np.where((pickSet[:,1]=='P')|(pickSet[:,1]=='S'))]
    # If there are not enough picks to surpass the minimum event summed probability, return
    if len(pickSet)<eveProbMinSum:
        print('Not enough picks to pass minimum event summed probability')
        return np.empty((0,5))
    QtWidgets.qApp.processEvents()
    # Create the ROI from the staLoc
    roi=defaultROI(staLoc,maxVertDist)
    maxHypDist=((roi[0]-roi[1])**2+(roi[2]-roi[3])**2)**0.5
    # Calculate the max duration a P and S arrival can differ (over the desired distance range)
    PSdelay=np.diff(calcPSarrivalTimes(vdInfo,maxHypDist))[0]
    maxSampShift=int(np.ceil(PSdelay/tDelta))
    maxTT=1*calcPSarrivalTimes(vdInfo,maxHypDist)[0]+2*maxSampShift*tDelta
    # Probability to be spread -/+ the actual pick time
    probSpread=signal.gaussian(1+2*tIdxSpread, std=1.0)
    probSpread/=np.sum(probSpread)
    # Get all of the pIdx,dIdx,prob trios
    originInfo=getOriginInfo(vdInfo,pickSet,staLoc,probSpread,tDelta,maxSampShift)
    # Create the stacking arrays
    ringLay,ringBounds,baseX,baseY,baseZ,baseProb,distErr=getStackRings(roi,vdInfo,maxHypDist,
                                                                        maxVertDist,PSdelay,tDelta)                                            
    # Assign information the ring index, and station grid bounds (for stacking)
    originInfo=assignLayerInfo(originInfo,ringLay,ringBounds,baseX,baseY,baseZ,baseProb)
    # Detect the events
    eveDetections=stackDetectAlgorithm(originInfo,ringLay,baseX,baseY,baseZ,baseProb,tDelta,
                                       len(probSpread)/2+nullBuffer,maxTT,eveProbMinSum,vdInfo,
                                       maxEveCount=maxEveCount)
    numDetect=len(eveDetections['t'])
    mapCurEve=[]
    for i in range(numDetect):
        x,y,z=eveDetections['loc'][i]
        mapCurEve.append([i,x,y,z,eveDetections['t'][i]])   
    print(str(numDetect)+' event(s) associated')            
    return np.array(mapCurEve)

# Return the max origin time error when stacking picks, in units of "tRes"
def getGridError_NumTres(roi,tRes,numXyTres,tResSplit,Vs,
                                    useOneDepth=False,testDepth=None):    
    numTresErr=1 # Set by the user gives (velocity model error + pick error)
    numTresErr+=numXyTres # Addition due to the initial XY grid spacing (set to be one tRes)
    numTresErr+=0.5/tResSplit # From digitizing origin times into bins of finite length
    if useOneDepth:
        maxEpi=((roi[0]-roi[1])**2+(roi[2]-roi[3])**2)**0.5
        d0,d1,d2=0,testDepth,roi[5]
        maxDistErr=np.max(np.abs([(d1**2+maxEpi**2)**0.5-(d0**2+maxEpi**2)**0.5,
                                  (d1**2+maxEpi**2)**0.5-(d2**2+maxEpi**2)**0.5]))
        numTresErr+=maxDistErr/(Vs*tRes) # From the max travel time distance differences between depths
    return numTresErr

# Reference each pick to a station index
def getPickStaIdxs(pickSet,staNames):
    pickStas,pickIdx=np.unique(pickSet[:,0],return_inverse=True)
    pickStaIdxs=np.ones(len(pickIdx),dtype=int)*-1
    for pos in np.unique(pickIdx):
        sta=pickStas[pos]
        if sta in staNames:
            posArgs=np.where(pickIdx==pos)[0]
            pickStaIdxs[posArgs]=np.where(staNames==sta)[0][0]
    # Remove any picks which did not have station metadata
    remArgs=np.where(pickStaIdxs!=-1)[0]
    pickStaIdxs=pickStaIdxs[remArgs]
    pickSet=pickSet[remArgs]
    return pickSet,pickStaIdxs

# Associate any number of picks based off pick alignment to reference solutions
# ...histogram resolution is given by tRes/tResSplit
# ...picks will be assigned a location if they have a residual<tRes
def alignLocate(staLoc,pickSet,sourceTag,minNumPicks=5,
                maxVertDist=10,tRes=1.0,
                tResSplit=5,testDepth=5.0):
    # Sanity checks before beginning
    if maxVertDist<=0 or tRes<=0:
        print('maxVertDist and tRes must be positive numbers')
        return np.empty((0,5))
    elif type(tResSplit)!=int:
        print('tResSplit must be an integer')
        return np.empty((0,5))
    # Grab simple velocity model
    vdInfo=getVelDelay(sourceTag)
    if vdInfo=='$pass':
        print('No simple velocity information supplied (see getVelDelay in Locate.py)')
        return np.empty((0,5))
    # Collect the station information
    staLocs=staLoc[:,1:].astype(float)
    staNames=staLoc[:,0]
    # Remove any picks which are neither P or S
    pickSet=pickSet[np.where((pickSet[:,1]=='P')|(pickSet[:,1]=='S'))]
    # Remove any picks without metadata
    pickSet=getPickStaIdxs(pickSet,staNames)[0]
    # Create the default ROI from the staLoc
    mainRoi=defaultROI(staLoc,maxVertDist)
    if testDepth>mainRoi[5] or testDepth<mainRoi[4]:
        print('testDepth must be within '+str(mainRoi[4])+' and '+str(mainRoi[5])+' which is determined by'+
              'the uppermost station elevation and maxVertDist (roughly)')
        return np.empty((0,5))
    # Make a holder for the returned event locations
    eveLocs,search=[],True
    while search:
        # Do a low resolution sweep to find a maximum position
        maxLoc,maxTime,gridSpace,coarsePickArgs=iterAlignLocate(vdInfo,staLocs,staNames,mainRoi,pickSet,
                                                                   tRes,tResSplit,1,useOneDepth=True,testDepth=testDepth)
        if len(coarsePickArgs)<minNumPicks:
            search=False
            break
        # Given this rough origin, do a search about it
        buff=0.5/tResSplit
        roi=[maxLoc[0]-gridSpace*(0.5+buff),maxLoc[0]+gridSpace*(0.5+buff),
             maxLoc[1]-gridSpace*(0.5+buff),maxLoc[1]+gridSpace*(0.5+buff),
             mainRoi[4],mainRoi[5]]
        maxLoc,maxTime,gridSpace,finePickArgs=iterAlignLocate(vdInfo,staLocs,staNames,roi,pickSet[coarsePickArgs],
                                                                   tRes,tResSplit,buff,useOneDepth=False)
        # Remove any picks were were included in this iterations pickSet
        pickSet=np.array([entry for i,entry in enumerate(pickSet) if i not in coarsePickArgs[finePickArgs]])
        # Append this iterations event if the number of stacked picks >= minNumPicks
        ## May want to allow searching again, as number of picks could drop...##
        ## ...a lot from coarse->fine (allowing another position to show)##
        if len(finePickArgs)<minNumPicks:
            search=False
        else:
            eveLocs.append([len(eveLocs)]+list(maxLoc)+[maxTime])
    eveLocs=np.array(eveLocs,dtype=str)
    if len(eveLocs)==0:
        eveLocs=np.empty((0,5))
    return eveLocs

# Run a iteration of align locate with a specified grid and resolution
def iterAlignLocate(vdInfo,staLocs,staNames,roi,pickSet,
                    tRes,tResSplit,numXyTres,
                    useOneDepth=False,testDepth=None):
    # First test grid spacing (taken from distance of center of a grid cell to a corner)
    errXY=2*(((vdInfo['Vs']*tRes*numXyTres)**2)/2.0)**0.5
    # Make a grid space to test locations
    xi=np.arange(roi[0],roi[1],errXY)
    yi=np.arange(roi[2],roi[3],errXY)
    if useOneDepth:
        zi=np.array([testDepth])
    else:
        zi=np.arange(roi[4],roi[5],errXY)
    xGrid,yGrid,zGrid=np.meshgrid(xi,yi,zi)
    gridLocs=np.array([xGrid.flatten(),yGrid.flatten(),zGrid.flatten()]).T
    # Reference each pick to a station index
    pickSet,pickStaIdxs=getPickStaIdxs(pickSet,staNames)
    pickTimes=pickSet[:,2].astype(float)
    # Increase the index for S-picks (easier referencing later)
    pickStaIdxs[np.where(pickSet[:,1]=='S')]+=len(staNames)
    # Calculate the distance for all locations and stations
    dists=cdist(gridLocs,staLocs)
    # Convert distance to travel times for P and S (P/S is left/right side of array)
    tt=np.hstack((calcPSarrivalTimes(vdInfo,dists)))
    # Align the times based of their delay (so they all represent origin times "origPicks")
    origPicks=pickTimes-tt[:,pickStaIdxs]
    # numTresErr is the factor times tRes which accounts for all potential error in the aligned times (from the true time)
    numTresErr=getGridError_NumTres(roi,tRes,numXyTres,tResSplit,vdInfo['Vs'],
                                    useOneDepth=useOneDepth,testDepth=testDepth)
    # Create an array of histograms for each event (row)
    bins=np.arange(np.min(pickTimes)-np.max(tt)-(numTresErr+1)*tRes,np.max(pickTimes),float(tRes)/tResSplit)
    counts=np.apply_along_axis(lambda a: np.histogram(a, bins=bins)[0], 1, origPicks)
    # Stack the bins cumulatively, use 2x (both ways from origin) numTresErr for the index
    cumSumLen=int(np.ceil(2*numTresErr*tResSplit))
    counts=np.cumsum(counts,axis=1)
    counts=counts[:,cumSumLen:]-counts[:,:-cumSumLen]
    # Assign origin times to each of the bins
    origTimes=bins[cumSumLen:]-tRes+float(tRes)/tResSplit
    # Collect the max position, and see which picks filled this grid cell...
    maxArg=np.unravel_index(np.argmax(counts.flatten()),counts.shape)
    # ...get the origin location and time
    maxLoc,maxOrigTime=gridLocs[maxArg[0]],origTimes[maxArg[1]]
    # ...calculate the travel times for these picks
    maxDists=cdist([maxLoc],staLocs)
    maxTT=np.hstack((calcPSarrivalTimes(vdInfo,maxDists)))
    maxOrigPicks=(pickTimes-maxTT[0,pickStaIdxs])
    maxResiduals=np.abs(maxOrigPicks-maxOrigTime)
    # ...take only the picks which have an abs(residual) < numTresErr*tRes...
    # ...max 1 per station and phase type "staTypes"
    posPickArgs,seenStaTypes=[],[]
    for arg in np.argsort(maxResiduals):
        staType=pickSet[arg,0]+'-----'+pickSet[arg,1]
        if maxResiduals[arg]<float(tRes)*numTresErr and staType not in seenStaTypes:
            posPickArgs.append(arg)
            seenStaTypes.append(staType)
#    print(np.mean(maxOrigPicks-maxOrigTime),float(tRes)*numTresErr)
    return maxLoc,maxOrigTime,errXY,np.array(posPickArgs,dtype=int)