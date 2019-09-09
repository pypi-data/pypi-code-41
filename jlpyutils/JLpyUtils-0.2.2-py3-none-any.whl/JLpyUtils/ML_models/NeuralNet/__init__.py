try:
    import tensorflow as __tf__
    
except ImportError:
    sys.exit("""You need tensorflow. run: '!pip install tensorflow' or '!pip install tensorflow-gpu'""")
    
import JLpyUtils.ML_models.NeuralNet.ConvNet
import JLpyUtils.ML_models.NeuralNet.plot
import JLpyUtils.ML_models.NeuralNet.search
import JLpyUtils.ML_models.NeuralNet.DenseNet
import JLpyUtils.ML_models.NeuralNet.utils