import numpy as np
from scipy.spatial import distance as dist

def calculate_ear(landmarks, eye_indices):
    # Landmarks are normalized (0.0 to 1.0), so we use them directly
    p2_p6 = dist.euclidean((landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y), 
                           (landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y))
    p3_p5 = dist.euclidean((landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y), 
                           (landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y))
    p1_p4 = dist.euclidean((landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y), 
                           (landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y))
    return (p2_p6 + p3_p5) / (2.0 * p1_p4)

def get_head_pose(landmarks, img_w, img_h):
    # Specific points for pose estimation: Nose tip, Chin, Left eye corner, Right eye corner, Mouth corners
    indices = [1, 152, 33, 263, 61, 291]
    model_points = np.array([
        (0.0, 0.0, 0.0),             # Nose tip
        (0.0, -330.0, -65.0),        # Chin
        (-225.0, 170.0, -135.0),     # Left eye corner
        (225.0, 170.0, -135.0),      # Right eye corner
        (-150.0, -150.0, -125.0),    # Left mouth corner
        (150.0, -150.0, -125.0)      # Right mouth corner
    ])

    image_points = np.array([
        (landmarks[i].x * img_w, landmarks[i].y * img_h) for i in indices
    ], dtype="double")

    focal_length = img_w
    center = (img_w / 2, img_h / 2)
    camera_matrix = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype="double")
    
    dist_coeffs = np.zeros((4, 1)) # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)
    
    return rotation_vector[0][0] 