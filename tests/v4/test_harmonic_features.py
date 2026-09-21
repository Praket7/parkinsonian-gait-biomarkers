import numpy as np
from src.v4.harmonic_features import harmonic_ratio, stride_regularity
def test_harmonic_features():
 x=np.sin(np.linspace(0,20,200)); assert np.isfinite(harmonic_ratio(x)) and np.isfinite(stride_regularity(x,20))
