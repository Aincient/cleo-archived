from collections import OrderedDict
from muses.naive_classification.definitions import classes, optimizer, loss, metrics
from muses.naive_classification.muses_cnn import MusesClassifier
from muses.search_index.documents.collection_item import CollectionItemDocument
import numpy as np

CLASSIFIERS = {}


def setup_classifier(target_size, mode='train', model_path=None, model_type='vgg', dataset='naive'):
    """Initialize a classifier. With the option 'train', weights are initialized,
    while 'load' loads weights of a pre-trained network

    :param target_size: size of the input data
    :param mode: 'train' for an untrained model, 'load' for a pre-trained model
    :param model_path: in 'load' mode, path to the model that needs to be loaded
    :param model_type: the type of model you want to create or load
    :type target_size: tuple
    :type mode: str
    :type model_path: str
    :return:
    :rtype: MusesClassifier
    """
    if model_path in CLASSIFIERS:
        return CLASSIFIERS[model_path]

    c = MusesClassifier(target_size, dataset=dataset)
    if mode == 'train':
        c.load_data()
        c.prepare_generator()
    c.create_model(model=model_type)
    if mode == 'load':
        if model_path is None:
            print('Define the path to the model that needs to be loaded')
            return None
        else:
            c.load_model(model_path)
    c.model.compile(
            loss=loss,
            optimizer=optimizer,
            metrics=metrics
        )

    CLASSIFIERS[model_path] = c

    return c


def predict_image_paths(image_paths, model_path, target_size=(128, 128)):
    """Use a trained classifier to predict the class probabilities of a list of images
    Returns most likely class and its probability

    :param image_paths: list of path(s) to the image(s)
    :param model_path: path to the pre-trained model
    :param target_size:
    :type image_paths: list
    :return:
    :rtype: list
    """
    c = setup_classifier(target_size, mode='load', model_path=model_path)
    predictions = c.predict_new(image_paths)
    return predictions


def predict_image_path_dict(image_path, model_path, target_size=(128, 128)):
    """Use a trained classifier to predict the class probabilities of a list of images
    Returns ordered dict of classes ordered by their probability

    :param image_path: list of path(s) to the image(s)
    :param model_path: path to the pre-trained model
    :param target_size:
    :type image_path: list
    :return:
    :rtype: OrderedDict
    """
    if not isinstance(image_path, (list, tuple)):
        image_path = [image_path]
    if len(image_path) <= 1:
        prediction = predict_image_paths(image_path, model_path, target_size)[0]
    else:
        prediction = np.mean(predict_image_paths(image_path, model_path, target_size), axis=0)
    named_prediction = {}
    for idx, p in enumerate(prediction):
        named_prediction[classes[str(idx)]] = p

    return OrderedDict(
        sorted(list(named_prediction.items()), key=lambda x: x[1], reverse=True)
    )


def predict_items(items, model_path, target_size=(128, 128)):
    """Use a trained classifier to predict the class probabilities of an item or multiple items
    Returns ordered dict of classes ordered by their probability

    :param items: the item(s) that need to be classified
    :param model_path: path to the pre-trained model
    :param target_size:
    :type items: CollectionItemDocument
    :return:
    :rtype: OrderedDict
    """
    named_prediction = {}
    total = []
    if not isinstance(items, (list, tuple)):
        items = [items]
    for item in items:
        if item.images:
            image_list = list(item.images)
            predictions = predict_image_paths(image_list, model_path, target_size)
            average_prediction = np.mean(predictions, axis=0)
            total.append(average_prediction)

    if total:
        total_average = np.mean(total, axis=0)
        for idx, p in enumerate(total_average):
            named_prediction[classes[str(idx)]] = p
        return OrderedDict(
            sorted(list(named_prediction.items()), key=lambda x: x[1], reverse=True)
        )
