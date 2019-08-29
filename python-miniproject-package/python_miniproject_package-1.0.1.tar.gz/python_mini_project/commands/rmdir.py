import os 
  

def run(path):
    try: 
        print(os.rmdir(path)) 
        print("Directory %s has been removed successfully" %path)
    except OSError: 
        print("Directory %s can not be removed as it is not empty" %path)