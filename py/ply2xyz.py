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

def display_inlier_outlier(cloud, ind):
	inlier_cloud = open3d.select_down_sample(cloud, ind)
	outlier_cloud = open3d.select_down_sample(cloud, ind, invert=True)

	print("Showing outliers (red) and inliers (gray): ")
	outlier_cloud.paint_uniform_color([1, 0, 0])
	inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
	draw_geometries([inlier_cloud, outlier_cloud])

display_inlier_outlier(np.asarray(ply2xyz("concave").points), 1)