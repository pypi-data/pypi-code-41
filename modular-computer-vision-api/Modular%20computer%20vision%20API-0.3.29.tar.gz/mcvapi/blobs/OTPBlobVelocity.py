import numpy as np, collections, tools, math
from OTPBase import OTPBase

class OTPBlobVelocity(OTPBase):
	_bvel_last_blobs = None

	def __init__(self, **kwargs):
		super(OTPBlobVelocity, self).__init__(**kwargs)
		self._bvel_last_blobs = []

	def compute(self, blobs):
		if len(blobs)==len(self._bvel_last_blobs):
			for i, (cblob, pblob) in enumerate(zip( blobs, self._bvel_last_blobs )):
				
				cblob._vel_vector = cblob._centroid[0]-pblob._centroid[0], cblob._centroid[1]-pblob._centroid[1]

				cblob._velocity = tools.lin_dist( cblob._centroid, pblob._centroid )

				cblob._velocity_angle_rad = tools.points_angle( (0,0), cblob._vel_vector )
				cblob._angular_velocity_rad = cblob._velocity_angle_rad - pblob._velocity_angle_rad
				
				cblob._translational_angle_rad = cblob.angle_radians-cblob._velocity_angle_rad
				if abs(cblob._translational_angle_rad)>(math.pi/2): cblob._velocity = -cblob._velocity
					#mov_angle -= math.pi*2
					#mov_angle = -mov_angle
				
				#cblob._movement_angle = mov_angle
				#print i, math.degrees(tools.points_angle( (0,0), cblob._vel_vector ) ), \
				#	math.degrees( tools.points_angle( cblob._tail, cblob._head ) )

				#cblob._angle_vel = pblob._angle_2_vertical_degrees - cblob._angle_2_vertical_degrees
		else:
			#Number of blobs are diferent from the past
			for blob in blobs: 
				
				blob._velocity = None
				blob._vel_vector = [None,None]
				blob._angular_velocity_rad = 0
				blob._velocity_angle_rad = 0
				blob._translational_angle_rad = 0
				
		
		self._bvel_last_blobs = blobs
		return blobs

	def process(self, image):
		blobs = super(OTPBlobVelocity, self).process(image)
		return OTPBlobVelocity.compute(self, blobs)



