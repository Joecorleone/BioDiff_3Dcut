import numpy as np
import math
from matplotlib import pyplot as plt
import time
from mpl_toolkits.mplot3d import Axes3D
import base64
import string
import os
import copy


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

"""
	global values, which will probably not be altered
"""
imageplateHeight=450#in mm
imageplateRadius=199#in mm
state = 1
#sample is assumed in center position



#maybe also create a singleScan class, to read all the values
class singleScanClass(object):
	
	
	def __init__(self,omega_sampletable,image_file):
		self.omega_sampletable = float(omega_sampletable)
		self.image_file        = image_file
		
		
class scanConfigClass(object):
	"""Class for a scan specific scan as defined in the according config file
	"""	
	
	def __init__(self,StartTime,ExperimentProposal,ExperimentRemark,ExperimentTitle,ScanNumber,ScanCommand,ScanRoi,Scan2ThetaSelector,Quantities,Units,SingleScans,FilePath):
		"""
		set up the configs for a scan containig an array of SingleScans
		"""
		self.startTime            = StartTime.strip()
		self.experimentProposal   = ExperimentProposal.strip()
		self.experimentRemark     = ExperimentRemark.strip()
		self.experimentTitle      = ExperimentTitle.strip()
		self.scanNumber           = ScanNumber.strip()
		self.scanCommand          = ScanCommand.strip()
		self.scanRoi              = ScanRoi
		self.scan2ThetaSelector   = Scan2ThetaSelector
		self.scanQuantities       = Quantities
		self.scanUnits            = Units
		self.singleScans          = SingleScans
		self.numberOfScans        = len(SingleScans)
		self.filePath             = FilePath
		self.directory            = None
		
		self.latticeMono          = 3.355
				
	def setDirectory(self,Directory):
		self.directory = Directory
		
	def checkFiles(self):
            count = 0
            for singleScan in self.singleScans:
                file = singleScan.image_file
                if self.directory is None:
                    if os.path.isfile(file):
                        count+=1
                else:
                    if os.path.isfile('%s%s' %(self.directory,file)):
                        count+=1
            return count
        
        def getWavelength(self):
            return 2.*self.latticeMono*math.sin(self.scan2ThetaSelector/2)
		
#create a Qarray where everything is saved to?
#class contains a numpy array of datapoints in Q and information of the scans
#ToDo
class setOfScans(object):
	def __init__(self,Name,Saved,Filename,Wavelength,
			Firstscan,Lastscan,Scanstep,Omegaoffset,Orientationmatrix,ShiftedImages):
		self.name 		= Name
		self.saved 		= Saved
		self.filename		= Filename
		self.wavelength		= Wavelength
		self.firstscan		= Firstscan
		self.lastscan		= Lastscan
		self.scanstep		= Scanstep
		self.omegaoffset	= Omegaoffset
		self.orientationmatrix	= Orientationmatrix
		self.shiftedImages	= ShiftedImages
	
def loadSetFile(filename):
	""" reads information from a set File, NOT USED BY GUI
	"""
	
	
	if filename.endswith('.set'):
		try:
			file=open(filename,'r')
		except IOError:
			print 'file %s not found!' %filename
			print 'Please specifiy a valid setup file, extension: ".set"'  
			return []
	else:
		try:
			file=open(filename + '.set','r')
		except IOError:
			print 'file %s not found!' %(filename+'.set')
			print 'Please specifiy a valid setup file, extension: ".set"'  
			return	[]
	filelines=file.readlines()
	
	#initialize variabls
	name = None
	filename = None
	wavelength = None
	firstscan = 0
	lastscan = -1
	scanstep = 1
	omegaoffset = 0
	orientationmatrix = np.mat([[1,0,0],[0,1,0],[0,0,1]])
	
	shiftedImages = True
	
	
	
	ListOfLoadedSets=[]
	comments=False
	notOnlyCommentsInLine=False
	scansEntered = False
	saved = False
	multiLineCommentTag="'''"
	singleLineCommentTag="#"
	for line in filelines:
		linestrip = line.strip()
		
		if multiLineCommentTag in linestrip:
			
			if comments:
				#ended at end of the line
				if linestrip.endswith(multiLineCommentTag):
					comments = False
				#ended at start or inbetween of the line
				else:
					linestrip = linestrip.split(multiLineCommentTag)[1].strip()
					comments = False
					notOnlyCommentsInLine = True				
				
			else:
				#started at start of line
				if linestrip.startswith(multiLineCommentTag):
					comments = True
				#started in between or at the end of a line
				else:
					linestrip = linestrip.split(multiLineCommentTag)[0].strip()
					comments = True
					notOnlyCommentsInLine = True
					
				
		if comments and not notOnlyCommentsInLine:
			pass
		else:
			
			if singleLineCommentTag in linestrip:
				if linestrip.startswith(singleLineCommentTag):
					notOnlyCommentsInLine = False
				else:
					linestrip = linestrip.split(singleLineCommentTag)[0].strip()
					notOnlyCommentsInLine = True
			if not singleLineCommentTag in linestrip or notOnlyCommentsInLine:	
				#print linestrip
				if linestrip=='':
					pass
				elif linestrip.startswith('+setOfScans{'):
					scansEntered = True
					saved = False
				elif linestrip.startswith('+savedSet{'):
					scansEntered = True
					saved = True
				elif linestrip.startswith('name:') and scansEntered:
					name = linestrip.replace('name:','').strip()
				elif linestrip.startswith('filename:') and scansEntered:
					filename = linestrip.replace('filename:','').strip()
				elif linestrip.startswith('wavelength:') and scansEntered:
					wavelength = float(linestrip.replace('wavelength:','').strip())
				elif linestrip.startswith('firstscan:') and scansEntered:
					firstscan = int(linestrip.replace('firstscan:','').strip())
				elif linestrip.startswith('lastscan:') and scansEntered:
					lastscan = int(linestrip.replace('lastscan:','').strip())
				elif linestrip.startswith('scanstep:') and scansEntered:
					scanstep = int(linestrip.replace('scanstep:','').strip())
				elif linestrip.startswith('omegaoffset:') and scansEntered:
					omegaoffset = float(linestrip.replace('omegaoffset:','').strip())
				elif linestrip.startswith('orientationmatrix:') and scansEntered:
					orientationmatrix = np.mat(eval(linestrip.replace('orientationmatrix:','').strip()))
				elif linestrip.startswith('shiftedImages:') and scansEntered:
					shiftedImages = linestrip.replace('shiftedImages:','').strip()
				elif linestrip.startswith('}') and scansEntered:
					ListOfLoadedSets.append(setOfScans(name,saved,filename,wavelength,
						firstscan,lastscan,scanstep,omegaoffset,orientationmatrix,shiftedImages))
					
					scansEntered = False
					#reset variables
					name = None
					saved = False
					filename = None
					wavelength = None
					firstscan = 0
					lastscan = -1
					scanstep = 1
					omegaoffset = 0.0
					orientationmatrix = np.array([[1,0,0],[0,1,0],[0,0,1]])
					shiftedImages = True
					
		
			notOnlyCommentsInLine = False
	
	#print ''
	#all configs for sets from .set-file read 
	SofQArrayOfScan=[]
	
	
	for scanSet in ListOfLoadedSets:
		if scanSet.saved:
			print "loading saved sets is not yet included!"
			if len(SofQArrayOfScan)==0:
				#SofQArrayOfScan=loadedOne
				
				pass
			else:
				#hstack
				pass
			#hstack
		else:
			print "reading setofScans from %s:" %scanSet.filename
			scanConfig=readScanFile(scanSet.filename)
			
			inputarray=readFile("%s" %(scanConfig.singleScans[0].image_file),)
			pixelheight=len(inputarray)
			pixelwidth=len(inputarray[0])
			wavelength = scanConfig.getWavelength()
			#print "wavelength:", wavelength
			kincident=2*np.pi/scanSet.wavelength#wavelength
			QstarArray=calcQstar(kincident,pixelwidth,pixelheight)
			print "Qzrange: %.2f to %.2f" %(QstarArray[2].min(),QstarArray[2].max())
			
			scanIntervalOk = True
			scanStepOk = True
			
			if scanSet.firstscan>=0 and scanSet.firstscan<=len(scanConfig.singleScans)-1:
				firstScan = scanSet.firstscan
			elif scanSet.firstscan <= -1:
				firstScan = len(scanConfig.singleScans)+1+scanSet.firstscan
			else:
				print 'Invalid firstscan entered for set of scans %s!' %scanSet.name
				scanIntervalOk = False			
			
			if scanSet.lastscan>=0 and scanSet.lastscan<=len(scanConfig.singleScans)-1:
				lastScan = scanSet.lastscan + 1
			elif scanSet.lastscan <= -1:
				lastScan = len(scanConfig.singleScans)+1+scanSet.lastscan
			else:
				print 'Invalid lastscan entered for set of scans %s!' %scanSet.name
				scanIntervalOk = False
				
			if firstScan>lastScan:
				print 'Empty interval of scans for set of scans %s!' %scanSet.name
				scanIntervalOk = False
				
			if scanSet.scanstep <= 0:
				print 'Choosen scanstep for det of scans %s is invalid!' %scanSet.name
				scanStepOk=False
				
				
			
			if not scanIntervalOk:
				print 'Set of scans %s was skipped, due to the choosen interval!' %scanSet.name
				
			elif not scanStepOk:
				print 'Set of scans %s was skipped, due to the choosen scanstep!' %scanSet.name
				
			else:
				for i,singleScan in enumerate(scanConfig.singleScans[firstScan:lastScan:scanSet.scanstep]):
					omega=singleScan.omega_sampletable+scanSet.omegaoffset
					imagefileTxt="%s" %(singleScan.image_file) 
					IntensArray=readFile(imagefileTxt)
		
					SofQArrayOfScan.append(calcQ(omega,QstarArray,IntensArray,orientationmatrix,shiftedImages))
					print "\tmeasurement %i of %i, omega: %.2f" %(i+1, math.floor((lastScan-firstScan)*1.0/scanSet.scanstep),omega)#len(scanConfig.singleScans), omega)#scanConfig.numberOfScans)	
				print ''
			
	return SofQArrayOfScan		
	
	
	
