import os

import argparse
import imp

# from django.conf import settings


# model base path
# coin_path = os.path.join(settings.IMAGE_CLASSIFICATION_DIR, 'models', 'coin')
from muses.image_classification.conf import IMAGE_CLASSIFICATION_DIR

object_path = os.path.join(
    IMAGE_CLASSIFICATION_DIR,
    'image_classification',
    'models',
    'object_classifier'
)

# parser definition
parser = argparse.ArgumentParser(description='creating a model')
parser.add_argument('model_definition',
                    help='specify the model_definition file to use')
parser.add_argument('model_name',
                    help='specify the (save)name of the model')


def create_model(model_definition):
    """create a model from its definition file
       Arguments:
        model_definition {model} -- architecture definition of a model
       Returns:
        model -- compiled model according to definition file specifications
    """
    try:
        def_path = os.path.join(object_path, 'definitions', model_definition)
        def_path = def_path.split('/')
        file, pathname, description = imp.find_module(model_definition, def_path)
    except ImportError as err:
        print("unable to find module " + model_definition)


    try:
        md = imp.load_module(model_definition, file, pathname, description)
    except ImportError:
        print("unable to load module " + model_definition)

    _model = md.construct_model()

    # compiling the model with specified parameters
    _model.compile(
        loss=md.loss,
        optimizer=md.optimizer,
        metrics=md.metrics,
    )

    # give final summary of model layers and variables
    _model.summary()

    return _model


# parse input arguments
args = parser.parse_args()
model_definition = args.model_definition
model_name = args.model_name

# create the specified model
compiled_model = create_model(model_definition)

# save created model
save_path = os.path.join(object_path, 'saves', model_name)
print(save_path)
compiled_model.save(save_path + '.h5')  # requires h5py package
