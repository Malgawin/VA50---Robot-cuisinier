#import cv2
#from engine.object_detection import ObjectDetection

#od = ObjectDetection("models/yolo11m.pt")

#cap = cv2.videoCapture('')


from ultralytics import YOLO

model = YOLO("yolo11n.pt")

# source=0 si camera du pc sinon 1
results = model.track(source=0, stream=True, show=True)

for r in results:
  # toutes les boxes actuelles
  boxes = r.boxes

  for box in boxes:
    # id de suivi
    track_id = int(box.id[0]) if box.id is not None else "N/A"

    # coordonnées des sommets des boxes
    coords = box.xyxy[0].tolist()
    xmin, ymin, xmax, ymax = [round(c, 2) for c in coords]

    # calculer les dimensions
    largeur = round(xmax - xmin, 2)
    hauteur = round(ymax - ymin, 2)

    # nom de l'objet détécté et confiance
    cls_id = int(box.cls[0])
    nom_classe = model.names[cls_id]
    confiance = float(box.conf[0])

    # affichage dans la console
    print(
        f"[ID: {track_id}] Objet : {nom_classe} | Conf : {confiance:.2f} |"
        f" Coords : ({xmin}, {ymin}, {xmax}, {ymax}) | Dim (L x H) :"
        f" {largeur} x {hauteur}"
    )
