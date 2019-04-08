__author__ = "Ozguc Capunaman"
__version__ = "2019.03.13"

import rhinoscriptsyntax as rs
import math
import time
import os
import scriptcontext as sc

class ghApp():
	def __init__(self):
		self._mainDIR = "C:\\Users\\Ozguc Capunaman\\Documents\\GitHub\\InteractiveDigitalFabrication\\sessions\\"
		self._session = None
		
		self.resolution = None
		self.layer_height = None

	def initSlice(self, init_geo):
		result = []
		plane = rs.PlaneFromPoints((-500,-500,0), (0,-500,0), (-500,0,0))
		planeSrf = rs.AddPlaneSurface(plane, 1000, 1000)
		crv = rs.IntersectBreps(init_geo, planeSrf)
		result.append(crv)
		while True:
			vec = rs.CreateVector((0,0,self.layer_height))
			planeSrf = rs.MoveObject(planeSrf, vec)
			crv = rs.IntersectBreps(init_geo, planeSrf)
			if crv == None:
				break
			else:
				result.append(crv)
		return result
	
	def crv2pts(self, crvList):
		result = []
		for i in range(len(crvList)):
			pts = rs.DivideCurve(crvList[i], self.resolution)
			result.extend(pts)
		return result
		
	def pts2xyz(self, pts, FN):
		filepath = self._mainDIR+self._session+"\\"+FN+".xyz"
		file = open(filepath, "w+")
		for i in range(len(pts)):
			coord = pts[i]
			file.write(str(coord[0]) + " " + str(coord[1]) + " " + str(coord[2]) + "\r\n")
		file.close()
	
	def xyz2pts(self, FN):
		filepath = self._mainDIR+self._session+"\\"+FN+".xyz"
		if(os.path.exists(filepath)):
			result = []
			with open(filepath) as fp:  
			   line = fp.readline()
			   while line:
				   curLine = line.strip()
				   coord = curLine.split(' ')
				   for i in range(len(coord)):
					   coord[i] = float(coord[i])
				   result.append(rs.AddPoint(coord))
				   line = fp.readline()
			return result
		else:
			raise Exception('File doesn\'t exist!')

	def shift(seq, n):
		for i in range(n):
			seq.append(seq.pop(0))
		return seq

	def divideLR(ptList):
		Llist = rs.CopyObjects(ptList[0:][::2])
		Rlist = rs.CopyObjects(ptList[1:][::2])
		shift(Rlist, 4)
		return Llist, Rlist

	def mergeLR(Llist, Rlist):
		assert(len(Llist) == len(Rlist))
		mergedList = []
		for i in range(len(Llist)):
			if rs.CurveLength(Llist[i]) >= rs.CurveLength(Rlist[i]):
				mergedList.append(rs.CopyObject(Llist[i]))
			else:
				mergedList.append(rs.CopyObject(Rlist[i]))
		return mergedList
	
	def dividePtCloud(self, points):
		ptList = []
		for i in range(len(points)):
			if i == 0:
				tmp = []
			elif i == len(points)-1:
				tmp.append(points[i])
				ptList.append(tmp)
			else:
				tmp.append(points[i])
				_,_,curZ = rs.PointCoordinates(points[i])
				_,_,nextZ = rs.PointCoordinates(points[i+1])
				distZ = curZ - nextZ
				if distZ < -50:
					ptList.append(tmp)
					tmp = []
		return ptList

	def createLines(ptList, rebuildCount = 10, degree = 3 ):
		crvList = []
		for i in range(len(ptList)):
			crv = rs.AddInterpCurve(ptList[i])
			rs.RebuildCurve(crv, degree,rebuildCount)
			crvList.append(crv)
		return crvList

	def offsetCurves(crvList, offsetFactor=5):
		result = []
		for i in range(len(crvList)):
			x,y,_ = rs.CurveEndPoint(crvList[i])
			vec = rs.VectorCreate((0,0,0),(x,y,0))
			unitVec = rs.VectorUnitize(vec)
			scaledVec = rs.VectorScale(unitVec, offsetFactor)
			tmp = rs.CopyObject(crvList[i], scaledVec)
			result.append(tmp)
		return result
		
	def getExtendedCrv(crvList, dist=50, layer_height=2.5, vecMul = .66):
		segmentCount = int(math.floor(dist / layer_height)) - 1
		tmpList = []
		for i in range(len(crvList)):
			extendedCrv = rs.ExtendCurveLength(crvList[i], 2, 0, dist)
			domStart, domEnd = rs.CurveDomain(extendedCrv)
			trimmedCrv = rs.TrimCurve(extendedCrv, (domStart, 0))
			tmpList.append(trimmedCrv)
		tmp = []
		###Smooth Curves###
		for i in range(len(tmpList)):
			bottomPt = rs.CurveEndPoint(tmpList[i])
			zVec = rs.VectorAdd((0,0,0),(0,0,dist))
			topPt = rs.CopyObject(bottomPt, zVec)
			line = rs.AddLine(bottomPt, topPt)
			crvPts = rs.DivideCurve(tmpList[i], segmentCount)
			LinePts = rs.DivideCurve(line, segmentCount)
			for i in range(segmentCount):
				tmpVec = rs.VectorCreate(LinePts[segmentCount-i-1], crvPts[i])
				tmpVec = rs.VectorScale(tmpVec, vecMul)
				rs.MoveObject(crvPts[i], tmpVec)
			tmp.append(rs.AddInterpCurve(crvPts))
			result = []
			for crv in tmp:
				crvLen = rs.CurveLength(crv)
				if crvLen < dist:
					tmpExt = dist-crvLen
					result.append(rs.ExtendCurveLength(crv, 2, 0, tmpExt))
				else:
					result.append(rs.CopyObject(crv))
		return result

	def getExtendedTP(crvList, dist=50, layer_height=2.5):
		result = []
		ptsList = []
		lenList = []
		segmentCount = math.floor(dist / layer_height)
		for crv in crvList:
			tmp = rs.DivideCurve(crv, segmentCount)
			lenList.append(len(tmp))
			ptsList.append(tmp)
		for i in range(min(lenList)):
			tmp = []
			for j in range(len(ptsList)):
				tmp.append(ptsList[j][i])
			tmp.append(ptsList[0][i])
			tmpCrv = rs.AddInterpCurve(tmp, knotstyle=3)
			result.append(tmpCrv)
		result.reverse()
		return result

	def interpolateTP(ptCloud):
		ptList = self.dividePtCloud(pts)
		crvL, crvR = self.divideLR(createLines(ptList, 5))
		crvMerged = self.mergeLR(crvL, crvR)
		
		offCrv = self.offsetCurves(crvMerged)
		extCrv = self.getExtendedCrv(offCrv)
		extTP = self.getExtendedTP(extCrv)
		return extTP 
		
	def reconSrf(self, crvList):
		return rs.AddLoftSrf(crvList, closed = True)
	
	def decodeMessage(self, udp_in):
		return udp_in.split("_")
	
	def run(self, RUN, udp_in):
		if RUN:
			if udp_in != b'':
				argsList = self.decodeMessage(udp_in)
				if argsList[0] == "+gh":
					
					### HANDSHAKE ###
					if argsList[1] == "handshake":
					# (2)session_(3)resolution_(4)layerheight
						self._session = argsList[2]
						self.resolution = int(argsList[3])
						self.layer_height = float(argsList[4])
						time.sleep(.1)
						print("Handshaking Done!")
						return "-gh_success"
						
					### INIT GEO ###
					elif argsList[1] == "initGeo":
					# (2)filename
						if init_geo == None:
							time.sleep(.1)
							return "-gh_fail_noInitGeo"
						else:
							crvList = self.initSlice(init_geo)
							pts = self.crv2pts(crvList)
							self.pts2xyz(pts, argsList[2])
						time.sleep(.1)
						print("Returning Initial Toolpath Done!")
						return "-gh_success"
					
					### READ SCAN ###
					elif argsList[1] == "readScan":
					# (2)filename_(3)output
						pc = self.xyz2pts(argsList[2])
						pc = self.dividePtCloud(pc)
						crvList = self.createLines(pc)

						extCrv = self.getExtendedCurves(crvList)
						extTp = self.getExtendedToolpath(extCrv)
						extPts = self.crv2pts(extTp)

						self.pts2xyz(extPts, argsList[3])

						time.sleep(.1)
						print("Reading Point Cloud Done!")
						return "-gh_success"
						
		return ""     

key = "app"

if sc.sticky.has_key(key):
	app = sc.sticky[key]
else:
	app = None
if RESET:
	sc.sticky[key] = ghApp()

if app != None:
	udp_out = app.run(RUN, udp_in)