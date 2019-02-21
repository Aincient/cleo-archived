import os

import argparse
import numpy as np

from keras.models import load_model

from muses.image_classification.conf import IMAGE_CLASSIFICATION_DIR

# model base path
object_path = os.path.join(IMAGE_CLASSIFICATION_DIR, 'image_classification', 'models', 'object_classifier')

# parser definition
parser = argparse.ArgumentParser(description='classifying an instance')
parser.add_argument('instance',
                    help='specify image file to classify')
parser.add_argument('model_name',
                    help='specify the name of the model to load')


def classify_instance(model, instance):
    """Classifying new data instances
    [description]
    Arguments:
        model {model} -- classifying model
        instance {array} -- image that needs to be classified
    Returns:
        array -- predictions as numpy array
    """
    result = model.predict(instance)
    print(result)
    return result


# parse input arguments
args = parser.parse_args()
instance = args.database
model_name = args.model_name

# prepare image


# load model
load_path = os.path.join(object_path, 'saves', model_name)
model = load_model(load_path + '.h5')

# obtain classification result
classify_instance(model, instance)
