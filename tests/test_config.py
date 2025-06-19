import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_dir_exists():
    from utils.config import DATA_DIR
    assert DATA_DIR == "data"
    assert os.path.exists(DATA_DIR)