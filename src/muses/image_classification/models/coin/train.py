import os

import argparse
import numpy as np

# from django.conf import settings

from keras.models import load_model
from keras.utils import np_utils
from muses.image_classification.models.coin.data import DATA

from muses.image_classification.conf import IMAGE_CLASSIFICATION_DIR

# model base path
coin_path = os.path.join(IMAGE_CLASSIFICATION_DIR, 'image_classification', 'models', 'coin')

# parser definition
parser = argparse.ArgumentParser(description='training a model')
parser.add_argument('database',
                    help='specify the database to use')
parser.add_argument('model_name',
                    help='specify the name of the model to load')
# parser.add_argument('-bs', '-batch_size',
#                     help='size of training batches')
# parser.add_argument('--num_epochs', type=int,
#                     help='run training for specified number of epochs')


def train_model(model, X_train, Y_train, num_epochs=1, batch_size=32):
    """Training a previously constructed model
    Arguments:
        model {model} -- created model
        X_train {[type]} -- training data
        Y_train {[type]} -- training labels
        batch_size {int} -- amount of training samples per batch
        num_epochs {[int} -- amount of training rounds over all the data
    Returns:
        model -- trained version of initial model
    """
    # Train the model using the training set
    model.fit(
        X_train,
        Y_train,
        batch_size=batch_size,
        epochs=num_epochs,
        verbose=1,
        validation_split=0.1  # ...holding out 10% of the data for validation
    )
    return model


# parse input arguments
args = parser.parse_args()
db = args.database
model_name = args.model_name
# batch_size = args.batch_size
# if(args.num_epochs == None):
#     num_epochs = None
# else:
#     num_epochs = args.num_epochs

# load model
load_path = os.path.join(coin_path, 'saves', model_name)
model = load_model(load_path + '.h5')

# load and organize data (use db param for switching between different databases)
(X_train, y_train), (X_test, y_test) = DATA

# prepare train data
X_train = X_train.astype('float32')
X_train /= np.max(X_train)  # Normalise data to [0, 1] range
Y_train = np_utils.to_categorical(y_train, 10)

# prepare test data
X_test = X_test.astype('float32')
X_test /= np.max(X_test)  # Normalise data to [0, 1] range
Y_test = np_utils.to_categorical(y_test, 10)

# perform model training and evaluate performance
train_model(model, X_train, Y_train)
model.evaluate(X_test, Y_test, verbose=1)

# save model (maybe don't add _trained if model already is trained before)
save_path = os.path.join(coin_path, 'saves', model_name + '_trained')
model.save(save_path + '.h5')
