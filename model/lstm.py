#
#
# LSTM weather prediction demo
# Written by: Dan R 2020
# https://github.com/danrustia11/WeatherLSTM
#
#

#
# Core Keras libraries
#
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

#
# For data conditioning
#
from scipy.ndimage import gaussian_filter1d
from scipy.signal import medfilt
import numpy as np

#
# Make results reproducible
#
from numpy.random import seed
seed(1)

#
# Other essential libraries
#
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import sklearn.metrics
from numpy import array
import typing
import sys

#
# Set input number of timestamps and training days
#
n_timestamp = 10
train_days = 1500  # number of days to train from
testing_days = 500 # number of days to be predicted
n_epochs = 25

if __name__ == "__main__":
    # args:
    # 1: path to dataset
    # 2: model save path
    if len(sys.argv) < 3:
        print("Usage: python3 lstm.py <dataset_path> <model_save_path>")
        sys.exit()

    dataset_path = sys.argv[1]
    model_save_path = sys.argv[2]

    dataset = pd.read_csv(dataset_path).reset_index(drop=True)


    train_set = dataset[0:train_days].reset_index(drop=True)
    test_set = dataset[train_days: train_days+testing_days].reset_index(drop=True)

    training_set = dataset.iloc[:, 1:2].values
    test_set = dataset.iloc[:, 1:2].values

    #
    # Normalize data first
    #
    sc = MinMaxScaler(feature_range = (0, 1))
    training_set_scaled = sc.fit_transform(training_set)
    test_set_scaled = sc.fit_transform(test_set)

    #
    # Split data into n_timestamp
    #
    def data_split(sequence: np.ndarray, n_timestamp: int) -> typing.Tuple[np.ndarray, np.ndarray]:
        X = []
        y = []
        for i in range(len(sequence)):
            end_ix = i + n_timestamp
            if end_ix > len(sequence)-1:
                break
            # i to end_ix as input
            # end_ix as target output
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
            X.append(seq_x)
            y.append(seq_y)
        return array(X), array(y)


    X_train, y_train = data_split(training_set_scaled, n_timestamp)
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)

    X_test, y_test = data_split(training_set_scaled, n_timestamp)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    print(X_train.shape)

    # Stacked LSTM
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(n_timestamp, 1), name='input'),
        tf.keras.layers.LSTM(125, activation='sigmoid', return_sequences=True, input_shape=(X_train.shape[1], 1)),
        tf.keras.layers.LSTM(125, activation='relu'),
        tf.keras.layers.Dense(1)
    ])


    #
    # Start training
    #
    model.compile(optimizer = 'adam', loss = 'mean_squared_error')
    history = model.fit(X_train, y_train, epochs = n_epochs, batch_size = 32)

    run_model = tf.function(lambda x: model(x))
    # This is important, let's fix the input size.
    STEPS = n_timestamp
    INPUT_SIZE = 1
    concrete_func = run_model.get_concrete_function(
        tf.TensorSpec([STEPS, INPUT_SIZE], model.inputs[0].dtype))

    # model directory.
    model.save("./model_keras", save_format="tf", signatures=concrete_func)

    converter = tf.lite.TFLiteConverter.from_saved_model("./model_keras")
    tflite_model = converter.convert()

    # converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    # converter._experimental_lower_tensor_list_ops = False

    # tflite_model = converter.convert()

    # Save the model.
    with open(model_save_path, "wb") as f:
        f.write(tflite_model)

    y_predicted = model.predict(X_test)

    #
    # 'De-normalize' the data
    #
    y_predicted_descaled = sc.inverse_transform(y_predicted)
    y_train_descaled = sc.inverse_transform(y_train)
    y_test_descaled = sc.inverse_transform(y_test)
    y_pred = y_predicted.ravel()
    y_pred = [round(yx, 2) for yx in y_pred]
    y_tested = y_test.ravel()

    mse = sklearn.metrics.mean_squared_error(y_test_descaled, y_predicted_descaled)
    r2 = sklearn.metrics.r2_score(y_test_descaled, y_predicted_descaled)
    print("mse=" + str(round(mse,2)))
    print("r2=" + str(round(r2,2)))