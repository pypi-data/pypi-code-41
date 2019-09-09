from PyQt5.Qt import QApplication
import sys
import numpy as np

firstImage = np.zeros((1649,1475), dtype=np.int16)
#firstImage = np.zeros((1649,1475), dtype=np.float)
#firstImage = np.ones((1649,1475), dtype=np.float)
#firstImage = np.ones((1649,1475), dtype=np.int16)
from pyqtgraph import ImageView

app = QApplication(sys.argv)

imageView = ImageView()
print("type firstImage %s " % type(firstImage))
print("array dtype %s" % firstImage.dtype)
print ("firstImage.min/max %s %s" % (firstImage.min(), firstImage.max()) )
print (firstImage)
print(dir(firstImage))
print("here")
imageView.setImage(firstImage)
print("here")
imageView.show()

sys.exit(app.exec_())