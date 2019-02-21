Naive classification
--------------------

Image classifier based on naively labeled data.
Data is labeled based on the presence of certain keywords in object title or object type

Usage
-----

Before you can use the classifier to classify new images, you have to either train the model or load an existing model.
Training can be done by using a data generator, that generates data by altering the original images
in a few different ways.
Since we have a relatively small data set, using a data generator prevents overfitting to some degree. It also helps
because we do not have to load all the training data at once.

Before you can train the model, you have to generate a data set using an exporter. For this classifier, we use the naive
exporter.

After training the model or loading an existing model, new images can be classified, which will return a list of
probabilities that indicate how likely it is that the image belongs to the different classes.

Generating a data set
---------------------

Generating a data set can be done with an exporter. In this case, we use the naive exporter. You do have to make sure
that you have followed the right steps to import the collections and generate the images first.

.. code-block:: sh

    ./manage.py muses_export_classification_data --exporter naive

In `/exporters/naive/muses_exporter_plugin.py` you can change parameters of this exporter.
If your machine can't handle the size of the dataset, you can alter the maximum number of images
per class by changing the `max_images` parameter in `do_export()`. This is also a way to combat
data imbalance if your classes are heavily imbalanced.

Definitions
-----------

It is important that you understand what is going on in `naive_classification.definitions.py`. This file contains two
different types of definitions:

Class definitions
^^^^^^^^^^^^^^^^^

`classes` and `synonyms_extended` contain definitions for the classes to use and the words to search for when you
are automatically labeling training data if you are generating a data set. You have to make sure that these definitions
are the same as the ones used in your data set. The classes in `classes` should be the same as in `synonyms_extended`,
and they should be numbered from 0 to the number of classes-1.

Model definitions
^^^^^^^^^^^^^^^^^

There are also definitions for a few different model types. Currently, we use `create_vgg_model()`, which contains
the definitions for a model that uses the VGG19 classifier.

Remember that if you change these definitions, you might not be able to load weights for older pre-trained models!
If you want to do load older models, you have to use the definitions that you used to train those models.

Training the model with a generator
-----------------------------------

To train the model with a generator, you have to follow a few steps. You have to create a new classifier instance, load
the data, prepare the generator and create the initial model. Then, you can start the training for a certain number of
epochs. After that, it is also possible to plot the performance of the model.

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier

    c = setup_classifier((128, 128))
    c.train_model(50, weighted=True, save=True)

There are a few parameters in train_model that are important.

- ``num_epochs``: the number of epochs that the training will run. Running the training for too many epochs usually
results in overfitting. If you see that the accuracy and loss in the validation set are significantly lower
than in the training set, or if your validation accuracy and loss are going down, you are probably overfitting.
It might be worthwhile to train the model a few epochs at a time to see if validation accuracy and loss are still
improving.
- ``save``: set to True if you want to save the model after training. Important if you want to use it again. Models are
stored in `muses/src/muses/naive_classification/models/`
- ``model_name``: the name of the saved model. Models are stored in /naive_classification/models/
- ``weighted``: set to True if you want to use different weights for the different classes. Important if the data is
imbalanced. Weights are determined automatically when loading the data and are stored in c.weights

Plotting the results
--------------------

After you've trained the model, graphs can be made of the accuracy and loss of the training and validation data.
Only the results of the most recent training session are plotted.

.. code-block:: python

    c.plot_performance(filepath)

If no file path is specified, plots are stored in ''muses/src/muses/naive_classification/plots/''

Getting the best training results
---------------------------------

