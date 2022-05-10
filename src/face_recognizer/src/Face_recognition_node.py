# nodo identificador

from logging import shutdown
import string
from matplotlib import image
import numpy as np
import imutils
import pickle
import cv2
import rospy 
from cv_bridge import CvBridge, CvBridgeError



class Face_recognition_node:
    def __init__(self) -> None:
        self.sub = rospy.Subscriber('caras_recortadas',image,self.callback)
        self.sub = rospy.Subscriber('lista_de_nombres',string,self.callback)
        self.pub_nombre = rospy.Publisher('nombre',string,queue_size=10)
        self.pub_cara = rospy.Publisher('face', image,queue_size=10)
        self.rate = rospy.Rate(1)
        self.bridge = CvBridge()
        self.crop_face_ready = False


        # load our serialized face embedding model from disk
        print("[INFO] loading face recognizer...")
        embbedModelPath = "../../data/openface.nn4.small2.v1.t7"
        embedder = cv2.dnn.readNetFromTorch(embbedModelPath) # This model is Torch-based and is responsible for extracting facial embeddings via deep learning feature extraction.

        # load the actual face recognition model along with the label encoder
        recognizerPath = "../../data/train_output/recognizer.pickle"
        recognizer = pickle.loads(open(recognizerPath, "rb").read())

        lePath = "../../data/train_output/le.pickle"
        le = pickle.loads(open(lePath, "rb").read())


        while rospy is not shutdown():
            if not self.new_image_ready:
                        continue

            # construct a blob for the face ROI, then pass the blob
		    # through our face embedding model to obtain the 128-d
		    # quantification of the face

            
            # la variable face coge el valor del topic recibido por el nodo anterior
            face = self.detected_face

            #
		    faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96),
			    (0, 0, 0), swapRB=True, crop=False)
		    embedder.setInput(faceBlob)
		    vec = embedder.forward()
		    # perform classification to recognize the face
		    preds = recognizer.predict_proba(vec)[0]
		    j = np.argmax(preds)
		    proba = preds[j]
		    name = le.classes_[j]

            # draw the bounding box of the face along with the associated
		    # probability
		    text = "{}: {:.2f}%".format(name, proba * 100)
		    y = startY - 10 if startY - 10 > 10 else startY + 10
		    cv2.rectangle(image, (startX, startY), (endX, endY),
			    (0, 0, 255), 2)
		    cv2.putText(image, text, (startX, y),
			    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

            # show the output image (publicada como topic mediante ROS)
            face_frame = self.bridge.cv2_to_imgmsg(face)
            self.pub_cara.publish(face_frame)
             

             # Pronunciar el nombre en voz alta


             #
    #leer el topic de face_detection_node
    def callback(self,data):
            if self.new_image_ready:
                return
            try:
                self.detected_face = self.bridge.imgmsg_to_cv2(data, 'bgr8')
                self.detected_face_ready = True
            except CvBridgeError as e:
                print(e)

def main(args):
    rospy.init_node('face_recognizer_node', anonymous=True)
    node =Face_recognition_node ()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("shutting down")


if __name__=='__main__':
    main(sys.argv)

