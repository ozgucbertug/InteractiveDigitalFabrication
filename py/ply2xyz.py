import open3d
import numpy as np

def ply2xyz(filename = "", srcPath = "../ply/", targetPath = "../xyz/"):
	srcDir = srcPath + filename + ".ply"
	ply = open3d.read_triangle_mesh(srcDir)

	xyz = open3d.PointCloud()
	xyz.points = ply.vertices
	targetDir = targetPath + filename + ".xyz"
	print(targetDir)
	open3d.write_point_cloud(targetDir, xyz)
	return xyz