def readScanFile(filename):
    file=open(filename,'r')
    filelines=file.readlines()
    
    # Meta information
    StartTimeString          = "### NICOS data file, created at "
    ExperimentProposalString = "Exp_proposal : "
    ExperimentRemarkString   = "Exp_remark : "
    ExperimentTitleString    = "Exp_title : "
    ScanNumberString         = "number : "
    ScanCommandString        = "info : "
    
    # Measurement information
    ScanRoiString            = "imgdet_roi : "
    Scan2ThetaSelectorString = "theta2_selectorarm_value :"
    
    
    # Meta information
    StartTime          = None
    ExperimentProposal = None
    ExperimentRemark   = None
    ExperimentTitle    = None
    ScanNumber         = None
    ScanCommand        = None
    
    # Measurement information
    ScanRoi            = None
    Scan2ThetaSelector = None
    
    
    
    #SingleScansString=""
    SingleScans=[]
    
    filePath = filename
    
    inHeaderMeta = False
    
    for i,line in enumerate(filelines):
        if line.startswith('### NICOS'):
            inHeaderMeta = True
            
        if line.startswith('### Scan data'):
            inHeaderMeta = False
        
        # meta header
        if inHeaderMeta:
            if line.find(StartTimeString)>-1:
                StartTime = line.split(StartTimeString)[1].strip()
            elif line.find(ExperimentProposalString)>-1:
                ExperimentProposal = line.split(ExperimentProposalString)[1].strip()
            elif line.find(ExperimentRemarkString)>-1:
                ExperimentRemark = line.split(ExperimentRemarkString)[1].strip()
            elif line.find(ExperimentTitleString)>-1:
                ExperimentTitle = line.split(ExperimentTitleString)[1].strip()
            elif line.find(ScanNumberString)>-1:
                ScanNumber = line.split(ScanNumberString)[1].strip()
            elif line.find(ScanCommandString)>-1:
                ScanCommand = line.split(ScanCommandString)[1].strip()
            elif line.find(ScanRoiString)>-1:
                ScanRoi = np.array(line.split(ScanRoiString)[1].strip()[1:-1].split(','),dtype=int)
            elif line.find(Scan2ThetaSelectorString)>-1:
                Scan2ThetaSelector = float(line.split(Scan2ThetaSelectorString)[1].replace('deg','').strip())
        
        # data header
        else:
            if line.startswith('### Scan data'):
                Quantities = filelines[i+1].strip()[1:].split(';')
                Units      = filelines[i+2].strip()[1:].split(';')
        
            elif not line.startswith('#'):
                linesplit = line.split(';')
                if linesplit[1].find('/')>-1:
                    file_name = linesplit[1].split('/')[-1].strip()
                else:
                    file_name = linesplit[1].strip()
                SingleScans.append(singleScanClass(linesplit[0],file_name))
    
    if not filelines[-1].startswith("### End of NICOS data file"):
        print 'File %s is incomplete!' %filename
        
    # at least omega and lambda <- not correct lambda
    # lambda has to be defined manually
    # config file gives scan numbers with correct omega position
    return scanConfigClass(StartTime,ExperimentProposal,ExperimentRemark,ExperimentTitle,ScanNumber,ScanCommand,ScanRoi,Scan2ThetaSelector,Quantities,Units,SingleScans,filePath)


