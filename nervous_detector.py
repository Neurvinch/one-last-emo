from imutils import face_utils
import numpy as np
from scipy.spatial import distance

def lip_distance(shape):
    shape = face_utils.shape_to_np(shape)
    top_lip = shape[50:53]
    bottom_lip = shape[56:59]
    dist = distance.euclidean(np.mean(top_lip, axis=0), np.mean(bottom_lip, axis=0))
    return dist

def is_nervous(shape):
    dist = lip_distance(shape)
    return dist < 5  # Empirical value, can be adjusted with more data
