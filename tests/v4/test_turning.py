import numpy as np
from src.v4.turning import turning_features
def test_turning(): assert turning_features(np.r_[np.zeros(20),np.ones(20)*40],100)["status"] == "OK"