def readFile(filename,shiftedImages=False):
    """ 
    reads the data files and corrects for shift if desired
    
    TODO only the medium resolution has been implemented for the shift correction
    """
    
    if filename.endswith('.tiff'):
        import tifffile

        fp = r'%s' %filename

        with tifffile.TIFFfile(fp) as tif:
            inputarray = np.array(tif.asarray(), dtype = np.uint32).transpose()
            
        #print inputarray.shape
    
    elif filename.endswith(''):
            
        if module_exists('pandas'):
            import pandas
            inputarray = np.array(pandas.read_csv(filename, sep = '\t', header = None), dtype = np.uint32)
        else:
            print "Please consider installing the module 'pandas' for speed up."
            inputarray = np.loadtxt(filename, dtype = np.uint32)
            
    
    if shiftedImages:
        # detector image from Biodiff can be shifted by a fixe number of pixel, depending on the used resolution
        # detect a shift by checking the beam stop position in the middle of the detector image
        shiftpixelLowRes  = 0   #TODO
        shiftpixelMedRes  = 174
        shiftpixelHighRes = 0   #TODO
        
        pixelheight=len(inputarray)
        pixelwidth=len(inputarray[0])	
        
        if pixelwidth == 2500:
            shiftpixel = shiftpixelMedRes
        else:
            shiftpixel = 0
            print 'Only medium resolution implemented'
        if checkForShift(pixelwidth,pixelheight,inputarray):
            inputarray=np.hstack((inputarray[:,pixelwidth-shiftpixel:],inputarray[:,:pixelwidth-shiftpixel]))
    return inputarray#numpy array
    
    

	
def calcQ(omega,QstarArray,IntensArray,orientationmatrix=np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]),range=[-180,180]):
	omegaR=omega/180.0*np.pi	
	rotMat=np.matrix([[np.cos(omegaR),-np.sin(omegaR),0],[np.sin(omegaR),np.cos(omegaR),0],[0,0,1]])
	QstarArray=orientationmatrix*rotMat*np.matrix(QstarArray)

	return (np.ravel(QstarArray[0]),np.ravel(QstarArray[1]),np.ravel(QstarArray[2]),np.ravel(IntensArray))

def checkForShift(pixelwidth,pixelheight,IntensArray):
	#additional array around coulkd be checked
	if np.array(IntensArray[pixelheight/2-10:pixelheight/2+10,pixelwidth/2-10:pixelwidth/2+10]).mean()>= IntensArray.mean():
		#print "   following measurement is shifted"
		return True
	else:
		return False
	
	
def angleToQstar(kincident,phix,phiy):
	sinPhix=np.matrix(np.sin(phix))
	#sinPhixM90=np.matrix(np.sin(phix-np.pi/2.0))
	cosPhix=np.matrix(np.cos(phix))
	sinPhiy=np.matrix(np.sin(phiy))
	cosPhiy=np.matrix(np.cos(phiy))

	#part with good resolution is on right side seen from origin
	QstarX= cosPhiy.transpose() * cosPhix +1  
	QstarY= cosPhiy.transpose() * sinPhix*(-1)

	QstarZ=sinPhiy.transpose() * np.matrix(np.ones_like(np.sin(phix)))

	QstarX=np.ravel(QstarX)
	QstarY=np.ravel(QstarY)
	QstarZ=np.ravel(QstarZ)	
		
	return kincident*np.array([QstarX,QstarY,QstarZ])#


def calcQstar(kincident,pixelwidth,pixelheight,range=[-180,180]):
	
	rowpixel=np.arange(0,pixelwidth)+0.5 # insert +0.5
	columnpixel=np.arange(0,pixelheight)+0.5 # insert +0.5
	#incoming beam is phix,phiy=0
	phiy=np.arctan((pixelheight*1.0/2.0-columnpixel*1.0)/pixelheight*imageplateHeight/imageplateRadius)	
	phix=rowpixel*1.0/pixelwidth*2*np.pi
	QstarArray=angleToQstar(kincident,phix,phiy)
	return QstarArray

'''
Binning
'''
def createHistHorizontalLayer(SofQarrayOfScan,minQx,maxQx,deltaQx,minQy,maxQy,deltaQy,minQz,maxQz): #binning necessary
	""" NOT USED BY GUI
	"""
	
	resolution=2
	#size=I/I.max()*150*scalePoints/100
	#idx=np.arange(0,len(SofQarrayOfScan[0][0])*len(SofQarrayOfScan),2060)
	
	#create grids:
	xgrid= np.arange(minQx,maxQx,deltaQx)	
	ygrid= np.arange(minQy,maxQy,deltaQy)
	extent=[minQx,maxQx,maxQy,minQy]
	
	xgridh=np.append(xgrid, 2*xgrid[-1]-xgrid[-2])
	ygridh=np.append(ygrid, 2*ygrid[-1]-ygrid[-2])

	rawidx=np.where((SofQarrayOfScan[0][2]>=minQz) & (SofQarrayOfScan[0][2]<=maxQz))
	Qx=SofQarrayOfScan[0][0][rawidx]
	Qy=SofQarrayOfScan[0][1][rawidx]
	# Qz=SofQarrayOfScan[0][2][rawidx]
	I=SofQarrayOfScan[0][3][rawidx]	
	mean=I.mean()	
	if len(SofQarrayOfScan)>1:
		for SofQarray in SofQarrayOfScan[1:]:		
			rawidx=np.where((SofQarray[2]>=minQz) & (SofQarray[2]<=maxQz))
			Qx=np.hstack((Qx,SofQarray[0][rawidx]))
			Qy=np.hstack((Qy,SofQarray[1][rawidx]))
			#Qz=np.hstack((Qz,SofQarray[2][rawidx]))
			I=np.hstack((I,SofQarray[3][rawidx]))
	Inorm=np.ones(I.shape)
	H, xedges, yedges=np.histogram2d(Qy, Qx,(ygridh,xgridh), weights=I)
	Hnorm, xedgesNorm, yedgesNorm=np.histogram2d(Qy, Qx, (ygridh,xgridh), weights=Inorm)
	idx=np.where(Hnorm!=0)
	Intensity=np.array(H)
	Intensity[idx]=H[idx]/Hnorm[idx]
	return (Intensity-mean, extent)


