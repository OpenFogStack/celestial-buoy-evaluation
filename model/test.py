from tensorflow import lite as tflite
import numpy as np
import pandas as pd

vals = pd.read_csv("./data.csv")["Temperature"]
min_v, max_v = float(vals.min()), float(vals.max())

print("min: {}, max: {}".format(min_v, max_v))

def scale(x: float) -> np.float32:
    if x < min_v:
        return np.float32(0)
    if x > max_v:
        return np.float32(1)
    return np.float32((x - min_v) / (max_v - min_v))

# https://www.tensorflow.org/lite/api_docs/python/tf/lite/Interpreter#used-in-the-notebooks

interpreter = tflite.Interpreter(model_path="./model.tflite")
interpreter.allocate_tensors()

print("signature list: %s" % interpreter.get_signature_list())

fn = interpreter.get_signature_runner('serving_default')

input_value = scale(0.32901)
output = fn(x=np.array([[[input_value]] * 10]))

print(output["output_0"][0][0])
