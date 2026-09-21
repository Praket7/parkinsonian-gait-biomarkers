import numpy as np
from src.v4.arm_swing import arm_features
def test_arm_features(): assert arm_features(np.sin(np.linspace(0,10,100)),np.sin(np.linspace(0,10,100)))["status"] == "OK"