class grid():
	'''
	object to hold the information about the specified grid
	'''
	def __init__(self,minQx,maxQx,deltaQx,minQy,maxQy,deltaQy,minQz,maxQz,deltaQz,usedScanSets=None,omegaOffset=0.,interpolationNum=0):
		self.bins  = (int(round((maxQx-minQx)/float(deltaQx))),int(round((maxQy-minQy)/float(deltaQy))),int(round((maxQz-minQz)/float(deltaQz))))
		self.minQx = minQx
		self.maxQx = maxQx
		self.deltaQx = deltaQx
		self.minQy = minQy
		self.maxQy = maxQy
		self.deltaQy = deltaQy
		self.minQz = minQz
		self.maxQz = maxQz
		self.deltaQz = deltaQz
		
		# some informations to be displayed on the info dialog
		self.usedScanSets = usedScanSets
		self.omegaOffset = omegaOffset
		self.interpolationNum = interpolationNum
		
		self.range = ((minQx,maxQx),(minQy,maxQy),(minQz,maxQz))
		# Meshgrid has the middle of the histogram bin
		#self.xMeshgrid, self.yMeshgrid, self.zMeshgrid  = np.meshgrid(
				#np.linspace(minQx+deltaQx/2.0,maxQx+deltaQx/2.0,num=self.bins[0],endpoint=False),
				#np.linspace(minQy+deltaQy/2.0,maxQy+deltaQy/2.0,num=self.bins[1],endpoint=False),				
				#np.linspace(minQz+deltaQz/2.0,maxQz+deltaQz/2.0,num=self.bins[2],endpoint=False),indexing = 'ij')
		
		self.xBins = np.linspace(minQx,maxQx,num=self.bins[0]+1,endpoint=True)
		self.yBins = np.linspace(minQy,maxQy,num=self.bins[1]+1,endpoint=True)
		self.zBins = np.linspace(minQz,maxQz,num=self.bins[2]+1,endpoint=True)
		gridMinQx,gridMaxQx = minQx+deltaQx/2.0,maxQx-deltaQx/2.0
		gridMinQy,gridMaxQy = minQy+deltaQy/2.0,maxQy-deltaQy/2.0
		gridMinQz,gridMaxQz = minQz+deltaQz/2.0,maxQz-deltaQz/2.0
		
		#print gridMinQx,gridMaxQx
		#print gridMinQy,gridMaxQy
		#print gridMinQz,gridMaxQz
		
		self.xMeshgrid, self.yMeshgrid, self.zMeshgrid  = np.meshgrid(
				np.linspace(gridMinQx,gridMaxQx,num=self.bins[0],endpoint=True),
				np.linspace(gridMinQy,gridMaxQy,num=self.bins[1],endpoint=True),
				np.linspace(gridMinQz,gridMaxQz,num=self.bins[2],endpoint=True),indexing = 'ij')
		#print int((maxQz-minQz)/float(deltaQz))
		
		#print 'xGrid shape:',self.xMeshgrid.shape
		#print 'yGrid shape:',self.yMeshgrid.shape
		#print 'zGrid shape:',self.zMeshgrid.shape,self.zMeshgrid[-1]
		#self.xMeshgrid, self.yMeshgrid, self.zMeshgrid  = np.ravel(self.xMeshgrid), np.ravel(self.yMeshgrid), np.ravel(self.zMeshgrid)
		#self.histIntensity, extent = np.histogramdd((np.arange(0,2),np.arange(0,2),np.arange(0,2)),bins=self.bins,range=self.range,weights = np.zeros((2)))
		self.histIntensity = np.zeros((self.xMeshgrid.shape))
		#extent = np.histogramdd((np.arange(0,2),np.arange(0,2),np.arange(0,2)),bins=self.bins,range=self.range,weights = np.zeros((2)))
		
		# extent is the boundary of the bins
		#print 'EXTENT: x:',extent[0].min(),extent[0].max(),len(extent[0]),'; y:',extent[1].min(),extent[1].max(),len(extent[1]),'; z:',extent[2].min(),extent[2].max(),len(extent[2])
		#print 'HistoShape:',self.histIntensity.shape
		self.histIntensity = np.array(self.histIntensity, dtype = np.uint32)
		self.histCounting  = copy.deepcopy(self.histIntensity)
		
	def __str__(self):
		return "bins: %s, range: %s" %(str(self.bins) ,str(self.range))

	def updateHistogram(self,AddHistIntensity,AddHistCounting):
		self.histIntensity += AddHistIntensity
		self.histCounting  += AddHistCounting
		
	def getNormedIntensity(self):
		idx=np.where(self.histCounting!=0)
		Intensity=np.array(self.histIntensity)
		Intensity[idx]=self.histIntensity[idx]/self.histCounting[idx]
		return Intensity
	
	def fillGrid(self,Kincident,Omegas,Imagefiles,QstarArray,NumInterpol, shiftedImages = False, progressDialog = None, verbose = False):
		inputarray=readFile(Imagefiles[0], shiftedImages)
		pixelheight=len(inputarray)
		pixelwidth=len(inputarray[0])
		n=NumInterpol+1.0
		
		countSteps = 0
		maxSteps = len(Imagefiles)*n
	
		
		for i, (omega, imagefile) in enumerate(zip(Omegas,Imagefiles)):
			
			IntensArray=readFile(imagefile, shiftedImages)
			
			SofQ = calcQ(omega,QstarArray,IntensArray)
			
			self.sortIntoGrid((SofQ[0],SofQ[1],SofQ[2]),SofQ[3])
			
			countSteps +=1
			if not progressDialog is None:
				progressDialog.Update(countSteps/maxSteps*100)
			if verbose:
				print "Measurement %i of %i with omega=%f sorted into the grid" %(i+1,len(Omegas),omega)
			if NumInterpol>0 and i<len(Omegas)-1:
				nextScanOmega  = Omegas[i+1]
				nextScanIntens = readFile(Imagefiles[i+1], shiftedImages)
				for j in range(1,int(n)):
					interPolOmega = omega*(n-j)/n + nextScanOmega * j/n
					SofQ = calcQ(interPolOmega,QstarArray,IntensArray*(n-j)/n + nextScanIntens * j/n)
					self.sortIntoGrid((SofQ[0],SofQ[1],SofQ[2]),SofQ[3])
					countSteps +=1
					if not progressDialog is None:
						progressDialog.Update(countSteps/maxSteps*100)
					if verbose:
						print "\tInterpolation %i of %i with omega=%f sorted into the grid" %(j,NumInterpol,interPolOmega)	
			
			

	def sortIntoGrid(self, QArray,Intensity,fastMethod = False):
		'''
		sorts the detector pixel in a predefined grid
		
		Keywords:
		grid -- contains the information on number of bins and overall range
		QArray -- QCoordinates for each pixel of a single detector image
		Intensity -- measured intensity for each pixel	
		'''
		median = np.median(Intensity)
		idx = np.where(Intensity>median)
		
		if fastMethod:
			
			xbinning = np.digitize(QArray[0][idx],self.xBins)
			ybinning = np.digitize(QArray[1][idx],self.yBins)
			zbinning = np.digitize(QArray[2][idx],self.zBins)   # first entry is everything left of bins and last is everything r
			
			idx2 = np.where((xbinning > 0) & (ybinning > 0) & (zbinning > 0) & (xbinning< len(self.xBins)-1) & (ybinning< len(self.yBins)-1) & (zbinning< len(self.zBins)-1))

			self.histIntensity[xbinning[idx2]-1,ybinning[idx2]-1,zbinning[idx2]-1] += Intensity[idx][idx2]
			self.histCounting[xbinning[idx2]-1,ybinning[idx2]-1,zbinning[idx2]-1] += 1
			
		else:
			Intens, extentIntens = np.histogramdd((QArray[0][idx],QArray[1][idx],QArray[2][idx]),bins=self.bins,range=self.range,weights = Intensity[idx])
			count , extentCount  = np.histogramdd((QArray[0][idx],QArray[1][idx],QArray[2][idx]),bins=self.bins,range=self.range)
			self.updateHistogram(Intens,count)



class cut():
	def __init__(self,CutType,IntensityMap,Extent,Axis1=None,Axis2=None,SlidingAxis=None,SlidingStep = 0.):
		self.cutType = CutType
		self.intensityMap = IntensityMap
		self.extent = Extent
		self.axis1 = Axis1
		self.axis1min = Extent[0]
		self.axis1max = Extent[1]
		self.axis2 = Axis2
		self.axis2min = Extent[2]
		self.axis2max = Extent[3]
		self.slidingAxis = SlidingAxis # list of interval boundaries
		self.slidingStep = SlidingStep
		
	def setAxisLabels(self,Axis1,Axis2,Axis3=None):
		self.axis1 = Axis1
		self.axis2 = Axis2
		self.axis3 = Axis3


