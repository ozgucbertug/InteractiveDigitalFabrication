__author__ = "Ozguc Capunaman"
__version__ = "2019.03.13"

import rhinoscriptsyntax as rs
import math
import time
import os
import scriptcontext as sc
import clr
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

clr.AddReference("Grasshopper")

class ghApp():
	def __init__(self):
		self._mainDIR = "C:\\Users\\Ozguc Capunaman\\Documents\\GitHub\\InteractiveDigitalFabrication\\sessions\\"
		self._session = None
		
		self.resolution = None
		self.layer_height = None
		self.WObj = rs.PointCoordinates(WObj)

		self.userParam = .6
		sc.sticky["param"] = self.userParam
		sc.sticky["FN"] = None
		sc.sticky["DIR"] = self._mainDIR



	def changeUserParam(self,msg,deltaVal =.05):
		if msg == "inc":
			if self.userParam + deltaVal >= 1.5:
				self.userParam = 1.5
				sc.sticky["param"] = self.userParam

			else:
				self.userParam += deltaVal
				sc.sticky["param"] = self.userParam
		else:
			if self.userParam - deltaVal <= 0:
				self.userParam = 0
				sc.sticky["param"] = self.userParam
			else:
				self.userParam -= deltaVal
				sc.sticky["param"] = self.userParam

	def initSlice(self, init_geo):
		result = []
		plane = rs.PlaneFromPoints((-5000,-5000,0), (0,-5000,0), (-5000,0,0))
		planeSrf = rs.AddPlaneSurface(plane, 10000, 10000)
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
		result = rs.JoinCurves(result)
		for i in range(1,len(result)):
			if not rs.CurveDirectionsMatch(result[0], result[i]):
				rs.ReverseCurve(result[i])
		return result

	def matchWObj(self, geoList):
		ref = rs.AddPoint(0,0,0)
		vec = rs.VectorCreate(rs.AddPoint(self.WObj), ref)
		rot = rs.RotateObjects(geoList, rs.AddPoint(0,0,0), -90, copy=True)
		return rs.CopyObjects(rot, vec)
	
	def crv2pts(self, crvList, startLayer = 1):
		result = []
		print(self.resolution, len(crvList))
		for i in range(startLayer,len(crvList)):
			pts = rs.DivideCurve(crvList[i], self.resolution)
			result.extend(pts)
		print(len(result))
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

	def shift(self, seq, n):
		for i in range(n):
			seq.append(seq.pop(0))
		return seq

	def dist(self, pt0, pt1):
		return rs.Distance(pt0, pt1)

	def divideLR(self, ptList):
		Llist = rs.CopyObjects(ptList[0:][::2])
		Rlist = rs.CopyObjects(ptList[1:][::2])
		self.shift(Rlist, 4)
		return Llist, Rlist

	def mergeLR(self, Llist, Rlist):
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
				if distZ < -10:
					ptList.append(tmp)
					tmp = []
		return ptList

	def clean(self, ptList):
		result = []
		for list in ptList:
			bin = []
			tmp = []
			tmplen = len(list)
	#        print(tmplen)
			for i in range(len(list)):
				if i ==0:
					tmp.append(list[i])
				else:
					if self.dist(list[i-1], list[i]) > 5:
						bin.append(tmp)
						tmp = []
					tmp.append(list[i])
			bin.append(tmp)
			tmpResult = []
			for b in bin:
				if len(b) > len(tmpResult):
					tmpResult = b
			result.append(tmpResult)
	#        print len(tmpResult)
	#        print "-------"
		return result

	def createLines(self, ptList, rebuildCount = 10, degree = 3 ):
		crvList = []
		for i in range(len(ptList)):
			crv = rs.AddInterpCurve(ptList[i])
			rs.RebuildCurve(crv, degree,rebuildCount)
			crvList.append(crv)
		return crvList

	def offsetCurves(self, crvList, offsetFactor=5):
		result = []
		for i in range(len(crvList)):
			x,y,_ = rs.CurveEndPoint(crvList[i])
			vec = rs.VectorCreate((0,0,0),(x,y,0))
			unitVec = rs.VectorUnitize(vec)
			scaledVec = rs.VectorScale(unitVec, offsetFactor)
			tmp = rs.CopyObject(crvList[i], scaledVec)
			result.append(tmp)
		return result
		
	def getExtendedCrv(self, crvList, dist=50, layer_height=2.5, vecMul = .66):
		segmentCount = int(math.floor(dist / layer_height)) - 1
		tmpList = []
		fullHeight = []
		for i in range(len(crvList)):
			extendedCrv = rs.ExtendCurveLength(crvList[i], 2, 0, dist)
			fullHeight.append(extendedCrv)
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

	def getExtendedTP(self, crvList, dist=50, layer_height=2.5):
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

	def extrapolateTP(self, ptCloud):
		ptList = self.dividePtCloud(ptCloud)
		ptList = self.clean(ptList)
		crvL, crvR = self.divideLR(self.createLines(ptList, 5))
		crvMerged = self.mergeLR(crvL, crvR)#[0:][::2]
		offCrv = self.offsetCurves(crvMerged)
		WObjCrv = self.matchWObj(offCrv)
		extCrv = self.getExtendedCrv(WObjCrv, vecMul = self.userParam)
		extLayer = self.getExtendedTP(extCrv)
		extTP = self.crv2pts(extLayer, 1)
		return extTP

	def extrapolateGeo(self, ptCloud):
		ptList = self.dividePtCloud(ptCloud)
		ptList = self.clean(ptList)
		crvL, crvR = self.divideLR(self.createLines(ptList, 5))
		crvMerged = self.mergeLR(crvL, crvR)
		offCrv = self.offsetCurves(crvMerged)
		extCrv = self.getExtendedCrv(offCrv, vecMul = self.userParam)
		return extCrv
		
	def reconSrf(self, crvList):
		assert(crvList != None)
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
						sc.sticky["session"] = self._session
						self.resolution = int(argsList[3])
						self.layer_height = float(argsList[4])
						time.sleep(.1)
						print("Handshaking Done!")
						print("Session: ", self._session, "Layer Subdivision: ", self.resolution, "Layer Height: ", self.layer_height)
						return "-gh_success"
						
					### INIT GEO ###
					elif argsList[1] == "initGeo":
					# (2)filename
						if init_geo == None:
							time.sleep(.1)
							return "-gh_fail_noInitGeo"
						else:
							crvList = self.initSlice(init_geo)
							WObjCrv = self.matchWObj(crvList)
							pts = self.crv2pts(WObjCrv, 1)
							self.pts2xyz(pts, argsList[2])
						time.sleep(.1)
						print("Returning Initial Toolpath Done!")
						return "-gh_success"
					
					### READ SCAN ###
					elif argsList[1] == "extGeo":
					# (2)filename
						# pc = self.xyz2pts(argsList[2])
						# self.extrapolateGeo(pc)
						time.sleep(.1)
						sc.sticky["FN"] = argsList[2]
						# print("Extrapolated Geometry!")
						return "-gh_success"
					elif argsList[1] == "extTP":
					# (2)filename_(3)output
						print("-")
						pc = self.xyz2pts(argsList[2])
						extTP = self.extrapolateTP(pc)
						self.pts2xyz(extTP, argsList[3])
						time.sleep(.1)
						print("Returning Extrapolated Toolpath Done!")
						return "-gh_success"
					elif argsList[1] == "dec" or argsList[1] == "inc":
						self.changeUserParam(argsList[1])
					elif argsList[1] == "WObj":
						self.WObj = [float(argsList[2]), float(argsList[3]), float(argsList[4])]

		return ""     

key = "app"

if sc.sticky.has_key(key):
	app = sc.sticky[key]
else:
	sc.sticky[key] = ghApp()
if RESET:
	sc.sticky[key] = ghApp()

if app != None:
	udp_out = app.run(RUN, udp_in)


	