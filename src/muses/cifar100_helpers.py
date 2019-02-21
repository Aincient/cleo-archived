import os
import sys
import numpy as np
from array import array
from PIL import Image
from six.moves import cPickle
from keras import backend as K


__all__ = (
    'get_single_cifar100_repr',
    'prepare_images_list_for_cifar100',
    'write_batch',
    'load_batch',
)


def get_single_cifar100_repr(im_path):
    """Get single image representation in CIFAR100 format.

    :param im_path:
    :return:
    """
    pil_im = Image.open(im_path)
    pix_im = pil_im.load()
    x, y = pil_im.size
    im_data = array('B')
    # im = np.array(pil_im)
    # r = im[:, :, 0]  # Slicing to get R data
    # g = im[:, :, 1]  # Slicing to get G data
    # b = im[:, :, 2]  # Slicing to get B data
    # return np.array([[r] + [g] + [b]], np.uint8)
    for color in range(0, 3):
        for x in range(0, x):
            for y in range(0, y):
                im_data.append(pix_im[x, y][color])
    return np.array(list(im_data), np.uint8)


def prepare_images_list_for_cifar100(images_list, text_labels):
    """Prepare images list for CIFAR100.

    :param images_list: List of tuples consisting of the full image path
                        as the first element and list of labels/categories of
                        the image as second argument.
    :param text_labels: Text labels - mapping between numerical and textual
                        representation of the labels/categories.
    :return:
    """
    data = []
    labels = []  # correspondent to `labels` in CIFAR100
    filenames = []  # correspondent to `filenames` in CIFAR100
    for im_path, categories in images_list:
        try:
            single = get_single_cifar100_repr(im_path)
        except (IndexError, IOError) as err:
            continue

        data.append(single)
        # if data is None:
        #     data = single
        # else:
        #     data = np.append(data, single, 0)
        labels.append(categories)
        filenames.append(im_path)

    data = np.array(data, np.uint8)

    # return data, labels, text_labels
    return {
        'batch_label': 'muses',
        'labels': labels,
        'data': data,
        'filenames': filenames,
        'text_labels': text_labels,
    }


def write_batch(images_list, dest_filename, text_labels):
    """Write single batch.

    :param images_list: List of tuples consisting of the full image path
                        as the first element and list of labels/categories of
                        the image as second argument.
    :param dest_filename: Output filename.
    :param text_labels: Text labels - mapping between numerical and textual
                        representation of the labels/categories.
    :return:
    """
    cifar100_data = prepare_images_list_for_cifar100(images_list, text_labels)
    dest = open(dest_filename, 'wb')
    cPickle.dump(cifar100_data, dest)
    dest.close()


def load_batch(file_path):
    """Load batch.

    :param file_path: Path to the batch to load data from.
    :return: Tuple of 3 elements: data,
                                  labels (numerical),
                                  text_labels (mapping between numerical
                                               and textual representation of
                                               the label/category)
    """
    f = open(file_path, 'rb')
    if sys.version_info < (3,):
        d = cPickle.load(f)
    else:
        d = cPickle.load(f, encoding='bytes')
    f.close()
    data = d['data']
    labels = d['labels']
    text_labels = d['text_labels']

    data = data.reshape(data.shape[0], 3, 64, 64)
    return data, labels, text_labels


def load_data(source_dir, num_train_samples=50000):
    """Load data.

    :param source_dir: Full path to directory to read the data from.
    :param num_train_samples:
    :return: Tuple of 3 elements: data,
                                  labels (numerical),
                                  text_labels (mapping between numerical
                                               and textual representation of
                                               the label/category)
    """
    files = [
        os.path.join(source_dir, _file)
        for _file
        in os.listdir(source_dir)
        if os.path.isfile(_file) and _file.startswith('data_batch')
    ]

    # num_train_samples = 50000

    x_train = np.empty((num_train_samples, 3, 64, 64), dtype='uint8')
    y_train = np.empty((num_train_samples,), dtype='uint8')

    for i in range(1, len(files)):
        file_path = os.path.join(source_dir, 'data_batch_' + str(i))
        (x_train[(i - 1) * num_train_samples: i * num_train_samples, :, :, :],
         y_train[(i - 1) * num_train_samples: i * num_train_samples],
         __nothing) = load_batch(file_path)

    file_path = os.path.join(source_dir, 'test_batch')
    x_test, y_test, text_labels = load_batch(file_path)

    y_train = np.reshape(y_train, (len(y_train), 1))
    y_test = np.reshape(y_test, (len(y_test), 1))

    if K.image_data_format() == 'channels_last':
        x_train = x_train.transpose(0, 2, 3, 1)
        x_test = x_test.transpose(0, 2, 3, 1)

    return (x_train, y_train), (x_test, y_test), text_labels
