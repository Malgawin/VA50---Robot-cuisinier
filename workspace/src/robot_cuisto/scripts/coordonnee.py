#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from ultralytics import YOLO
import cv2

class YoloGazeboNode:
    def __init__(self):
        if not rospy.core.is_initialized():
            rospy.init_node('yolo_gazebo_detection', anonymous=True)
        
        # 1. Chargement du modèle YOLO
        self.model = YOLO("yolo11n.pt")
        self.bridge = CvBridge()
        
        # Stockage des images reçues de Gazebo
        self.cv_image = None
        self.depth_image = None

        # Paramètres intrinsèques de la caméra virtuelle Gazebo (résolution 640x480 par défaut)
        self.fx = 554.38
        self.fy = 554.38
        self.cx = 320.5
        self.cy = 240.5

        # 2. Abonnements aux topics ROS exacts de Gazebo
        rospy.Subscriber("/rgbd_camera/color/image_raw", Image, self.rgb_callback)
        rospy.Subscriber("/rgbd_camera/depth/image_raw", Image, self.depth_callback)
        
        rospy.loginfo("Nœud YOLO pour Gazebo démarré. En attente des flux de la simulation...")

    def rgb_callback(self, data):
        try:
            self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            # Mettre à jour cx et cy dynamiquement selon la taille réelle de l'image
            self.cx = self.cv_image.shape[1] / 2.0
            self.cy = self.cv_image.shape[0] / 2.0
        except CvBridgeError as e:
            rospy.logerr(f"Erreur cv_bridge RGB : {e}")

    def depth_callback(self, data):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
        except CvBridgeError as e:
            rospy.logerr(f"Erreur cv_bridge Depth : {e}")
            
    def objet_reperer(self):
        # lister le nom de tous les objets reperer sur la caméra
        while self.cv_image is None and not rospy.is_shutdown():
            rospy.loginfo_throttle(1.0, "En attente de la première image de la caméra...")
            rospy.sleep(0.1)

        if self.cv_image is None:
            return []

        results = self.model.track(source=self.cv_image, persist=True, verbose=False)
        objet = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                nom_classe = self.model.names[cls_id]
                objet.append(nom_classe)
                print(nom_classe)
        return objet

    def obtenir_coordonnees_objet(self, nom_recherche):
        # récuperer les coordonnées d'un objet en particulier dans le monde caméra
        while self.cv_image is None and not rospy.is_shutdown():
            rospy.sleep(0.1)

        if self.cv_image is None:
            print("[ERREUR] self.cv_image est None")
            return None

        results = self.model.track(source=self.cv_image, persist=True, verbose=False)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                nom_classe = self.model.names[cls_id]

                if nom_classe.lower() == nom_recherche.lower():
                    print("coucou -> Objet trouvé !")
                    coords = box.xyxy[0].tolist()
                    xmin, ymin, xmax, ymax = [round(c, 2) for c in coords]

                    u = (xmin + xmax) / 2.0
                    v = (ymin + ymax) / 2.0

                    if self.depth_image is None:
                        print("[ERREUR] self.depth_image est None (pas de flux de profondeur)")
                        return None

                    try:
                        h_img, w_img = self.depth_image.shape[:2]
                        y1 = max(0, int(ymin))
                        y2 = min(h_img, int(ymax))
                        x1 = max(0, int(xmin))
                        x2 = min(w_img, int(xmax))
                        
                        if y2 > y1 and x2 > x1:
                            roi = self.depth_image[y1:y2, x1:x2]
                            valid_roi = roi[np.isfinite(roi) & (roi > 0)]
                            if valid_roi.size > 0:
                                profondeur = float(np.median(valid_roi))
                                print(f"[DEBUG] Profondeur mesurée : {profondeur} m")
                                
                                # Rétroprojection pixels -> 3D caméra (X, Y, Z)
                                X = (u - self.cx) * profondeur / self.fx
                                Y = (v - self.cy) * profondeur / self.fy
                                Z = profondeur
                                
                                coord_3d = [round(X, 3), round(Y, 3), round(Z, 3)]
                                print(f"[SUCCÈS] Coordonnées 3D Caméra : {coord_3d}")
                                return coord_3d
                            else:
                                print("[ATTENTION] La zone ROI de profondeur est vide (valeurs nulles/NaN).")
                    except Exception as e:
                        print(f"[ERREUR EXCEPTION] {e}")
                        pass

        return None

    def run(self):
        # Afficher en temps réel les objets reperer avec leur niveau de précision ainsi que leurs coordonnées
            rate = rospy.Rate(30) # 30 Hz
            while not rospy.is_shutdown():
                if self.cv_image is not None:
                    results = self.model.track(source=self.cv_image, persist=True, verbose=False)

                    for r in results:
                        boxes = r.boxes
                        for box in boxes:
                            track_id = int(box.id[0]) if box.id is not None else "N/A"
                            coords = box.xyxy[0].tolist()
                            xmin, ymin, xmax, ymax = [round(c, 2) for c in coords]

                            # Calcul des dimensions de la boîte
                            largeur = round(xmax - xmin, 2)
                            hauteur = round(ymax - ymin, 2)

                            # Calcul de la profondeur pour l'affichage en direct
                            profondeur = 0.0
                            if self.depth_image is not None:
                                try:
                                    h_img, w_img = self.depth_image.shape[:2]
                                    y1 = max(0, int(ymin))
                                    y2 = min(h_img, int(ymax))
                                    x1 = max(0, int(xmin))
                                    x2 = min(w_img, int(xmax))
                                    
                                    if y2 > y1 and x2 > x1:
                                        roi = self.depth_image[y1:y2, x1:x2]
                                        valid_roi = roi[np.isfinite(roi) & (roi > 0)]
                                        if valid_roi.size > 0:
                                            profondeur = round(float(np.median(valid_roi)), 2)
                                except Exception:
                                    pass

                            cls_id = int(box.cls[0])
                            nom_classe = self.model.names[cls_id]
                            confiance = float(box.conf[0])

                            print(
                                f"[ID: {track_id}] Objet : {nom_classe} | Conf : {confiance:.2f} | "
                                f"Coords : ({xmin}, {ymin}, {xmax}, {ymax}) | "
                                f"Dim (L x H) : {largeur} x {hauteur} | Profondeur : {profondeur} m"
                            )

                    # Affichage optionnel de la fenêtre vidéo avec les boîtes YOLO
                    annotated_frame = results[0].plot()
                    cv2.imshow("Gazebo YOLO Detection", annotated_frame)
                    cv2.waitKey(1)

                rate.sleep()

if __name__ == '__main__':
    try:
        node = YoloGazeboNode()
        node.run()
        objet = node.objet_reperer()
        if len(objet) == 0:
            print("aucun objet")
        else:
            print(f"Recherche des coordonnées pour : {objet[0]}")
            resultat = node.obtenir_coordonnees_objet(objet[0])
            print("Résultat final :", resultat)
    except rospy.ROSInterruptException:
        cv2.destroyAllWindows()