def createIntegratingCut(Grid,minQx=None,maxQx=None,minQy=None,maxQy=None,minQz=None,maxQz=None, integrationAxis = 'z'):
	"""
	create a cut in the before filled grid
	
	Keywords:
	Grid -- a grid, which has been filled with detectorpixel from several measurements
	minQx,...,maxQz -- Limits for the cut, also work as integration boundaries
	integrationAxis -- the axis which is integrated along, has be either 'x','y' or 'z'	
	"""
	possibleIntegrationAxes = ['x','y','z']
	if not integrationAxis in possibleIntegrationAxes:
		print "Specified integration axis '%s' is not valid, no cut created!" %str(integrationAxis)
		return
	else:
		if minQx is None:
			minQx = Grid.minQx
		if maxQx is None:
			maxQx = Grid.maxQx
		if minQy is None:
			minQy = Grid.minQy
		if maxQy is None:
			maxQy = Grid.maxQy
		if minQz is None:
			minQz = Grid.minQz
		if maxQz is None:
			maxQz = Grid.maxQz
		
				
		if integrationAxis == 'x':
			return cut('integratingCut',createIntensityMap(Grid,minQx,maxQx,Grid.deltaQx,minQy,maxQy,Grid.deltaQy,minQz,maxQz,Grid.deltaQz,'x'),[minQy,maxQy,minQz,maxQz])
			
		elif integrationAxis == 'y':
			return cut('integratingCut',createIntensityMap(Grid,minQx,maxQx,Grid.deltaQx,minQy,maxQy,Grid.deltaQy,minQz,maxQz,Grid.deltaQz,'y'),[minQx,maxQx,minQz,maxQz])
			
		elif integrationAxis == 'z':
			return cut('integratingCut',createIntensityMap(Grid,minQx,maxQx,Grid.deltaQx,minQy,maxQy,Grid.deltaQy,minQz,maxQz,Grid.deltaQz,'z'),[minQx,maxQx,minQy,maxQy])
		

def createSlidingCut(Grid,minQx=None,maxQx=None,minQy=None,maxQy=None,minQz=None,maxQz=None, slidingAxis = 'z', slidingStep = None):
	"""
	create a cut in the before filled grid
	
	Keywords:
	Grid -- a grid, which has been filled with detectorpixel from several measurements
	minQx,...,maxQz -- Limits for the cut, also work as integration boundaries
	integrationAxis -- the axis which is integrated along, has be either 'x','y' or 'z'	
	"""
	possibleSlidingAxes = ['x','y','z']
	if not slidingAxis in possibleSlidingAxes:
		print "Specified sliding axis '%s' is not valid, no cut created!" %str(slidingAxis)
		return
	else:
		if minQx is None:
			minQx = Grid.minQx
		if maxQx is None:
			maxQx = Grid.maxQx
		if minQy is None:
			minQy = Grid.minQy
		if maxQy is None:
			maxQy = Grid.maxQy
		if minQz is None:
			minQz = Grid.minQz
		if maxQz is None:
			maxQz = Grid.maxQz
		
		idx = np.where((Grid.xMeshgrid >= minQx) & (Grid.xMeshgrid <= maxQx) 
			     & (Grid.yMeshgrid >= minQy) & (Grid.yMeshgrid <= maxQy) 
			     & (Grid.zMeshgrid >= minQz) & (Grid.zMeshgrid <= maxQz))
		
		intens = Grid.histIntensity
		counts = Grid.histCounting
		
		intens = intens[idx]
		counts = counts[idx]
		
		# TODO this is a stupid workaround, a real solution would be better, as this is not ensured to be working all times
		try:
			intens = intens.reshape((maxQx-minQx)/Grid.deltaQx,(maxQy-minQy)/Grid.deltaQy,(maxQz-minQz)/Grid.deltaQz)
			counts = counts.reshape((maxQx-minQx)/Grid.deltaQx,(maxQy-minQy)/Grid.deltaQy,(maxQz-minQz)/Grid.deltaQz)
		except ValueError:
			intens = intens.reshape(int(round((maxQx-minQx)/Grid.deltaQx)),int(round((maxQy-minQy)/Grid.deltaQy)),int(round((maxQz-minQz)/Grid.deltaQz)))
			counts = counts.reshape(int(round((maxQx-minQx)/Grid.deltaQx)),int(round((maxQy-minQy)/Grid.deltaQy)),int(round((maxQz-minQz)/Grid.deltaQz)))
		
		# TODO check if sum axis are correct for 'x' and 'y'
		intensityMap = []
		slidingAxisArray = []
		
		
		# axis in a numpy array are counted outside in
		# zAxis is first Axis: axis=0
		# yAxis is second Axis: axis=1
		# xAxis is third Axis: axis=2
		
		if slidingAxis == 'x':
			count  = 0
			startI = 0
			if slidingStep is None:
				slidingStep = Grid.deltaQx
			
			
			for i in range(intens.shape[0]):
				if i*Grid.deltaQx > slidingStep*count:
					intensityMap.append( (intens[startI:i,:,:].sum(axis=0)/np.maximum(np.ones(counts[startI:i,:,:].shape),counts[startI:i,:,:]).sum(axis=0)).transpose())
					slidingAxisArray.append([minQx+count*slidingStep,minQx+slidingStep*(count+1)])
					count += 1
					startI = i
					
					
			intensityMap.append( (intens[startI:,:,:].sum(axis=0)/np.maximum(np.ones(counts[startI:,:,:].shape),counts[startI:,:,:]).sum(axis=0)).transpose())
			slidingAxisArray.append([minQx+count*slidingStep,minQx+slidingStep*(count+1)])
			return cut('slidingCut', intensityMap,[minQy,maxQy,minQz,maxQz],SlidingAxis=slidingAxisArray,SlidingStep = slidingStep)
			
		elif slidingAxis == 'y':
			count  = 0
			startI = 0
			if slidingStep is None:
				slidingStep = Grid.deltaQy
				
			for i in range(intens.shape[1]):
				if i*Grid.deltaQy > slidingStep*count:
					intensityMap.append( (intens[:,startI:i,:].sum(axis=1)/np.maximum(np.ones(counts[:,startI:i,:].shape),counts[:,startI:i,:]).sum(axis=1)).transpose())
					slidingAxisArray.append([minQy+count*slidingStep,minQy+slidingStep*(count+1)])
					count += 1
					startI = i
					
			intensityMap.append( (intens[:,startI:,:].sum(axis=1)/np.maximum(np.ones(counts[:,startI:,:].shape),counts[:,startI:,:]).sum(axis=1)).transpose())
			slidingAxisArray.append([minQy+count*slidingStep,minQy+slidingStep*(count+1)])
			return cut('slidingCut', intensityMap,[minQx,maxQx,minQz,maxQz],SlidingAxis=slidingAxisArray,SlidingStep = slidingStep)
			
		elif slidingAxis == 'z':
			count  = 0
			startI = 0
			if slidingStep is None:
				slidingStep = Grid.deltaQz
				
			for i in range(intens.shape[2]):
				if i*Grid.deltaQz > slidingStep*count:
					intensityMap.append( (intens[:,:,startI:i].sum(axis=2)/np.maximum(np.ones(counts[:,:,startI:i].shape),counts[:,:,startI:i]).sum(axis=2)).transpose())
					slidingAxisArray.append([minQz+count*slidingStep,minQz+slidingStep*(count+1)])
					count += 1
					startI = i
					
			intensityMap.append( (intens[:,:,startI:].sum(axis=2)/np.maximum(np.ones(counts[:,:,startI:].shape),counts[:,:,startI:]).sum(axis=2)).transpose())
			slidingAxisArray.append([minQz+count*slidingStep,minQz+slidingStep*(count+1)])
			return cut('slidingCut', intensityMap,[minQx,maxQx,minQy,maxQy],SlidingAxis=slidingAxisArray,SlidingStep = slidingStep)

	


