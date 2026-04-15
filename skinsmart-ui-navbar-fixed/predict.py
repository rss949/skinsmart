import tensorflow as tf
import numpy as np
import cv2

model = tf.keras.models.load_model("ml/model/skin_model.h5")

classes = ["acne", "clear", "dark_spots", "dark_circles"]

def predict_skin(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)
    class_index = np.argmax(preds)
    confidence = float(np.max(preds))

    return classes[class_index], confidence
