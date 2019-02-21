import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
from muses.cifar10_helpers import load_data, load_range
from keras import utils, optimizers
from keras.preprocessing.image import ImageDataGenerator
from .definitions import create_naive_model, classes, create_vgg_model, loss, optimizer, metrics, DATASET_DIR, \
    create_xception_model, materials
from sklearn.utils import class_weight
from django.conf import settings

__all__ = (
    'MusesClassifier',
)


class MusesClassifier(object):

    def __init__(self, target_size=(128, 128), weights=None, dataset='naive'):
        """

        :param target_size:
        :param weights:
        :type target_size: tuple
        :type weights: dict
        """
        if dataset == 'naive':
            data_classes = classes
        elif dataset == 'material':
            data_classes = materials

        self.model = None
        self.train_data = None
        self.train_labels = None
        self.test_data = None
        self.test_labels = None
        self.all_data = None
        self.all_labels = None
        self.label_mapping = data_classes
        self.history = None
        self.datagen = None
        self.target_size = target_size
        self.rescale_factor = 255
        self.num_classes = len(data_classes)
        self.weights = weights
        self.dataset_dir = os.path.join(DATASET_DIR, dataset)

    def create_model(self, model='naive'):
        """Create an empty model

        :param model: the model type. Can either be 'naive'  or 'vgg'
        :type model: str
        :return:
        """
        if model == 'naive':
            self.model = create_naive_model(self.target_size, self.num_classes)
        elif model == 'vgg':
            self.model = create_vgg_model(self.target_size, self.num_classes)
        elif model == 'xception':
            self.model = create_xception_model(self.target_size, self.num_classes)
        else:
            raise Exception('Use a valid model name to create a model')

    def compile_model(self):
        """Compile a model

        """
        self.model.compile(
            loss=loss,
            optimizer=optimizer,
            metrics=metrics
        )

    def load_data(self):
        """Load test data from a file and determine class weights

        :return:
        """

        (self.test_data, self.test_labels), self.label_mapping = load_data(
            self.dataset_dir
        )[1:]
        self.num_training = len(load_data(self.dataset_dir)[0][1])
        test_label_list = [i[0] for i in self.test_labels]
        keys = list(self.label_mapping.keys())
        weight_values = class_weight.compute_class_weight('balanced', keys, test_label_list)
        weights = {}
        for idx, key in enumerate(keys):
            weights[int(key)] = weight_values[idx]
        self.weights = weights
        self.num_classes = len(self.label_mapping)
        self.test_labels = utils.to_categorical(self.test_labels, self.num_classes)
        self.test_data = self.test_data.astype('float32')
        self.test_data /= self.rescale_factor

    def custom_generator(self, file_name, batch_size, rescale_factor=255):
        """A custom data generator that goes through the training data in a random order and yields batches of data
        Yields batches indefinitely, and shuffles data after it has been through all of the batches

        :param file_name: file path to the data set
        :param batch_size:
        :param rescale_factor:
        :return:
        """
        while True:
            order = [i * batch_size for i in range(0, int(self.num_training / batch_size))]
            np.random.shuffle(order)
            for i in range(0, int(self.num_training/batch_size)):
                if i >= int(self.num_training/batch_size):
                    i = 0
                    np.random.shuffle(order)
                start = order[i]
                data_range = (start, start + batch_size)
                (train_x, train_y), mapping = load_range(file_name, data_range)
                num_classes = len(mapping)
                train_labels = utils.to_categorical(train_y, num_classes)
                train_data = train_x.astype('float32')
                train_data /= rescale_factor
                train_data, train_labels = next(self.train_datagen.flow(train_data, train_labels, batch_size))

                yield (train_data, train_labels)

    def prepare_generator(self):
        """Prepare data generators
        Should be called before train_datagenerator

        :return:
        """

        if self.test_data is None:
            print('Load the data first')
            return None
        self.train_datagen = ImageDataGenerator(
            featurewise_center=True,
            featurewise_std_normalization=True,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,)
        self.train_datagen.fit(self.test_data)

        val_datagen = ImageDataGenerator(
            featurewise_center=True,
            featurewise_std_normalization=True,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,)
        val_datagen.fit(self.test_data)
        self.val_generator = val_datagen.flow(
            self.test_data,
            self.test_labels,
            batch_size=32,
        )

    def train_model(self, num_epochs, batch_size=32, save=False, model_name='model', weighted=False):
        """Train the model with the data generators

        :param num_epochs: Number of epochs the training will run
        :param batch_size: Size of the batches generated by the data generator
        :param save: True if you want to save the model
        :param model_name: Name of the file to save the model to
        :param weighted: True if you want to use class weights
        :return:
        """

        if weighted:
            class_weight = self.weights
        else:
            class_weight = None

        if self.test_data is not None:
            self.history = self.model.fit_generator(
                self.custom_generator(self.dataset_dir, batch_size),
                validation_data=self.val_generator,
                shuffle=True,
                steps_per_epoch=int(self.num_training / batch_size),
                epochs=num_epochs,
                class_weight=class_weight,
            )
            if save:
                save_path = os.path.join(
                    settings.PROJECT_DIR(
                        os.path.join(
                            '..', '..', '..', 'src', 'muses', 'naive_classification', 'models'
                        )
                    )
                    + '/' + model_name + '_trained'
                )
                self.model.save(save_path + '.h5')
        else:
            print('Prepare the training and test data before you train the model')

    def load_model(self, model_path):
        """Load a model from an .h(df)5 file

        :param model_path: path to the model weights
        :type model_path: str
        :return:
        """
        self.model.load_weights(model_path)

    def predict_new(self, image_paths):
        """Classify a list of images and return the predictions

        :param image_paths: list of paths to image files
        :type image_paths: list
        :return:
        :rtype: list
        """

        img_list = []
        desired_size = self.target_size[0]

        # Resize the image in such a way that aspect ratio stays the same
        for image_path in image_paths:
            im = Image.open(image_path)
            old_size = im.size

            ratio = float(desired_size) / max(old_size)
            new_size = tuple([int(x * ratio) for x in old_size])

            im = im.resize(new_size, Image.ANTIALIAS)

            new_im = Image.new("RGB", (desired_size, desired_size), color='White')
            new_im.paste(im, ((desired_size - new_size[0]) // 2,
                              (desired_size - new_size[1]) // 2))

            img_array = np.asarray(new_im)
            img_array = img_array.astype('float32')
            img_array = (img_array / self.rescale_factor)
            img_list.append(img_array)
        preds = self.model.predict(np.array(img_list))

        return preds

    def plot_performance(self, filepath=None):
        """Plot the performance of a trained model and save the plots
        Should only be done after training a model

        :param filepath: filepath to store the images
        :type filepath: str
        :return:
        """

        if self.history.history:
            if not filepath:
                filepath = settings.PROJECT_DIR(
                    os.path.join(
                        '..', '..', '..', 'src', 'muses', 'naive_classification', 'plots'
                    )
                ) + '/'
            path_loss = '{}loss.png'.format(filepath)
            if 'acc' in self.history.history:
                acc = self.history.history['acc']
                score = 'accuracy'
            elif 'f1' in self.history.history:
                acc = self.history.history['f1']
                score = 'f1'
            else:
                return 'Could not plot performance'

            path_accuracy = '{}{}.png'.format(filepath, score)

            loss = self.history.history['loss']
            epochs = range(1, len(acc) + 1)

            if 'val_acc' in self.history.history:
                val_acc = self.history.history['val_acc']
                plt.plot(epochs, val_acc, 'b', label='Validation acc')
            elif 'val_f1' in self.history.history:
                val_acc = self.history.history['val_f1']
                plt.plot(epochs, val_acc, 'b', label='Validation f1')

            plt.plot(epochs, acc, 'bo', label='Training {}'.format(score))
            plt.title('Training and validation {}'.format(score))
            plt.legend()
            plt.savefig(path_accuracy)
            plt.close()

            plt.figure()
            plt.plot(epochs, loss, 'bo', label='Training loss')

            if 'val_loss' in self.history.history:
                val_loss = self.history.history['val_loss']
                plt.plot(epochs, val_loss, 'b', label='Validation loss')

            plt.title('Training and validation loss')
            plt.legend()
            plt.savefig(path_loss)
            plt.close()

        else:
            print('Nothing to plot')

    def unfreeze_layers(self, number_of_layers):
        """Unfreeze a certain number of layers from the convolutional base

        :param number_of_layers: number of layers to unfreeze
        :return:
        """
        for layer in self.model.layers[0].layers:
            layer.trainable = False
        for idx in range(0, number_of_layers):
            self.model.layers[0].layers[-(idx + 1)].trainable = True

        self.model.compile(
            loss=loss,
            optimizer=optimizer,
            metrics=metrics
        )

    def set_optimizer(self, lr=0.0004, decay=0.000006):
        new_optimizer = optimizers.RMSprop(lr=lr, decay=decay)
        self.model.compile(
            loss=loss,
            optimizer=new_optimizer,
            metrics=metrics
        )