def createIntensityMap(Grid,minQx,maxQx,deltaQx,minQy,maxQy,deltaQy,minQz,maxQz,deltaQz,integrationAxis):
	# integrationAxes: 'x','y','z'
	idx = np.where((Grid.xMeshgrid >= minQx) & (Grid.xMeshgrid < maxQx) 
		     & (Grid.yMeshgrid >= minQy) & (Grid.yMeshgrid < maxQy) 
		     & (Grid.zMeshgrid >= minQz) & (Grid.zMeshgrid < maxQz))
	
	#print '---'
	#print Grid.xMeshgrid.min(),Grid.xMeshgrid.max(),Grid.xMeshgrid.shape
	#print Grid.yMeshgrid.min(),Grid.yMeshgrid.max(),Grid.yMeshgrid.shape
	#print Grid.zMeshgrid.min(),Grid.zMeshgrid.max(),Grid.zMeshgrid.shape
	
	intens = Grid.histIntensity
	counts = Grid.histCounting
	
	intens = intens[idx]
	counts = counts[idx]
	
	# TODO this is a stupid workaround, a real solution would be better, as this is not ensured to be working all times
	#print intens.shape
	#print 'minQx',minQx,'maxQx',maxQx,'deltaQx',deltaQx
	#print 'minQy',minQy,'maxQy',maxQy,'deltaQy',deltaQy
	#print 'minQz',minQz,'maxQz',maxQz,'deltaQz',deltaQz
	#print (maxQx-minQx)/Grid.deltaQx,(maxQy-minQy)/Grid.deltaQy,(maxQz-minQz)/Grid.deltaQz
	#print int(round((maxQx-minQx)/Grid.deltaQx)),int(round((maxQy-minQy)/Grid.deltaQy)),int(round((maxQz-minQz)/Grid.deltaQz))
	#print int(np.floor((maxQx-minQx)/Grid.deltaQx)),int(np.floor((maxQy-minQy)/Grid.deltaQy)),int(np.floor((maxQz-minQz)/Grid.deltaQz))
	try:
		#intens = intens.reshape((maxQx-minQx)/Grid.deltaQx,(maxQy-minQy)/Grid.deltaQy,(maxQz-minQz)/Grid.deltaQz)
		#counts = counts.reshape((maxQx-minQx)/Grid.deltaQx,(maxQy-minQy)/Grid.deltaQy,(maxQz-minQz)/Grid.deltaQz)
		intens = intens.reshape(int(round((maxQx-minQx)/Grid.deltaQx)),int(round((maxQy-minQy)/Grid.deltaQy)),int(round((maxQz-minQz)/Grid.deltaQz)))
		counts = counts.reshape(int(round((maxQx-minQx)/Grid.deltaQx)),int(round((maxQy-minQy)/Grid.deltaQy)),int(round((maxQz-minQz)/Grid.deltaQz)))
	except ValueError:
		intens = intens.reshape(int(np.floor((maxQx-minQx)/Grid.deltaQx)),int(np.floor((maxQy-minQy)/Grid.deltaQy)),int(np.floor((maxQz-minQz)/Grid.deltaQz)))
		counts = counts.reshape(int(np.floor((maxQx-minQx)/Grid.deltaQx)),int(np.floor((maxQy-minQy)/Grid.deltaQy)),int(np.floor((maxQz-minQz)/Grid.deltaQz)))
	
	# TODO check if sum axis are correct for 'x' and 'y'
	if integrationAxis == 'x':
		return (intens.sum(axis=0)/np.maximum(np.ones(counts.sum(axis=0).shape),counts.sum(axis=0))).transpose()
		
	elif integrationAxis == 'y':
		return (intens.sum(axis=1)/np.maximum(np.ones(counts.sum(axis=1).shape),counts.sum(axis=1))).transpose()
		
	elif integrationAxis == 'z':
		return (intens.sum(axis=2)/np.maximum(np.ones(counts.sum(axis=2).shape),counts.sum(axis=2))).transpose()

'''
Plotting read Scans
'''
def plotSingleScan(SofQarray):
	fig = plt.figure()
	fig.facecolor=1.0
	ax = fig.gca(projection='3d')
	#size=I/I.max()*150*scalePoints/100
	idx=np.arange(0,len(SofQarray[0]),250)
	I=SofQarray[3]
	color=I/I.max()
	ax.scatter(SofQarray[0][idx],SofQarray[1][idx],SofQarray[2][idx], zdir='z', label='zs=0, zdir=z', marker='o', s=2, c=color[idx], edgecolors=None)
	#ax.scatter(SofQarray[0],SofQarray[1],SofQarray[2], zdir='z', label='zs=0, zdir=z', marker='o', s=2, c=color, edgecolors=None)
	ax.legend()
	ax.facecolor='white'
	plt.show()
	
def plotMultipleScans(SofQarrayOfScan):
	fig = plt.figure()
	fig.facecolor=1.0
	ax = fig.gca(projection='3d')
	#size=I/I.max()*150*scalePoints/100
	idx=np.arange(0,len(SofQarrayOfScan[0][0])*len(SofQarrayOfScan),2060)	
	Qx=SofQarrayOfScan[0][0]
	Qy=SofQarrayOfScan[0][1]
	Qz=SofQarrayOfScan[0][2]
	I =SofQarrayOfScan[0][3]
	color=I/I.max()
	for SofQarray in SofQarrayOfScan[1:]:
		Qx=np.hstack((Qx,SofQarray[0]))
		Qy=np.hstack((Qy,SofQarray[1]))
		Qz=np.hstack((Qz,SofQarray[2]))
		I=np.hstack((I,SofQarray[3]))		
	color=I/I[idx].max()	
	ax.scatter(Qx[idx],Qy[idx],Qz[idx], zdir='z', label='zs=0, zdir=z', marker='o', s=8, c=color[idx], edgecolors='none')
	#ax.scatter(SofQarray[0],SofQarray[1],SofQarray[2], zdir='z', label='zs=0, zdir=z', marker='o', s=2, c=color, edgecolors=None)
	ax.legend()
	ax.facecolor='white'
	plt.show()
		
