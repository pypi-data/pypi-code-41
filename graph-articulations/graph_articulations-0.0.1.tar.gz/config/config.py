from pathlib import Path
import os

PART_ROOT = Path(os.environ['ARTICULATIONS_PARTS_DIR'])
CONNECTIVITY_ROOT = Path(os.environ['ARTICULATIONS_GRAPH_DIR'])
MODEL_ROOT = Path(os.environ['ARTICULATIONS_MESH_DIR'])
GRAPH_ART_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
DATA_ROOT = GRAPH_ART_ROOT / 'articulation_data'
