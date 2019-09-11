from rp import *

def colab_display_video_file(path,debug=True):
	#Given a path to a video file, display that video file in google colab
	assert isinstance(path,str)
	extension=get_file_extension(path).lower()
	if not extension in {'mp4','avi'} and debug:
		print("colab_display_video_file: warning: "+repr(extension)+' might not be a valid video file extension! (If it is, any this message is annoying, just call colab_display_video_file with parameter debug=True)')
	
	from IPython.display import HTML
	from base64 import b64encode
	mp4 = open(path,'rb').read()
	data_url = "data:video/"+extension+";base64," + b64encode(mp4).decode()