def twoDplot(Intensity,extent,Imin=None,Imax=None, matplotlibPlugin = None,axis1Label=None,axis2Label=None):
	
	kwds = {}
	
	if matplotlibPlugin is None:
		plot = plt

	else:
		plot = matplotlibPlugin.axes
		
		
	if Imin is not None:
		kwds['vmin'] = Imin
	if Imax is not None: 
		kwds['vmax'] = Imax
	
	colorPlot = plot.imshow(Intensity, extent=extent, origin='lower',interpolation='nearest', aspect='equal', **kwds)
	
	
	if matplotlibPlugin is None:
		if axis1Label is not None:
			plot.xlabel(axis1Label)
		if axis2Label is not None:
			plot.ylabel(axis2Label)
		plot.colorbar()
		plot.show()
	else:
		if axis1Label is not None:
			plot.axes.set_xlabel(axis1Label)
		if axis2Label is not None:
			plot.axes.set_ylabel(axis2Label)
		colorBar = matplotlibPlugin.figure.colorbar(colorPlot)
		return colorPlot, colorBar

def getKiOmegasAndFiles(ListOfScanSets,Omega_Offset = 0):
	imagefiles = []
	omegas     = []
	
	for scanConfig in ListOfScanSets:
		for i,singleScan in enumerate(scanConfig.singleScans):
			if scanConfig.directory is None:
				imagefile = "%s" %(singleScan.image_file)
			else:
				imagefile = "%s%s" %(scanConfig.directory,singleScan.image_file)
			if os.path.isfile(imagefile):
				imagefiles.append(imagefile)
				omegas.append(singleScan.omega_sampletable + Omega_Offset)
			else:
				print "Imagefile %s is not present in folder, will be skipped!" %(imagefile)
	
	omegas = np.array(omegas)
	imagefiles = np.array(imagefiles)
	wavelength = scanConfig.getWavelength()
	#print "wavelength:", wavelength
	kincident=2*np.pi/wavelength
	
	# sort arrays after omega, necessary if several runs are combined
	idx        = np.argsort(omegas)
	omegas     = omegas[idx]
	imagefiles = imagefiles[idx]
	return (kincident,omegas,imagefiles)

def createScanPattern(Kincident,Imagefile):
	# Determine the QstarArray
	"""
	QstarArray is an array containing the Q coordinates corresponding to the pixels of a detector image,
	it is a prototype for all measurements, rotating the array around zAxis 
	"""
	inputarray=readFile(Imagefile)
	pixelheight=len(inputarray)
	pixelwidth=len(inputarray[0])
	QstarArray=calcQstar(Kincident,pixelwidth,pixelheight)
	
	# only valid if crystal has c-axis parallel to rotation axis
	#print "Qzrange: %.2f to %.2f" %(QstarArray[2].min(),QstarArray[2].max())
	return  QstarArray

def main():
	wavelength=2.6737#in Angstroem, can be read from selector
	#possible reading resolutions: 125, 250, 500 in micrometer
	resolution=500#in micrometer
	#changes the number of pixel per picture, can also be read out
	
	#if resolution is the same for each scan you can set constResolution=True
	constResolution=True
	
	#to change initial rotation of sample
	omega_offset=-20.9
	
	
	
	#runname="test_031212_2998"
	#runname="test_031212_3076"
	runname=["test_031212_3076","test_031212_3077"]
	#user should specify the configfilename, each scan filenam is clear then
	
	"""
	Necessary assumption: all scans have the same resolution and wavelength!!!
	sort all runs by their omegavalue
	
	"""
	
	listOfScanSets = []
	
	for run in runname:
		listOfScanSets.append(readScanFile(run))
	
	kincident, omegas,imagefiles = getKiOmegasAndFiles(listOfScanSets,omega_offset)
	QstarArray = createScanPattern(kincident,imagefiles[0])	
	
	# creating the grid, choosing it too large or with too small deltas will unnecessarily increse its size
	minQx, maxQx, deltaQx = -1.5,3.3,0.01
	minQy, maxQy, deltaQy = -1.0,3.5,0.01
	minQz, maxQz, deltaQz = -0.2,0.2,0.1#-1.1,1.1,0.01
	
	histoGrid = grid(minQx,maxQx,deltaQx,minQy,maxQy,deltaQy,minQz,maxQz,deltaQz)
	#print histoGrid
	
	# putting the images into the grid
	# Qcoordinates are created by rotating the QstarArray around omega
	# Intensities will be directly sorted into the predefined grid, to save memory usage
	# therefore only one measurement set and the grid have to be kept in the memory during runtime
	# after filling the grid the user can executes cut on the grid
	
	# interpolat inbetween scans
	numInterpol = 0 #number of additional interpolation steps
	
	
	
	histoGrid.fillGrid(kincident,omegas,imagefiles,QstarArray,numInterpol,True,None,True)
		
	createdCut = createCut(histoGrid,minQz=-0.2,maxQz=0.2,integrationAxis = 'z')
	while True:
		manualVmin = int(raw_input('Enter vmin: '))
		manualVmax = int(raw_input('Enter vmax: '))
		twoDplot(createdCut.intensityMap,extent = createdCut.extent,Imin=manualVmin,Imax=manualVmax,axis1Label = 'Qx',axis2Label = 'Qy') #, vmin=Imin,vmax=Imax
		#plt.colorbar()
		#plt.show()	
	"""
	for i,run in enumerate(runname):
		
				
		
		for i,singleScan in enumerate(scanConfig.singleScans):
			omega=singleScan.omega_sampletable+omega_offset
			imagefileTxt="%s_%i.txt" %(singleScan.image_file,i) 
			#print imagefileTxt
			IntensArray=readFile(imagefileTxt)
			
			#print IntensArray
			#calc some common values
			SofQArrayOfScan.append(calcQ(kincident,pixelwidth,pixelheight,omega,QstarArray,IntensArray))
			#print SofQarray
			print "measurement %i of %i, omega: %.2f" %(i+1, len(scanConfig.singleScans), omega)#scanConfig.numberOfScans)
		

	#return SofQArrayOfScan
	"""


	
def saveArray(Array,filename):
	np.save(filename,Array)
	#TODO: also save a config holding the information of the set of scans
	
def loadArray(filename):
	#TODO: also read a config holding the information of the set of scans
	return np.load(filename)


