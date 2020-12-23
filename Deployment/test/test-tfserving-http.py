# -----------------------------------
# Testing TensorFlow Serving via HTTP
# Author: Mirko Rodriguez
# -----------------------------------

import argparse
import json
import numpy as np
import requests
from tensorflow.keras.preprocessing import image

# Args
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Image PATH is required.")
ap.add_argument("-m", "--model", required=True, help="Model NAME is required.")
ap.add_argument("-v", "--version", required=True, help="Model VERSION is required.")
ap.add_argument("-p", "--port", required=True, help="Model PORT number is required.")
args = vars(ap.parse_args())

image_path = args['image']
model_name = args['model']
model_version = args['version']
port = args['port']

print("\nModel:",model_name)
print("Model version:",model_version)
print("Image:",image_path)
print("Port:",port)


# Loading image
test_image = image.load_img(image_path,target_size = (224, 224))
test_image = image.img_to_array(test_image)
test_image = np.expand_dims(test_image, axis = 0)
test_image = test_image.astype('float32')
test_image /= 255.0

data = json.dumps({"signature_name": "serving_default", "instances": test_image.tolist()})
headers = {"content-type": "application/json"}
uri = ''.join(['http://127.0.0.1:',port,'/v',model_version,'/models/',model_name,':predict'])
print("URI:",uri)

json_response = requests.post(uri, data=data, headers=headers)
predictions = json.loads(json_response.text)['predictions'][0]
print("\npredictions:",predictions)

index = np.argmax(predictions)
CLASSES = ["Cat", "Dog"] 
ClassPred = CLASSES[index]
ClassProb = predictions[index]

print("Index:", index)
print("Pred:", ClassPred)
print("Prob:", ClassProb)
