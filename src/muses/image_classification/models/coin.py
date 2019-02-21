import numpy as np

from keras.datasets import cifar10  # Test variables and test dataset
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Sequential, load_model
# Utilities for one-hot encoding of ground truth values
from keras.utils import np_utils


n_classes = 10
# n_classes = 6
batch_size = 32  # in each iteration, we consider 32 training examples at once
num_epochs = 10  # we iterate 10 times over the entire training set

(X_train, y_train), (X_test, y_test) = cifar10.load_data()

# There are 50000 training examples in CIFAR-10
num_train, height, width, depth = X_train.shape

num_test = X_test.shape[0]  # there are 10000 test examples in CIFAR-10
num_classes = np.unique(y_train).shape[0]  # there are 10 image classes

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= np.max(X_train)  # Normalise data to [0, 1] range
X_test /= np.max(X_test)  # Normalise data to [0, 1] range

# One-hot encode the labels
Y_train = np_utils.to_categorical(y_train, num_classes)

# One-hot encode the labels
Y_test = np_utils.to_categorical(y_test, num_classes)

input_shape = (height, width, depth)
# input_shape = (128, 128, 3)


def create_model():
    """Create model.

    :return:
    """
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu',
                     input_shape=input_shape))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    # model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
    # model.add(Conv2D(32, (3, 3), activation='relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    # model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    # model.add(Conv2D(128, (3, 3), activation='relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(n_classes, activation='softmax'))

    return model


m1 = create_model()
m1.summary()

# using the cross-entropy loss function
m1.compile(
    loss='categorical_crossentropy',
    optimizer='adam',  # Using the Adam optimiser
    metrics=['accuracy']  # Reporting the accuracy
)

m1.save('/models/coin/v1.h5')

new_model = load_model('/models/coin/v1.h5')
# # Train the model using the training set...
# m1.fit(
#     X_train,
#     Y_train,
#     batch_size=batch_size,
#     epochs=num_epochs,
#     verbose=1,
#     validation_split=0.1  # ...holding out 10% of the data for validation
# )

# # # Evaluate the trained model on the test set!
# m1.evaluate(X_test, Y_test, verbose=1)