While you could just train the model for a certain number of steps, this is probably not going to give you the optimal
results. To get the best results, you have to first do transfer learning to optimize your classifier,
and then use fine-tuning to fine tune the model. Good explanations of transfer learning and fine-tuning can be found
online (for example, see https://deeplearningsandbox.com/how-to-use-transfer-learning-and-fine-tuning-in-keras-and-tensorflow-to-build-an-image-recognition-94b0b02444f2)

Transfer learning is the act of using a pre-trained model, substituting the top with your own classifier and re-training
that top. To do this, first make sure that all the layers in the VGG part of the model are frozen (and thus can't be
trained), either by setting `trainable` to False (layer.trainable = False) or by freezing the layers of a new model:

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier
    c = setup_classifier((128, 128))
    c.unfreeze_layers(0)
    c.train_model(30, weighted=True, save=True)

After training the model for a sufficient number of epochs (in my case, this was usually somewhere between 25 and 60),
you want to fine tune the model you just trained. To do so, unfreeze a few layers of the VGG model and train the model
again. It might also be wise to set a low learning rate (of about 1e-5):

.. code-block:: python

    c.unfreeze_layers(4)
    c.set_optimizer(lr=0.00005, decay=0)
    c.train_model(30, weighted=True, save=True)

After you have trained and optimized a model, you can start using it by changing `model_path` in the base definitions.

Loading an existing model
-------------------------

Loading an existing model can be done as follows (replace the file path with the path of the model you want to load)

.. code-block:: python

    from muses.naive_classification.muses_cnn import setup_classifier

    filepath = 'muses/src/muses/naive_classification/models/model.h5'
    c = setup_classifier(target_size, mode='load', model_path=filepath)

Once again, when you want to load a model, it is important to know how many layers were trained in that model. If you
fine-tuned the last 4 layers of the VGG model (c.unfreeze_layers(4)), you can only load the weights of that model into
a model with the last 4 layers unfrozen. Either do this in the definitions, or define a new model and unfreeze the last
4 layers:

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier
    c = setup_classifier((128, 128))
    c.unfreeze_layers(4)
    filepath = 'muses/src/muses/naive_classification/models/model.h5'
    c.load_model(filepath)

You can only load a model if the classes of that model are the same as the classes in your definitions file.

Classifying new images
----------------------
Classifying a new image can be done manually:

.. code-block:: python

    from muses.naive_classification.muses_cnn import setup_classifier

    filepath = 'muses/src/muses/naive_classification/models/model.h5'
    c = setup_classifier(target_size, mode='load', model_path=filepath)

    image_path = '/home/thomas/Pictures/image.jpg'
    prediction = c.predict_new(image_path)

Instead of calling predict_new with one file path, you can also use a list of different file paths.
Although classifying images manually can be useful, you probably want to use helper functions.

Helper functions
----------------

'helpers.py' contains a few useful helper functions. The function 'setup_classifier' will set up a new classifier
or load a classifier with a pre-trained model, depending if you use the flag 'train' or 'load'.

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier

    classifier = setup_classifier(
        (128, 128),
        'load',
        '/home/thomas/projects/muses/src/muses/naive_classification/models/test.h5'
    )
    classifier.predict_new(['/home/thomas/Pictures/test.jpg'])

With 'predict_items'  and 'predict_image_path_dict', you can classify an image or an item with a pre-trained classifier.
Both of these functions return ordered dicts with the classes ordered by their probability.
They take a list of Item objects, or a list of image paths.

.. code-block:: python

    from muses.naive_classification.helpers import predict_image_path_dict
    image_path = '/home/thomas/Pictures/image.jpg'
    filepath = 'muses/src/muses/naive_classification/models/model.h5'
    prediction = predict_image_path_dict(
            image_path,
            model_path=filepath
        )

Instead of predicting one item path, you can also predict a list of paths, in which case you will get the average
prediction.
It works the same for predict_items, but you have to use an item or a list of items instead.

Simple use-case
---------------

It is perhaps useful to combine the previous steps into one simple use case, which mentions all the steps you need
to take to train a new model with a naive dataset, the VGG19 model and both transfer learning and finetuning.

1. Export data to dataset
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    ./manage.py muses_export_classification_data --exporter naive

2. Set up and train a classifier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, use transfer learning for a number of epochs, then unfreeze the layers and fine tune for some additional epochs

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier
    image_path = '/home/user/muses/naive_classification/plots/new_model'
    c = setup_classifier((128, 128))
    c.unfreeze_layers(0)
    c.train_model(30, weighted=True, save=True, model_name='new_model')
    c.plot_performance(image_path)
    c.unfreeze_layers(4)
    c.set_optimizer(lr=0.00005, decay=0)
    c.train_model(20, weighted=True, save=True, model_name='new_model_finetuned')
    c.plot_performance('{}_finetuned'.format(image_path))

3. Check for overfitting and add model to setttings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look at the plots to see if validation accuracy decreases (or loss increases) after a certain number of steps.
If so, run the previous steps again, but for a smaller number of epochs.
If you are happy with your model, add its name to the base settings (in
MUSES_CONFIG['classification']['naive_classification']['model_path']). Make sure that the definitions you used to train
the model are the same as your current definitions. In this case, it means that the last 4 layers in create_cgg should
be unfrozen (in create_vgg_model, it should say `for layer in vgg_conv.layers[:-4]:` )

Alternative: using `muses_train_model`
--------------------------------------

Although I highly recommend using the method described above (because it gives you a better feel of what is going on,
and a lot more flexibility), it is also possible to use a management command:

.. code-block:: sh

    ./manage.py muses_train_model --model-name new_model --epochs 50 --plot-performance --fine-tuning

The number of epochs you specify are split into transfer learning and fine-tuning epochs, if you use fine-tuning.
Plots are stored in `naive_classification/plots`

