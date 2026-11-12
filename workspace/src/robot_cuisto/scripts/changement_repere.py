#!/usr/bin/env python3
import sys
import numpy as np
import rospy
from scipy.spatial.transform import Rotation as R
import tf


def changement_repere_generique(point, T_matrice):
    """Applique une matrice de transformation 4x4 à un point [X, Y, Z]."""
    p_hom = np.array([point[0], point[1], point[2], 1.0])
    p_transf_hom = T_matrice @ p_hom
    return p_transf_hom[:3]

def recuperer_matrice_camera_a_robot(target_frame="j2n6s200_link_base",source_frame=None):
    listener = tf.TransformListener()
    
    # Liste des candidats possibles en simulation Gazebo
    if source_frame==None:
        candidats_frames = [
            "rgbd_camera_color_optical_frame",
            "rgbd_camera_link",
            "camera_color_optical_frame"
        ]
        
        source_frame = None
        # Attendre que les liaisons TF soient initialisées dans ROS
        rospy.sleep(2.0)
        
        for frame in candidats_frames:
            if listener.frameExists(target_frame) and listener.frameExists(frame):
                source_frame = frame
                break

    rospy.loginfo(f"Utilisation du repère source TF : {source_frame} vers {target_frame}")

    try:
        listener.waitForTransform(target_frame, source_frame, rospy.Time(0), rospy.Duration(4.0))
        (trans, rot) = listener.lookupTransform(target_frame, source_frame, rospy.Time(0))
        
        try:
            rotation_matrix = R.from_quat(rot).as_matrix()
        except AttributeError:
            rotation_matrix = R.from_quat(rot).as_dcm()

        T = np.identity(4)
        T[:3, :3] = rotation_matrix
        T[:3, 3] = trans
        return T
    except Exception as e:
        rospy.logerr(f"Impossible de récupérer les TF depuis la caméra ({source_frame}) : {e}")
        return None