def createOutputFile(Cut,filename,boolGPscript= True,progressDialog = None):
	extent = Cut.extent
	#create the grid
	
	
	if Cut.cutType == 'integratingCut':
		Intensity = Cut.intensityMap.transpose()
		xgrid=np.linspace(extent[0],extent[1],num=len(Intensity),endpoint=False)
		ygrid=np.linspace(extent[2],extent[3],num=len(Intensity[0]),endpoint=False)
		#print Intensity.shape
		dataoutput = open(filename, 'w')
		maxSteps = len(Intensity)*len(Intensity[0])
		countSteps = 0.0
		for i,y in enumerate(ygrid):
			for j,x in enumerate(xgrid):
				dataoutput.write("%f\t%f\t%f\n" %(x,y,Intensity[j][i]))
				if not progressDialog is None:
					countSteps += 1.0				
					progressDialog.Update(countSteps/maxSteps*100)
			dataoutput.write("\n")
		dataoutput.close()
	
	elif Cut.cutType == 'slidingCut':
		name,suffix = filename.rsplit('.')
		countSteps = 0.0
		maxSteps = len(Cut.intensityMap[0])*len(Cut.intensityMap[0][0])
		for i,singleMap in enumerate(Cut.intensityMap):
			
			dataoutput = open('%s_%03d.%s' %(name,i,suffix), 'w')
					
			for i,y in enumerate(ygrid):
				for j,x in enumerate(xgrid):
					dataoutput.write("%f\t%f\t%f\n" %(x,y,Intensity[j][i]))
					if not progressDialog is None:
						countSteps += 1.0				
						progressDialog.Update(countSteps/(len(Cut.intensityMap) * maxSteps)*100)
				dataoutput.write("\n")
			dataoutput.close()
		
	if boolGPscript:
		if filename.endswith('.map'):
			gnuploscript = open(filename + '.gp', 'w')
		else:
			gnuploscript = open(filename[:-4] + '.gp', 'w')
		gnuploscript.write("reset\nset encoding utf8\nset view map  \nset term png\nset output '%s.png'\nset pm3d interpolate 1,1\nset palette positive nops_allcF maxcolors 0 gamma 1.5 color model RGB\n" %(filename))
		gnuploscript.write("set palette defined ( 0 0 0 1, 0.25 0 1 1, 0.5 0 1 0, 0.75 1 1 0, 1 1 0 0 )\n set ylabel 'Q_y'\nset xlabel 'Q_x'\nset colorbox\nshow colorbox\nset cbrange [%f:%f]\nset title ''\nset size square\nset border lw 0.6\nset tics scale 0.5\n"%(Intensity.min(),Intensity.max()))
		gnuploscript.write("splot [:][:][:] '%s.map' u 1:2:($3*1) with pm3d notitle" %filename)
		gnuploscript.close()



'''
	Menu
'''
def displayMainMenu(state):
	#state = 1 nothing loaded yet
	#state = 2 data loaded, no hist
	#state = 3 data loaded, hist
	print "\n  main menu:"
	print "-------------------"
	print "  1: load new set file"
	if state>1:
		print "  2: create a histogramm from points in a horizontal layer"
	if state>2:
		print "  3: plot the current histogramm"
		print "  4: export the current histogramm"
	print "  0: exit"
	print "-------------------"

	
def menuLoadSetFile():
	global state
	#loading data loop 
	while True:
		setFileName = raw_input('Please enter a SetFile present in the directory: ')
		#print setFileName
		QArray = loadSetFile(setFileName.strip())#loadSetFile('measurementAt4K')
		if len(QArray)>0:
			break
	if state == 1:
		state = 2
	return QArray

def menuSpecifyHisto(QArray):
	global state
	while True:
		gridInQx = raw_input('Specifiy the grid in Qx ("start,end,step"): ')
		startQx,endQx,stepQx = np.array(gridInQx.split(','),dtype=float)
		if endQx>startQx and stepQx > 0:
			break
		else:
			print "Please specify a valid grid!"
	
	while True:
		gridInQy = raw_input('Specifiy the grid in Qy ("start,end,step"): ')
		startQy,endQy,stepQy = np.array(gridInQy.split(','),dtype=float)
		if endQy>startQy and stepQy > 0:
			break
		else:
			print "Please specify a valid grid!"
		
	while True:
		rangeInQz = raw_input('Specifiy the integration range in Qz ("start,end"): ')	
		startQz,endQz = np.array(rangeInQz.split(','),dtype=float)
		if endQz>startQz:
			break
		else:
			print "Please specify a valid range in Qz!"
			
	if state == 2:
		state = 3
	return createHistHorizontalLayer(QArray,startQx,endQx,stepQx,startQy,endQy,stepQy,startQz,endQz)

def menuPlotHisto(Intensity,extent):
	global state
	while True:
		rangeI = raw_input('Specifiy the range in intensitydisplayed ("Imin,Imax")\n "None" value for one of them will adjust intensity limit automatically ("None,Imax"): ')
		IMin,IMax = rangeI.strip().split(',')
		if IMin == "None":
			if IMax == "None":
				twoDplot(Intensity,extent)
				break
			else:
				twoDplot(Intensity,extent,Imax=float(IMax))
				break
		elif IMax == "None":
			twoDplot(Intensity,extent,Imin=float(IMin))
			break
		else:
			if IMax>=IMin:
				twoDplot(Intensity,extent,Imin=float(IMin),Imax=float(IMax))
				break
			else:
				print "Please specify a valid range in intensity!"
				
def menuExportHisto(Intensity,extent):
	global state
	valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
	while True:
		filename = raw_input('Choose a filename for the data file (without extension): ')
		#if os can create such file fine, other wise error
		filename_corrected = ''.join(c for c in filename if c in valid_chars)
		if filename_corrected == filename:
			
			while True:
				boolGPscript = raw_input('Do you wish to create a gnuplot script too? (Y/n) ').strip()
				if boolGPscript == 'y' or boolGPscript == 'Y' or boolGPscript == '':					
					
					boolGPscript = True
					break
				elif boolGPscript == 'n' or boolGPscript == 'N':
					boolGPscript = False
					break
				else:
					print "Please type 'y' or 'n'"
			
			
							
			break
		else:
			print "Please choose a valid filename, e.g. %s" %filename_corrected
			
	createOutputFile(Intensity,extent,filename_corrected,boolGPscript)


		
	
#print '\n\n'
#print '\t##############################'
#print '\t#                            #'
#print '\t#        Biodiffplot         #'
#print '\t#            v0.01           #'
#print '\t#                            #'
#print '\t##############################'
#print '\n'
	

if __name__=='__main__':
	
	main()
	
	
	#QArray = menuLoadSetFile()
	#plotting loop
	while False:
		displayMainMenu(state)
		chooseOption = raw_input('Please choose an option: ').strip()
		
		if chooseOption == '1' and state>=1:
			QArray = menuLoadSetFile()
		elif chooseOption =='2' and state>=2:
			Intensity,extent = menuSpecifyHisto(QArray)
		elif chooseOption =='3' and state>=3:
			menuPlotHisto(Intensity,extent)	
		elif chooseOption =='4' and state>=3:
			menuExportHisto(Intensity,extent)
		elif chooseOption == '0' and state>=1:
			break
		else: 
			print 'Please choose a valid option!' 
			time.sleep(1)

#else:
	#print 'for help execute function "help()"'

	#SofQArrayOfScan = main()
	#Intensity,extent = plotHorizontalLayer(SofQArrayOfScan,-1.5,3.0,0.005,-1.0,3.5,0.005,-0.05,0.05)
	#Intensity,extent = plotHorizontalLayer(SofQArrayOfScan,-2.0,3.5,0.01,-2.0,3.5,0.01,-0.2,0.2)
	#twoDplot(Intensity,extent,Imin=0,Imax=80)
	##
	## fuck ypixel gehen nach aussen
	##
	##
