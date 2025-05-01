#!/usr/bin/env python3

import pandas as pd
import tensorflow as tf
import keras
import keras_tuner as kt
import matplotlib.pyplot as plt

label = "winner"
input_filename = "game_data_train.csv"
model_filename = "selector_model.keras"
train_ratio = 0.80
learning_curve_filename = "train_selector_curve.png"
#
# Load the training dataframe, separate into X/y
#
dataframe = pd.read_csv(input_filename, index_col=0)
X = dataframe.drop(label, axis=1)
y = dataframe[label]

y = pd.get_dummies(y, dtype=int)
y = y.drop("green", axis=1)

print(X)
#
# Prepare a tensorflow dataset from the dataframe
#
dataset = tf.data.Dataset.from_tensor_slices((X, y))
# print(dataset)
# print(list(dataset.as_numpy_iterator()))
# print(dataset.element_spec)


#
# Find the shape of the inputs and outputs.
# Necessary for the model to have correctly sized input and output layers
#
#
# This is happening *before* batching, so
# the shape does not yet include the batch size
#
for features, labels in dataset.take(1):
    input_shape = features.shape
    output_shape = labels.shape
print(input_shape)
print(output_shape)


#
# Split the dataset into train and validation sets.
#
dataset_size       = dataset.cardinality().numpy()
train_size         = int(train_ratio * dataset_size)
validate_size      = dataset_size - train_size
train_dataset      = dataset.take(train_size)
validation_dataset = dataset.skip(validate_size)

#
# Cause the datasets to shuffle, internally
#
train_dataset      = train_dataset.shuffle(buffer_size=train_size)
validation_dataset = validation_dataset.shuffle(buffer_size=validate_size)

#
# Cause the datasets to batch.
# Efficiency benefits.
# Training differences.
#
BATCH_SIZE = 32
train_dataset      = train_dataset.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
validation_dataset = validation_dataset.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)



#
# Build the model
#
tf.random.set_seed(80)

def build_model(hp):
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=input_shape))
    model.add(
        keras.layers.Dense(
            hp.Int("layer_0", min_value=500, max_value=1000, step=50),
            activation="leaky_relu"
        )
    )
    model.add(
        keras.layers.Dense(
            hp.Int("layer_1", min_value=500, max_value=1000, step=50),
            activation="leaky_relu"
        )
    )
    if hp.Boolean("dropout0"):
        model.add(keras.layers.Dropout(0.5))
    model.add(
        keras.layers.Dense(
            hp.Int("layer_2", min_value=500, max_value=1000, step=50),
            activation="leaky_relu"
        )
    )
    if hp.Boolean("dropout1"):
        model.add(keras.layers.Dropout(0.4))
    model.add(
        keras.layers.Dense(
            hp.Int("layer_3", min_value=500, max_value=1000, step=50),
            activation="leaky_relu"
        )
    )
    if hp.Boolean("dropout2"):
        model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(256, activation="leaky_relu"))
    model.add(keras.layers.Dense(256, activation="leaky_relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(128, activation="leaky_relu"))
    model.add(keras.layers.Dense(128, activation="leaky_relu"))
    model.add(keras.layers.Dropout(0.3))
    model.add(keras.layers.Dense(64, activation="leaky_relu"))
    model.add(keras.layers.Dense(64, activation="leaky_relu"))
    model.add(keras.layers.Dense(32, activation="leaky_relu"))
    model.add(keras.layers.Dense(32, activation="leaky_relu"))
    model.add(keras.layers.Dense(16, activation="leaky_relu"))
    model.add(keras.layers.Dense(16, activation="leaky_relu"))
    model.add(keras.layers.Dense(8, activation="leaky_relu"))
    model.add(keras.layers.Dense(8, activation="leaky_relu"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    learning_rate = hp.Float("lr", min_value=0.00001, max_value=0.0005, sampling="log")

    loss = "binary_crossentropy"
    model.compile(loss=loss,
              optimizer=keras.optimizers.RMSprop(learning_rate=learning_rate),
              metrics=["accuracy"])
    return model

tuner = kt.Hyperband(
    build_model,
    objective='val_loss',
    max_epochs=150,
    factor=3,
    directory="search"
)

#print(model.summary())
#print(model.layers[1].get_weights())

#
# Compile the model
#



#
# Update the learning rate dynamically
#
def scheduler(epoch, learning_rate):
    r = learning_rate
    if epoch >= 10:
        r = learning_rate * float(tf.exp(-0.005))
    return r
learning_rate_callback = keras.callbacks.LearningRateScheduler(scheduler)

#
# Stop training if validation loss does not improve
#
early_stop_callback = keras.callbacks.EarlyStopping(monitor="val_loss", patience=17, restore_best_weights=True)

#
# Train for up to epoch_count epochs
#
""" epoch_count = 150
history = model.fit(x=train_dataset,
                    epochs=epoch_count,
                    validation_data=validation_dataset,
                    callbacks=[learning_rate_callback, early_stop_callback])
epochs = len(history.epoch) """
tuner.search(
    x=train_dataset,
    validation_data=validation_dataset,
    callbacks=[learning_rate_callback, early_stop_callback]
)

best_hps=tuner.get_best_hyperparameters(num_trials=1)[0]

print(f"""
The hyperparameter search is complete. The optimal number of units in the first densely-connected
layer is {best_hps.get('units')} and the optimal learning rate for the optimizer
is {best_hps.get('learning_rate')}.
""")


#
# Save the model
#
model.save(model_filename)
