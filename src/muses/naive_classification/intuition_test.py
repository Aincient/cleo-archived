# Some functions to get a feeling if the image classification does what it should do
# Only for testing

import os
import numpy as np
from muses.search_index.documents import CollectionItemDocument
from muses.exporters.naive.muses_exporter_plugin import NaiveExporter
from muses.naive_classification.definitions import classes
from muses.naive_classification.helpers import predict_image_path_dict, predict_items
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from django.conf import settings
from PIL import Image

item_top_list = []

model_path = settings.PROJECT_DIR(
                    os.path.join(
                        '..', '..', '..',
                        'src',
                        'muses',
                        'naive_classification',
                        'models',
                        'vgg_met_classes_6_trained.h5'
                    )
                )

# Folder to store image results
# Change for your needs
imout = '/home/thomas/Documents/classified_images/'


def test_model(path=model_path, num_examples=10, model_type='vgg'):
    """Classify random items and document the outcome

    :param num_examples: number of items you want to classify
    :param path: path to the pre-trained model
    :param model_type: type of model that will be loaded
    :type num_examples: int
    :type path: str
    :return:
    """
    for idx, item in enumerate(CollectionItemDocument.search().scan()):
        prediction = predict_items(item, path)
        prediction_text = ""
        for p in list(prediction)[:2]:
            prediction_text += "{}: {} \n".format(p.key(), prediction[p.key()])
        image = item.images[0]
        img = mpimg.imread(image)
        imgplot = plt.imshow(img)
        plt.title("{}".format(prediction_text), fontsize=8)
        plt.savefig('{}prediction-{}.png'.format(imout, idx))
        plt.close()
        if idx > num_examples:
            break


def show_classes(num):
    """Get "num" random images from the exporter and show their class

    :param num: number of images you want to classify
    :return:
    """
    n = NaiveExporter()
    images = n.do_export()
    for i in range(num):
        im_path, category = images[np.random.randint(0, len(images))]
        img = mpimg.imread(im_path)
        plt.title(classes[category])
        plt.savefig('{}{}.png'.format(imout, i))
        plt.close()


def show_category(num, categories):
    """Get 'num' examples of images from a certain category

    :param num:
    :param categories:
    :return:
    """
    n = NaiveExporter()
    images = n.do_export()
    if not isinstance(categories, (list, tuple)):
        categories = [categories]
    for category in categories:
        category_name = classes[category]
        for i in range(num):
            im_path, im_category = images[np.random.randint(0, len(images))]
            while im_category != category:
                im_path, im_category = images[np.random.randint(0, len(images))]
            img = mpimg.imread(im_path)
            imgplot = plt.imshow(img)
            plt.title(im_path)
            plt.savefig('{}{}{}.png'.format(imout, category_name, i))
            plt.close()


def get_all_predictions(top):
    predictions = []
    total = []
    idx = 0
    if len(item_top_list) > 1:
        for idx, item in enumerate(item_top_list):
            print(idx)
            score = sum([1 / (top.index(i) + 1) for i, j in zip(top, item['item_top']) if i == j])
            total.append({'images': item['images'], 'score': score})
            if score > 2:
                predictions.append({'images': item['images'], 'score': score})
                if len(predictions) > 10:
                    predictions.sort(key=lambda x: x['score'], reverse=True)
                    return predictions
        total.sort(key=lambda x: x['score'], reverse=True)
        return total[:10]

    for item in CollectionItemDocument.search().scan():
        print('Step {}, found {} results'.format(idx, len(predictions)))
        idx += 1
        if idx > 10000:
            total.sort(key=lambda x: x['score'], reverse=True)
            return total[:10]
        prediction = predict_items(item, model_path)
        if prediction is not None:
            item_top = list(prediction)[0:3]
            item_top_list.append({'images': item.images, 'item_top': item_top})
            score = sum([1/(top.index(i)+1) for i, j in zip(top, item_top) if i == j])
            total.append({'images': item.images, 'score': score})


def find_similar(img_path, name):
    """From 6000 collection items, find the top ten most similar items
    to an image

    :param img_path: path to the image
    :param name: name of the subfolder where results should be saved
    :return:
    """
    original_prediction = predict_image_path_dict(
        img_path,
        model_path
    )
    top = list(original_prediction)[0:3]
    top_scorers = get_all_predictions(top)
    folder = '{}{}/'.format(imout, name)
    for idx, item in enumerate(top_scorers):
        for im_idx, im_path in enumerate(item['images']):
            img = mpimg.imread(im_path)
            imgplot = plt.imshow(img)
            plt.title('Number {}\nScore: {}'.format(idx, item['score']))
            plt.savefig('{}{}-{}.png'.format(folder, idx, im_idx))
            plt.close()
    img = mpimg.imread(img_path)
    imgplot = plt.imshow(img)
    plt.savefig('{}original.png'.format(folder))
    plt.close()
    return top_scorers
