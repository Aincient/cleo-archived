=====
CLEO
=====
The codebase of CLEO

.. note::

    This is the closed-source doc. For the open-source doc, see the
    ``README_OS.rst`` file. Do not put any sensitive information there.

Prerequisites
=============

- Postgres, postgis.
- Python >=2.7, >=3.5
- Redis
- Elasticsearch 5.x

Installation
============

Additional Python 3.6 dependencies
----------------------------------
tkinter
~~~~~~~
On Python 3.6 you will need to install the ``python3.6-tk`` package for
``tkinter`` support.

.. code-block:: sh

    sudo apt-get install python3.6-tk

NodeJS
------

Install NodeJS:

.. code-block:: sh

    https://nodejs.org/en/download/

Then run:

.. code-block:: sh

    yarn install

Postgis
-------

.. code-block:: sh

    sudo apt-get install libgdal-dev

    sudo su -l postgres

    createdb -T template0 -E utf-8 -l en_US.UTF-8 -O postgres muses

    psql  -c 'create extension postgis;' -d muses

    ./manage.py migrate

Database engine shall be `django.contrib.gis.db.backends.postgis`.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'muses',
            'USER': 'whoever',
            'PASSWORD': 'whatever',
        }
    }

Redis
-----
**Install**

.. code-block:: sh

    sudo apt install redis-server

**Allow connections**

- Edit the redis conf file ``sudo nano  /etc/redis/redis.conf`` file.
- Find line ``bind 127.0.0.1`` and change it to ``bind 0.0.0.0``
- Save the redis.conf file.

**Restart**

.. code-block:: sh

    sudo systemctl restart redis

or

.. code-block:: sh

    /etc/init.d/redis-server restart

**Test**

.. code-block:: sh

    redis-cli ping

The expected output is ``PONG``.

Elasticsearch
-------------
Either install it or run with Docker.

.. code-block:: sh

    docker pull docker.elastic.co/elasticsearch/elasticsearch:5.5.3
    docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:5.5.3

Data
----

Import cities and countries:

.. code-block:: sh

    ./manage.py cities --import=country
    ./manage.py cities --import=city

Docker
------
Application can be run full or partially using docker

For running ES and Postgres in docker containers:

.. code-block:: text

    Available services:
    - elasticsearch
    - postgres
    - django
    - frontend
    - nginx

.. code-block:: sh

    docker-compose up -d postgres elasticsearch

.. code-block:: text

    both services will be available on localhost:[PORT]
    ES: 9200
    Postgres: 5432

    Check docker-compose.yml for detail configuration/volumes/linking

For running full application:

.. code-block:: sh

    docker-compose up -d

.. code-block:: text

    Application will be available on localhost:8000

Using `tensorflow` on GPU
-------------------------
Machine learning can be a very memory intensive process. Especially when
training with larger datasets, it can be very slow, and some machines might
even run out of internal memory.

That's why it's better to run this process on a good GPU. These following steps
will explain how to set up `tensorflow-gpu` with an NVidia graphics card.

First off, if you currently have `tensorflow` installed, you need to uninstall
`tensorflow`, `tensorboard` and `tensorflow-tensorboard` with `pip`. Then,
you have to install `tensorflow-gpu` (version 1.8.0 seems to work fine).

.. code-block:: sh

    pip uninstall tensorflow
    pip uninstall tensorflow-tensorboard
    pip uninstall tensorboard
    pip install tensorflow-gpu

After you have installed `tensorflow-gpu`, you need to follow the steps from
`NVidia guide
<https://www.nvidia.com/en-us/data-center/gpu-accelerated-applications/tensorflow/>`_.

There are a few things you need to do differently:

- You can install the latest NVidia drivers (I use 396, but later ones might
  work as well), but you need to make sure that you install CUDA version 9.0,
  and the accompanying version of cuDNN.
- When using Ubuntu versions higher than 17.x, you need to install CUDA using
  the runfile. If you do that, make sure that the installer does not install
  NVidia drivers. Navigate to where you've saved the run file and do:
- After the last step, you need to restart your computer.

.. code-block:: sh

    sudo chmod +x cuda_9.0.176_384.81_linux.run
    ./cuda_9.0.176_384.81_linux.run --override

Where you have to replace ``cuda_9.0.176_384.81_linux.run`` with the name of
your runfile.

After you have followed the NVidia guide, you have to
symlink /usr/local/cuda to /usr/local/cuda-9.0.

This will make sure that `tensorflow` uses the right version of CUDA:

.. code-block:: sh

    ln -s /usr/local/cuda-9.0 /usr/local/cuda.

Your `tensorflow` operations should now run on GPU.

First, export data:

.. code-block:: sh

    ./manage.py muses_export_classification_data --exporter=naive

Set up a new model:

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier
    c = setup_classifier((128, 128))

As a result, you should see a message that ends with something like:

.. code-block:: text

    Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:0
    with 3181 MB memory) -> physical GPU (device: 0, name: GeForce GTX 1050,
    pci bus id: 0000:01:00.0, compute capability: 6.1)

Usage
=====
Logical break-down (order is important):

(1) Import data using `muses_import` command.
(2) Copy original data using `muses_copy_from_original` command.
(3a) Translate data using `muses_translate` command.
(3b) Fix wrong translations using `muses_fix_wrong_translations` command.
(4) Fetch geo-locations using `muses_fetch_geo_coordinates` command.
(5) Download images using `muses_download_images` command.
(6) Find periods using `muses_find_periods` command.
(7) Classify images using `muses_classify` command.
(8) Sync Elasticsearch indexes.

(1) Importing data from known sources
-------------------------------------
.. note::

    As we import data from various sources, our data is not yet ready to be
    indexed. Normally, each time database is updated, our search indexes
    would be updated too. However, in certain circumstances we shall postpone
    updating of indexes until we have the database ready. For that, we
    shall execute the scripts one after another with
    ``--settings=settings.dev_no_indexing`` option (or
    ``--settings=settings.stg_no_indexing`` for staging).

At the moment, data is imported from the following data sources:

- www.rmo.nl
- brooklynmuseum.org
- thewalters.org
- metmuseum.org

Importing data
~~~~~~~~~~~~~~

Since importing from API can take a long time (and we don't want to have
either latencies or too many requests), we keep requests in JSON cache (located
in the `implementation/import/`. Some JSON dumps of what we have fetched so far
are located in the `implementation/initial`. When starting up locally or
on a new server, make sure to copy entire `implementation/initial` to
`implementation/import` and only then run `muses_import` command (with
`--refetch` directives set to 0.

RMO
^^^

To import data from www.rmo.nl API, run the following command:

.. code-block:: sh

    ./manage.py muses_import --importer rmo_nl --settings=settings.dev_no_indexing

Brooklyn
^^^^^^^^
To import data from www.brooklynmuseum.org API, run the following command:

.. code-block:: sh

    ./manage.py muses_import --importer brooklynmuseum_org --refetch-objects 1 --refetch-images 0 --refetch-geo 0 --settings=settings.dev_no_indexing

When running for the first time, use the following command:

.. code-block:: sh

    ./manage.py muses_import --importer brooklynmuseum_org --refetch-objects 0 --refetch-images 1 --refetch-geo 0 --settings=settings.dev_no_indexing

It's assumed, that you have used the cached version of the objects JSON and Geo.

Walters
^^^^^^^
To import data from www.thewalters.org API, run the following command:

.. code-block:: sh

    ./manage.py muses_import --importer thewalters_org --refetch-objects 0 --refetch-geo 0 --settings=settings.dev_no_indexing

When running for the first time, use the following command:

.. code-block:: sh

    ./manage.py muses_import --importer brooklynmuseum_org --refetch-objects 0 --refetch-images 1 --refetch-geo 0 --settings=settings.dev_no_indexing

It's assumed, that you have used the cached version of the objects JSON and Geo.

Metropolitan
^^^^^^^^^^^^
To import data from www.metmuseum.org API, run the following command:

.. code-block:: sh

    ./manage.py muses_import --importer metmuseum_org --refetch-objects 0 --refetch-images 0 --settings=settings.dev_no_indexing

When running for the first time, use the following command:

.. code-block:: sh

    ./manage.py muses_import --importer metmuseum_org --refetch-objects 0 --refetch-images 1 --refetch-geo 0 --settings=settings.dev_no_indexing

It's assumed, that you have used the cached version of the objects JSON and images.

Updating data
~~~~~~~~~~~~~
When you add new fields to the model and want to populate their values from
existing data (RAW), after you have added the fields and ran migrations, use
`muses_update` command.

- `importer`: ID of the importer.
- `fields`: Comma separated names of the fields (in `Item` model) you want to
  populate.

Note, that after you have ran `muses_update` commands for all 4 collections,
you should repeat `muses_copy_from_original` and `muses_translate`
commands for new fields only.

Brooklyn
^^^^^^^^
.. code-block:: sh

    ./manage.py muses_update \
        --importer=brooklynmuseum_org \
        --fields='accession_date,inscriptions_orig,credit_line_orig,exhibitions' \
        --settings=settings.dev_no_indexing

Walters
^^^^^^^
**Add missing fields**

.. code-block:: sh

    ./manage.py muses_update \
        --importer=thewalters_org \
        --fields='museum_collection_orig,style_orig,culture_orig,inscriptions_orig,credit_line_orig,provenance_orig' \
        --settings=settings.dev_no_indexing

**Update existing fields**

.. code-block:: sh

    ./manage.py muses_update \
        --importer=thewalters_org \
        --fields='geo_location,city_orig' \
        --settings=settings.dev_no_indexing

Metropolitan
^^^^^^^^^^^^
.. code-block:: sh

    ./manage.py muses_update \
        --importer=metmuseum_org \
        --fields='credit_line_orig,region_orig,sub_region_orig,locale_orig,excavation_orig' \
        --settings=settings.dev_no_indexing

Copy and translation commands to run afterwards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Copy missing fields**

.. code-block:: sh

    ./manage.py muses_copy_from_original \
        --target-language=en \
        --copy-fields='inscriptions,credit_line,exhibitions, \
            museum_collection,style,culture,inscriptions,credit_line,provenance, \
            city,credit_line,region,sub_region,locale,excavation' \
        --update-existing \
        --settings=settings.dev_no_indexing

**Translate missing fields**

.. code-block:: sh

    ./manage.py muses_translate \
        --target-language=nl \
        --use-cache \
        --translated-fields='inscriptions,credit_line,exhibitions, \
            museum_collection,style,culture,inscriptions,credit_line,provenance, \
            city,credit_line,region,sub_region,locale,excavation' \
        --update-existing \
        --settings=settings.dev_no_indexing

**Finally**

Perform the following steps again:

- `(3b) Fix wrong translations`_
- `(4) Geo-locations`_
- Rebuild index.

(2) Copying original data
-------------------------
Default fields
~~~~~~~~~~~~~~
**On local dev**

.. code-block:: sh

    ./manage.py muses_copy_from_original --target-language=nl --settings=settings.dev_no_indexing
    ./manage.py muses_copy_from_original --target-language=en --settings=settings.dev_no_indexing

**On staging**

.. code-block:: sh

    ./manage.py muses_copy_from_original --target-language=nl --settings=settings.stg_no_indexing
    ./manage.py muses_copy_from_original --target-language=en --settings=settings.stg_no_indexing

**On production**

.. code-block:: sh

    ./manage.py muses_copy_from_original --target-language=nl --settings=settings.prd_no_indexing
    ./manage.py muses_copy_from_original --target-language=en --settings=settings.prd_no_indexing

Custom fields
~~~~~~~~~~~~~
You can provide a comma-separated list of fields to copy.

.. code-block:: sh

    ./manage.py muses_copy_from_original \
        --target-language=nl \
        --copy-fields=keywords,reign,site_found,acquired,references,dynasty \
        --update-existing \
        --settings=settings.dev_no_indexing

    ./manage.py muses_copy_from_original \
        --target-language=en \
        --copy-fields=keywords,reign,site_found,acquired,references,dynasty \
        --update-existing \
        --settings=settings.dev_no_indexing

(3a) Translations
-----------------

Load latest Thesauri fixture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    ./manage.py loaddata cached_api_calls_thesauritranslation

Default fields
~~~~~~~~~~~~~~
**On local dev**

.. code-block:: sh

    ./manage.py muses_translate --target-language en --use-cache --settings=settings.dev_no_indexing
    ./manage.py muses_translate --target-language nl --use-cache --settings=settings.dev_no_indexing

**On staging**

.. code-block:: sh

    ./manage.py muses_translate --target-language en --use-cache --settings=settings.stg_no_indexing
    ./manage.py muses_translate --target-language nl --use-cache --settings=settings.stg_no_indexing

**On production**

.. code-block:: sh

    ./manage.py muses_translate --target-language en --use-cache --settings=settings.prd_no_indexing
    ./manage.py muses_translate --target-language nl --use-cache --settings=settings.prd_no_indexing

Custom fields
~~~~~~~~~~~~~
You can provide a comma-separated list of fields to translate.

.. code-block:: sh

    ./manage.py muses_translate \
        --target-language=nl \
        --use-cache \
        --translated-fields=keywords,reign,site_found,acquired,references,dynasty \
        --update-existing \
        --settings=settings.dev_no_indexing

    ./manage.py muses_translate \
        --target-language=en \
        --use-cache \
        --translated-fields=keywords,reign,site_found,acquired,references,dynasty \
        --update-existing \
        --settings=settings.dev_no_indexing

(3b) Fix wrong translations
---------------------------

Load latest Translation fix fixture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    ./manage.py loaddata cached_api_calls_translationfix


Run management command to fix faulty translations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**In local dev**

.. code-block:: sh

    ./manage.py muses_fix_wrong_translations --settings=settings.dev_no_indexing

**On staging**

.. code-block:: sh

    ./manage.py muses_fix_wrong_translations --settings=settings.stg_no_indexing

(4) Geo-locations
-----------------
Fetch GEO coordinates
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: sh

    ./manage.py muses_fetch_geo_coordinates --use-cache --settings=settings.dev_no_indexing

Find missing countries
~~~~~~~~~~~~~~~~~~~~~~
There are items that have a known city but an unknown country. Some of those countries can be added by a command

**In local dev**

.. code-block:: sh

    ./manage.py muses_find_missing_countries --settings=settings.dev_no_indexing

**On staging**

.. code-block:: sh

    ./manage.py muses_find_missing_countries --settings=settings.stg_no_indexing

(5) Download images
-------------------
Download all images (except metropolitan)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    ./manage.py muses_download_images --settings=settings.dev_no_indexing

Or for specific importer:

.. code-block:: sh

    ./manage.py muses_download_images --importer=thewalters_org --settings=settings.dev_no_indexing

Download metropolitan images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Some APIs are more strict than others. For metmuseum.org we have to bypass
API protection (which is restricted to browsers only and does not allow
script based data collection by default). Therefore, we need to provide
alternative callback function for downloading the images. We use Firefox
and selenium. You will need to install ``xvfb`` package which is used to
start Firefox in headless mode.

Install xvfb
^^^^^^^^^^^^
.. code-block:: sh

    sudo apt-get install xvfb

Set up Firefox 47
^^^^^^^^^^^^^^^^^
Download and unpack Firefox 47
++++++++++++++++++++++++++++++
**Download**

`From this location
<https://ftp.mozilla.org/pub/firefox/releases/47.0.1/linux-x86_64/en-GB/firefox-47.0.1.tar.bz2>`__
location and unzip it into ``/usr/lib/firefox47/``

.. code-block:: sh

    wget https://ftp.mozilla.org/pub/firefox/releases/47.0.1/linux-x86_64/en-GB/firefox-47.0.1.tar.bz2

**Unpack**

.. code-block:: sh

    tar -xvjf firefox-47.0.1.tar.bz2

Configure
+++++++++
Specify the full path to your Firefox in ``FIREFOX_BIN_PATH``
setting. Example:

   .. code-block:: python

       FIREFOX_BIN_PATH = '/usr/lib/firefox47/firefox'

If you set to use system Firefox, remove or comment-out the
``FIREFOX_BIN_PATH`` setting.

After that your Selenium tests would work.

And finally, run the download images script in headless mode:

.. code-block:: sh

    xvfb-run python manage.py muses_download_images --importer=metmuseum_org --settings=settings.dev_no_indexing --obtain-image-func="muses.firefox_helpers.obtain_image"

Import and export of metropolitan images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Although the download would work locally, it seems to become a problem to
do on the server. Therefore, we need to selectively prepare an archive of
metropolitan images (with relations to the item Object ID/record_number)
upload it to the cloud, download it on the server and run import.

Step 1: Export
^^^^^^^^^^^^^^
Copy all downloaded metmuseum.org images into a single directory and save
a JSON cache file containing links to them locally.

.. code-block:: sh

    ./manage.py muses_export_local_met_images --settings=settings.dev_no_indexing

Step 2: Commit JSON cache
^^^^^^^^^^^^^^^^^^^^^^^^^
You should copy the produced
`implementation/import/metmuseum_org/images/all_met_images.json` file
to the `implementation/initial/metmuseum_org/images/all_met_images.json`
directory and commit.

Step 3: Archive exported files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You should archive entire `implementation/media/export` directory into
`export.zip` file.

Step 4: Upload
^^^^^^^^^^^^^^
Upload the `export.zip` somewhere in the cloud. Since Google Drive is easy
to use and allows us to upload large files, you could use it. Once the
file is uploaded, make a sharable link.

Step 5: Download
^^^^^^^^^^^^^^^^
Download the `export.zip` from the cloud using `scripts/gdown.pl` script.

.. code-block:: sh

    ./scripts/gdown.pl https://drive.google.com/file/a/1A2abAaAabAa-ABabcdefghijkABCDE1A/view?usp=sharing

Step 6: Unpack
^^^^^^^^^^^^^^
Unpack the downloaded `export.zip` file.

.. code-block:: sh

    unzip export.zip

Copy it to the `implementation/media/import/metmuseum_org/` directory.

Step 7: Import
^^^^^^^^^^^^^^

.. note::

    Make sure to run `./manage.py muses_import --importer metmuseum_org --refetch-objects 0 --refetch-images 0`
    command before proceeding further.

On dev:

.. code-block:: sh

    ./manage.py muses_import_local_met_images --settings=settings.dev_no_indexing

On staging/production:

.. code-block:: sh

    ./manage.py muses_import_local_met_images --settings=settings.stg_no_indexing

(6) Periods
-----------
First, load the fixture.

.. code-block:: sh

    ./manage.py loaddata period_tree

Then, find period nodes for collection items.

.. code-block:: sh

    ./manage.py muses_find_periods --settings=settings.dev_no_indexing

.. note::

    To force-update current periods, use ``--update-existing`` option.

.. code-block:: sh

    ./manage.py muses_find_periods --update-existing --settings=settings.dev_no_indexing

(7) Classify
------------
A more extensive explanation of classification and how to train a new model can be found
in `naive_classification/README.rst`. Usually, you should not have to train a new model, and
you only have to crop the images and classify the collection items.

Before running classification, you should generate thumbnails and clean metropolitan images.

**Generate large images**

.. code-block:: sh

    ./manage.py generateimages generator_ids muses_collection:image:image_large


**Clean MET images**

The images from MET have black borders, and sometimes they are an image of a 404 screen. To clean these images, use

.. code-block:: sh

    ./manage.py muses_crop_met_images

Now you're ready to classify.

**Classify**

.. code-block:: sh

    ./manage.py muses_classify --update-existing --settings=settings.dev_no_indexing

Fetching the collection data
----------------------------
Collection data can be fetched using the Django's management interface.

.. code-block:: text

    http://localhost:8000/admin/muses_collection/item/

Clicking the "Syc collection" (top right corner) would start importing
of all collection items from all registered data importers.

Preparing the data-sets
-----------------------
Before we proceed with training of the data, we need to prepare the data-sets.
Before proceeding with this step, make sure you have fetched data the way
described in the `Fetching the collection data`_.

Perform the following steps in order to have it done.

1. Build Elastic index
~~~~~~~~~~~~~~~~~~~~~~
On production or staging do:

.. code-block:: sh

    cd implementation/server
    ./manage.py search_index --rebuild -f

When developing locally, use shortcuts:

.. code-block:: sh

    ./scripts/rebuild_index.sh

2. Prepare images
~~~~~~~~~~~~~~~~~

Convert images to 128x128 PNG format and generate sized images.

.. code-block:: sh

    ./manage.py generateimages generator_ids muses_collection:image:image_ml muses_collection:image:image_sized

3. Export images to CIFAR 10 format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We want to export the images to the CIFAR 10 format, so tensorflow can
deal with them easily

Naive data-set
^^^^^^^^^^^^^^
.. code-block:: sh

    ./manage.py muses_export_classification_data --exporter=naive

For the image classification, we use the naive exporter, which naively
categorizes the data by looking at the title and object type.
Exporting the data can take a lot of time and internal memory.

The dataset is stored in ``muses/implementation/datasets/naive``

All data-sets
^^^^^^^^^^^^^
It is also possible to define other exporters. Running all the exporters
collectively is also possible

.. code-block:: sh

    ./manage.py muses_export_classification_data

Data-sets are stored (relative path from the project root):

- ``muses/implementation/datasets/all``
- ``muses/implementation/datasets/coin``
- ``muses/implementation/datasets/naive``

4. Load the prepared data-sets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is quite similar to ``keras.datasets.cifar10.load_data``. The only
difference is that it returns an extra item (3-rd element of the tuple)
which is the mapping between numerical and textual labels/categories.

It is possible to load a data-set, which can be useful for tests, although it
should usually not be necessary to do so.

To load the data-sets saved in the step
`3. Export images to CIFAR 10 formats for all data-sets`_, do as follows:

.. code-block:: python

    from muses.cifar10_helpers import load_data

    all_data = load_data('/home/user/repos/muses/implementation/datasets/all')
    coin_data = load_data('/home/user/repos/muses/implementation/datasets/coin')

Generating a classifier
-----------------------

To classify the images, we use naive classification, which is based on
the categorization done by the naive exporter. First, you have to
instantiate a classifier and a model

.. code-block:: python
    
    from muses.naive_classification.helpers import setup_classifier
    c = setup_classifier((128, 128))

If you want to load a pre-trained model, you can also use setup_classifier

.. code-block:: python

    from muses.naive_classification.helpers import setup_classifier
    c = setup_classifier(
            (128, 128),
            mode = 'load',
            model_path = '/home/repos/muses/src/muses/naive_classification/models/model_trained.h5',
            model_type = 'vgg'
        )

Model type and model path define the type of model (we usually use VGG19, which is a network
pre-trained on the imagenet dataset) and the path to the model you want to load (usually
located in ``/naive_classification/models/``)

Training the model
------------------

After initializing a classifier and model, you can train them for a
certain number of steps. It automatically takes data from the naive
dataset that was generated when exporting the data.

.. code-block:: python

    num_steps = 50
    c.train_model(num_steps, save=True, model_name='new_model', weighted=True)
    c.plot_performance()

When training the model, you have to beware of overfitting. For a more detailed guide on
training a machine learning model, see the README file in the `naive_classification` folder.

Classification
--------------

You can classify images objects, item object and images from a path.
The functions to do so are all in naive_classification/helpers.py
You can get an ordered dict with the class probabilities for each class,
either for one or multiple images, or one or multiple items.
These functions can take one image/item, or a list of those.

.. code-block:: python

    from muses.naive_classification.helpers import predict_image_path_dict, predict_items
    model_path = '/home/repos/muses/src/muses/naive_classification/models/model_trained.h5'

    # Get the class probabilities for an image
    image_prediction = predict_image_path_dict(image_path, model_path)

    # Get the class probabilities for an item
    item_prediction = predict_items(collection_item, model_path)

CSRF tokens
===========
To obtain a CSRF token make use of `/csrftoken/` endpoint.

**Sample request:**

.. code-block:: text

    POST http://localhost:8000/csrftoken/

**Or with cURL:**

.. code-block:: text

    curl -X POST -i http://localhost:8000/csrftoken/

**Sample response:**

.. code-block:: javascript

    {"token": "bsHtEMn9K8rqWSm1ql5hz5BcBNR3DuFJRgyc6VVE4c0Gh7PzjaEJap9FErsgxkBz"}

Elasticsearch indexes
=====================
Synonyms
--------
There are two lists of synonyms for Elasticsearch:

- English: `implementation/synonyms/raw/en.txt`
- Dutch: `implementation/synonyms/raw/nl.txt`

Both of them are not in format accepted by Elasticsearch. We need to do some
tiny transformation in order to make it acceptable.

Example of the English synonyms:

.. code-block:: text

    word_id;preferred_EN;variant1;variant2;variant3;variant4;variant5;variant6;variant7
    1;Anatolia;anatolia;anatolie;anatolien;;;;
    2;Assyria;assyria;assyrie;assyrien;;;;
    3;Babylonia;babylonia;babylonie;babylonien;;;;
    4;Byblos;;;;;;;
    5;Crocodilopolis;;;;;;;
    6;Greek-Roman;graeco-roman;greco-roman;;;;;
    7;Herodote;herodotos;;;;;;
    8;Horapollo;horapollon;;;;;;
    9;Isis-aphrodite;;;;;;;
    10;Manetho;manethon;manethos;;;;;
    11;Maya;;;;;;;
    12;Nefertiti;nefertete;nofretete;;;;;
    13;Oxyrhynchus;oxyrhynchos;behnasa;el-Bahnasa;bahnasa;;;
    14;pharaoh;pharao;;;;;;
    15;Plutarchus;plutarchos;;;;;;
    16;Punt;;;;;;;
    17;Rosetta;Rosette;el rashid;el-rashid;al-rashid;;;
    18;Saqqara;saqqarah;saqqareh;sakkarah;;;;
    19;Serapeum;serapaeum;serapeion;;;;;
    20;Sinuhe;sinouhe;;;;;;
    21;Taffeh;taffah;taffa;tafa;taphis;;;
    22;Thebes;;;;;;;
    23;Teye;tiy;tiye;;;;;
    24;Wenamun;wen-amon;wenamoen;;;;;

What is made of it:

.. code-block:: text

    anatolia, anatolia, anatolie, anatolien
    assyria, assyria, assyrie, assyrien
    babylonia, babylonia, babylonie, babylonien
    greek-roman, graeco-roman, greco-roman
    herodote, herodotos
    horapollo, horapollon
    manetho, manethon, manethos
    nefertiti, nefertete, nofretete
    oxyrhynchus, oxyrhynchos, behnasa, el-bahnasa, bahnasa
    pharaoh, pharao
    plutarchus, plutarchos
    rosetta, rosette, el rashid, el-rashid, al-rashid
    saqqara, saqqarah, saqqareh, sakkarah
    serapeum, serapaeum, serapeion
    sinuhe, sinouhe
    taffeh, taffah, taffa, tafa, taphis
    teye, tiy, tiye
    wenamun, wen-amon, wenamoen

In detail:

- All one-word lines are being removed
- All words are lower-cased.
- All empty elements are removed.
- First row is removed.
- First element of each row (number) is removed.

.. note::

    Do not commit synonyms files if anyhow the format has been changed (see
    the example of the synonyms file if anything (format, delimiter, etc)
    has been changed.

Geo-coordinates
---------------
If no geo-location could be discovered, the values for latitude and longitude
are set respectively to "-90.0" and "-180.0".

Authentication and registration
===============================
Logging in
----------
In order to log in, you should make a POST request with the following
information to the `/rest-auth/login/` endpoint.

**Sample request:**

.. code-block:: text

    POST http://localhost:8000/rest-auth/login/

.. code-block:: javascript

    {
        "usernname": "admin",
        "password": "test"
    }

**Or if we use cURL:**

.. code-block:: text

    curl -X POST -H 'Content-Type: application/json' -i http://localhost:8000/rest-auth/login/ --data '{
        "username": "admin",
        "email": "",
        "password": "test"
    }'

**Sample response:**

.. code-block:: text

    HTTP 200 OK
    Allow: POST, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "key": "144bae5d5e3f00bef13c92a5d33a327d7bc37f0a"
    }

Logging out
-----------
It's as simple as sending a GET request to the `/rest-auth/logout/` endpoint.

**Sample request:**

.. code-block:: text

    GET http://localhost:8000/rest-auth/logout/

**Sample response:**

.. code-block:: javascript

    {"detail": "Successfully logged out."}

Authenticated user details
--------------------------
It's as simple as sending a GET request to the `/rest-auth/user/` endpoint.

**Sample request:**

.. code-block:: text

    GET http://localhost:8000/rest-auth/user/

**Sample response:**

.. code-block:: javascript

    {
        "pk": 3,
        "username": "admin",
        "email": "admin@localhost",
        "first_name": "Admin",
        "last_name": "Localhost",
        "account_settings": {
            "language": "nl"
        }
    }

Editing the profile
-------------------
It's a POST request to the `/rest-auth/user/` endpoint.

**Sample request:**

.. code-block:: text

    POST http://localhost:8000/rest-auth/user/

.. code-block:: javascript


    {
        "pk": 3,
        "username": "admin",
        "email": "admin2@localhost",
        "first_name": "Admin",
        "last_name": "Localhost",
        "account_settings": {
            "language": "en"
        }
    }

**Sample response:**

.. code-block:: text

    HTTP 200 OK
    Allow: GET, PUT, PATCH, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "pk": 3,
        "username": "admin",
        "email": "admin2@localhost",
        "first_name": "Admin",
        "last_name": "Localhost",
        "account_settings": {
            "language": "en"
        }
    }

Registration
------------
Post request to `/rest-auth/registration/`.

**Sample request:**

.. code-block:: text

    POST http://localhost:8000/rest-auth/registration/

.. code-block:: javascript

    {
        "username": "test4",
        "email": "test4@localhost",
        "password1": "test1234",
        "password2": "test1234"
    }

**Sample response:**

.. code-block:: text

    HTTP 201 Created
    Allow: POST, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "key": "eb7698d526bfa06bbba59cf747ed1c23f78866cd"
    }


Password reset
--------------
For non-authenticated users who forgot their password.

Step 1: Request password reset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Post request to `/rest-auth/password/reset/`. If there's an account
registered with the given e-mail address, a password reset e-mail would be sent
to the latter for the confirmation.

**Sample request:**

.. code-block:: text

    POST http://localhost:8000/rest-auth/password/reset/

.. code-block:: javascript

    {
        "email": "test4@localhost"
    }

**Sample response:**

.. code-block:: text

    HTTP 200 OK
    Allow: POST, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "detail": "Password reset e-mail has been sent."
    }

Step 2: Confirm password reset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sample e-mail contents:

.. code-block:: text

    http://localhost:8000/rest-auth/password/reset/confirm/?uidb64=MjA&token=4xr-6cd6bd1942f9e841a333
    uidb64: MjA
    token: 4xr-6cd6bd1942f9e841a333

Make a POST request to the endpoint specified
`/rest-auth/password/reset/confirm/` providing the following fields:

- `new_password1`: Your new password
- `new_password2`: Repeat your new password
- `uid`: The value of `uid64` you got in a confirmation e-mail.
- `token`: The value of `token` your got in a confirmation e-mail.

**Sample request**

.. code-block:: text

    POST http://localhost:8000/rest-auth/password/reset/confirm/?uidb64=MjA&token=4xr-6cd6bd1942f9e841a333

.. code-block:: javascript

    {
        "new_password1": "newpass",
        "new_password2": "newpass",
        "uid": "MjA",
        "token": "4xr-6cd6bd1942f9e841a333"
    }

**Sample response:**

.. code-block:: text

    HTTP 200 OK
    Allow: POST, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "detail": "Password has been reset with the new password."
    }

Change current password
-----------------------
For authenticated users who desire to change their current password.

Make a POST request to the `/rest-auth/password/change/` endpoint.


**Sample request**

.. code-block:: text

    POST http://localhost:8000/rest-auth/password/change/

.. code-block:: javascript

    {
        "new_password1": "newpass2",
        "new_password2": "newpass2"
    }

**Sample response:**

.. code-block:: text

    HTTP 200 OK
    Allow: POST, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "detail": "New password has been saved."
    }

Favourites
==========
Manage
------
Add
~~~
**Sample request**

.. code-block:: text

    POST http://localhost:8000/account/usercollectionitemfavourites/

.. code-block:: javascript

    {
        "collection_item": 36522
    }

**Sample response**

.. code-block:: text

    HTTP 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Type: application/json
    Location: http://localhost:8000/account/usercollectionitemfavourites/10/
    Vary: Accept

.. code-block:: javascript

    {
        "url": "http://localhost:8000/account/usercollectionitemfavourites/10/",
        "id": 10,
        "user": 3,
        "collection_item": 36522
    }

**Exceptions**

If you try to add the same item to favourites more than once, you will
get the following response:

.. code-block:: text

    HTTP 400 Bad Request
    Allow: GET, POST, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "detail": "You have already added that item as a favourite."
    }

Remove
------
To remove item from favourite, send a DELETE request to the item detail
endpoint `/account/usercollectionitemfavourites/{item-id}/`:

**Sample request**

.. code-block:: text

    DELETE http://localhost:8000/account/usercollectionitemfavourites/1/

**Sample response**

.. code-block:: text

    HTTP 204 No Content
    Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

List
----
Get `/account/usercollectionitemfavourites/show_indexes/`.

**Sample request**

.. code-block:: text

    GET http://localhost:8000/account/usercollectionitemfavourites/show_indexes/

**Sample response**

.. note::

    Note, that ID of the original favourite is stored in ``fav_id`` field.

.. code-block:: javascript

    {
        "count": 4,
        "page_size": 10000,
        "current_page": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 36518,
                "record_number": "1244",
                "inventory_number": "AED 133",
                "api_url": "http://www.rmo.nl/collectie/zoeken?object=AED 133",
                "importer_uid": "rmo_nl",
                "language_code_orig": "nl",
                "department": "Egypte",
                "title_en": [
                    "acting player",
                    "standing"
                ],
                "description_en": [
                    "acting player",
                    "standing"
                ],
                "period_en": [
                    "graeco-roman period",
                    "Roman imperial time"
                ],
                "primary_object_type_en": "votive image",
                "object_type_en": [
                    "votive image"
                ],
                "material_en": [
                    "terracotta"
                ],
                "city_en": " ",
                "country_en": "Egypt",
                "title_nl": [
                    "toneelspeler",
                    "staand"
                ],
                "description_nl": [
                    "toneelspeler",
                    "staand"
                ],
                "period_nl": [
                    "Grieks-Romeinse Periode",
                    "Romeinse keizertijd"
                ],
                "primary_object_type_nl": "votiefbeeld",
                "object_type_nl": [
                    "votiefbeeld"
                ],
                "material_nl": [
                    "terracotta"
                ],
                "city_nl": " ",
                "country_nl": "Egypte",
                "dimensions": "15 cm",
                "object_date_begin": "0",
                "object_date_end": "0",
                "location": {
                    "lat": "26.820553",
                    "lon": "30.802498"
                },
                "images": [
                    "/prj/implementation/media/collection_images_medium/37b1.png"
                ],
                "images_urls": [
                    {
                        "th": "/media/collection_images_medium/57dd.jpg",
                        "lr": "/media/collection_images_medium/09f1.jpg"
                    }
                ],
                "fav_id": 1
            },
            # ...
        ]
    }

Export
------
CSV
~~~
To export all favourites into CSV format, the
`/account/usercollectionitemfavourites/show_indexes/` endpoint is used.

**Sample request**

.. code-block:: text

    GET http://localhost:8000/account/usercollectionitemfavourites/export_all/

Excel
~~~~~
To export all favourites into excel format, the
`/account/usercollectionitemfavourites/show_indexes/` endpoint is used.

**Sample request**

.. code-block:: text

    GET http://localhost:8000/account/usercollectionitemfavourites/export_all/?docformat=xlsx

Invitations
===========
Super-admins might invite users to User Groups.

The `/invitations/send-invites/` endpoint shall be used for the purpose.

We have two fields there:

- User group: User group to which they are invited.
- E-mails: One e-mail per line. As many e-mails as desired, however, keep it
  below 500 at once.

.. code-block:: text

    barseghyan@gw20e.com
    barseghyan@gw30e.com
    barseghyan@gw40e.com
    barseghyan@gw50e.com

If one of the e-mails specified is not valid or already used or already
invited, an error would be shown. Unless the error is fixed, no invitations
will be sent.

Once invitations are sent, e-mails are sent around to the invitees.

Sample e-mail:

.. code-block:: text

    You (barseghyan@gw80e.com) have been invited to join localhost:8000
    If you'd like to join, please go to http://localhost:8000/invitations/accept-invite/safscbdrmeexup2i3cbohtyuydpsktoszayx0lgfysrqbbb6wckilhjnrxlhz41u

Invitees have 3 days to respond to their invitation.

When registering they should use the same e-mail address to which they got
invited.

Upon successful registration, they will be added to the correspondent group
chosen.

Throttling (API usage limits)
=============================
Protected endpoints
-------------------
At the moment, the search endpoint (`/api/collectionitem/`) has usage
limits. Usage limits are based on what type of user API is dealing with.

We have the following user groups defined:

- `super_user`_: 999,999,999 requests per month
- `unlimited_access_user`_: 500,000 requests per month
- `subscribed_user`_: 500,000 requests per month
- `authenticated_user`_: 1,000 requests per month

User can belong to one and only one group. If user technically happens to
belong to multiple groups (for instance, he is a ``super_user`` and
``unlimited_access_user``) the first one (in the order presented above) is
used, having the rest simply ignored.

Usage limits are defined in ``DEFAULT_THROTTLE_RATES`` key of the
``REST_FRAMEWORK`` setting:

.. code-block:: python

    REST_FRAMEWORK = {
        # ...
        'DEFAULT_THROTTLE_RATES': {
            'super_user': '999999999/j',
            'unlimited_access_user': '500000/j',
            'subscribed_user': '500000/j',
            'authenticated_user': '1000/j',
        },
        # ...
    }

User groups
-----------
super_user
~~~~~~~~~~
Active when ``is_superuser`` property of the Django standard
``django.contrib.auth.models.User`` is set to True.

unlimited_access_user
~~~~~~~~~~~~~~~~~~~~~
Active when ``unlimited_access`` property of the
``muses.user_account.models.AccountSettings`` is set to True.

subscribed_user
~~~~~~~~~~~~~~~
Active when user has active subscription (not implemented yet).

authenticated_user
~~~~~~~~~~~~~~~~~~
Active when user is authenticated.

API
---
We have a service endpoint to query current usage and limits for the
authenticated user. Response values are intuitively understandable, but
most-likely, the `num_requests_left` is what matters most.

**Sample request**

.. code-block:: text

    GET http://localhost:8000/account/userapiusage/

**Sample response**

.. code-block:: text

    HTTP 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    {
        "scope": "unlimited_access_user",
        "rate": "3/j",
        "ident": 5,
        "num_requests_limit": 500000,
        "duration_limit": "30 days",
        "current_num_requests": 1000,
        "num_requests_left": 499000
    }

Resetting the user limit counts
-------------------------------
It's possible to reset user limit counts for users with management command
`muses_reset_api_usage_counts`.

It accepts two arguments:

- group (required). Allowed values are equal to the ``DEFAULT_THROTTLE_RATES``
  keys of the ``REST_FRAMEWORK`` settings.
- user (optional): An integer - ID of the user.

In order to reset API usage counts for all groups, call the management
command multiple times.

Reset for entire group
~~~~~~~~~~~~~~~~~~~~~~
**For unlimited_access_user**

.. code-block:: sh

    ./manage.py muses_reset_api_usage_counts --group=unlimited_access_user

**For authenticated_user**

.. code-block:: sh

    ./manage.py muses_reset_api_usage_counts --group=authenticated_user

Reset for a given user within the given group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

    ./manage.py muses_reset_api_usage_counts --group=unlimited_access_user --user=5

Collection search API
=====================
Search API base endpoint is `/api/collectionitem/`.

Internationalisation
--------------------
In order to have Dutch response (error messages, emails) from API,
add ``Accept-Language`` header to the request with value ``nl``.

Curl example:

.. code-block:: text

    curl -X POST -H 'Content-Type: application/json' -H 'Accept-Language: nl' -i http://localhost:8000/rest-auth/registration/ --data '{
        "username": "des15",
        "email": "des15@des.des",
        "password1": "test1234",
        "password2": "test1234"
    }'

Facets
------
Most of the facets are language specific and thus - are disabled by default
(since faceting makes requests heavier). Enable facets upon need by providing
a correspondent facet name as a GET param.

Example (enables `primary_object_type_en` and `material_en` facets):

.. code-block:: text

    http://localhost:3000/api/collectionitem/?facet=primary_object_type_en&facet=material_en

Check the `faceted_search_fields` property of the
`CollectionItemDocumentViewSet` view for complete list of available facets.

Filtering
---------
Check the `filter_fields` property of the
`CollectionItemDocumentViewSet` view for complete list of available filters.

Example (filters by given `primary_object_type_en`):

.. code-block:: text

    http://localhost:3000/api/collectionitem/?primary_object_type_en=coin

Results with empty images
~~~~~~~~~~~~~~~~~~~~~~~~~
For the image search endpoints and backends we only show items that do have
images. It's not so in listing views. If you want to show (in the listing
views) results with images only, add the following to the query params:

.. code-block:: text

    images__isnull=False

Example:

.. code-block:: text

    http://localhost:3000/api/collectionitem/?images__isnull=False

Or:

.. code-block:: text

    http://localhost:8000/api/collectionitem/?images__exists=True

Nested facets
-------------
Most of the facets are language specific and thus - are disabled by default
(since faceting makes requests heavier). Enable facets upon need by providing
a correspondent facet name as a GET param.

Periods
~~~~~~~
Nested facets are enabled for periods. At the moment we have 4 nesting levels.

Example:

.. code-block:: javascript

    "period_1_en": {
        "name": "Graeco-Roman Period",
        "period_2_en": {
            "name": "Roman Period",
            "period_3_en": {
                "name": "Early-Empire",
                "period_4_en": {
                    "name": "Claudius"
                }
            }
        }
    }

To enable the nested facets for English, add ``nested_facet=period_1_en``
to the URL. For Dutch it would be ``nested_facet=period_1_nl``.

**Sample request**

In the example given, we have just one result (otherwise, the list of facets
would be too big for the documentation). If you want to have a bigger list,
follow remove the ``&period_4_en=Claudius`` part from the URL below.

.. code-block:: text

    http://localhost:3000/api/collectionitem/?nested_facet=period_1_en&period_4_en=Claudius

**Sample response**

.. code-block:: javascript

    {
        "count": 1,
        "current_page": 1,
        "facets": {
            "period_1_ens": {
                "doc_count": 1,
                "period_1_en_name": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [
                        {
                            "key": "Graeco-Roman Period",
                            "doc_count": 1,
                            "period_2_ens": {
                                "doc_count": 1,
                                "period_2_en_name": {
                                    "doc_count_error_upper_bound": 0,
                                    "sum_other_doc_count": 0,
                                    "buckets": [
                                        {
                                            "key": "Roman Period",
                                            "doc_count": 1,
                                            "period_3_ens": {
                                                "doc_count": 1,
                                                "period_3_en_name": {
                                                    "doc_count_error_upper_bound": 0,
                                                    "sum_other_doc_count": 0,
                                                    "buckets": [
                                                        {
                                                            "key": "Early-Empire",
                                                            "doc_count": 1,
                                                            "period_4_ens": {
                                                                "doc_count": 1,
                                                                "period_4_en_name": {
                                                                    "doc_count_error_upper_bound": 0,
                                                                    "sum_other_doc_count": 0,
                                                                    "buckets": [
                                                                        {
                                                                            "key": "Claudius",
                                                                            "doc_count": 1
                                                                        }
                                                                    ]
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        },
        "next": null,
        "page_size": 30,
        "previous": null,
        "results": [
            {
                "id": 37034,
                "importer_uid": "rmo_nl",
                "record_number": "114304",
                "inventory_number": "AEM 15",
                "classified_as": [],
                "api_url": "http://www.rmo.nl/collectie/zoeken?object=AEM 15",
                "web_url": null,
                "department": "Egypte",
                "dimensions": "Diam. 19 mm, gew. 3,39 gr",
                "object_date_begin": "41",
                "object_date_end": "42",
                "location": {
                    "lat": "26.820553",
                    "lon": "30.802498"
                },
                "images": [
                    "/path/to/media/collection_images_medium/a31789.png",
                    "/path/to/media/collection_images_medium/221c6f.png"
                ],
                "images_urls": [
                    {
                        "th": "/media/collection_images_medium/030d.jpg",
                        "lr": "/media/collection_images_medium/5d4e.jpg"
                    },
                    {
                        "th": "/media/collection_images_medium/05d4.jpg",
                        "lr": "/media/collection_images_medium/ce2b.jpg"
                    }
                ],
                "title_en": [
                    "coin",
                    "aes-19",
                    "claudius I"
                ],
                "description_en": [
                    "coin",
                    "aes-19",
                    "claudius I Vz: Claudiuskop r.",
                    "TI KLAU KAI [SEBAS GER] M",
                    "Ks: Nike nl",
                    "AUTOKRA",
                    "LB (= year 2)"
                ],
                "period_en": [
                    "graeco-roman period",
                    "Roman imperial times",
                    "claudius 41-42"
                ],
                "period_1_en": {
                    "name": "Graeco-Roman Period",
                    "period_2_en": {
                        "name": "Roman Period",
                        "period_3_en": {
                            "name": "Early-Empire",
                            "period_4_en": {
                                "name": "Claudius"
                            }
                        }
                    }
                },
                "primary_object_type_en": "coin",
                "object_type_en": [
                    "coin",
                    "aes-19",
                    "claudius I"
                ],
                "material_en": [
                    "metal",
                    "copper"
                ],
                "city_en": "_",
                "country_en": "Egypt",
                "title_nl": [
                    "munt",
                    "aes-19",
                    "Claudius I"
                ],
                "description_nl": [
                    "munt",
                    "aes-19",
                    "Claudius I",
                    "Vz: Claudiuskop r.",
                    "TI KLAU KAI [SEBAS GER]M",
                    "Kz: Nike n.l.",
                    "AUTOKRA",
                    "L B (= jaar 2)"
                ],
                "period_nl": [
                    "Grieks-Romeinse Periode",
                    "Romeinse keizertijd",
                    "Claudius 41-42"
                ],
                "primary_object_type_nl": "munt",
                "object_type_nl": [
                    "munt",
                    "aes-19",
                    "Claudius I"
                ],
                "material_nl": [
                    "metaal",
                    "koper"
                ],
                "city_nl": "_",
                "country_nl": "Egypte"
            }
        ],
        # ...
    }

Download single item
--------------------
CSV
~~~
Endpoint: `/api/collectionitem/{object-id}/download/`

**Sample request**

    http://localhost:3000/api/collectionitem/36534/download/

Excel
~~~~~
Endpoint: `/api/collectionitem/{object-id}/download/`

**Sample request**

    http://localhost:3000/api/collectionitem/36534/download/?docformat=xlsx

Find similar items
------------------
By image upload
~~~~~~~~~~~~~~~
Step 1. Uploading an image
^^^^^^^^^^^^^^^^^^^^^^^^^^
We have a endpoint for user uploaded user images, which are used to find
similar items.

**Sample request**

.. code-block:: text

    POST http://localhost:8000/account/usersearchimages/

.. code-block:: javascript

    {
        "image": "base64:sdhfdsfjdskljfds"
    }

**Sample response**

.. code-block:: text

    HTTP 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Type: application/json
    Location: http://localhost:8000/account/usersearchimages/2/
    Vary: Accept

.. code-block:: javascript

    {
        "url": "http://localhost:8000/account/usersearchimages/2/",
        "id": 2,
        "user": 3,
        "image": "http://localhost:8000/media/image1.jpg",
        "created": "2018-06-20",
        "updated": "2018-06-20"
    }

Step 2a. Find similar items
^^^^^^^^^^^^^^^^^^^^^^^^^^^
For finding similar items we have another endpoint
``/account/usersearchimagefindsimilar/{uploaded_image_id}/``.

**Sample request**

.. code-block:: text

    GET http://localhost:8000/account/usersearchimagefindsimilar/1/

**Sample response**

.. code-block:: text

    HTTP 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    HTTP 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
        "classified": [
            [
                "amulet",
                0.5868679881095886
            ],
            [
                "vessel",
                0.17379513382911682
            ],
            [
                "bead",
                0.06809809803962708
            ],
            [
                "statue",
                0.04649878665804863
            ],
            [
                "ring",
                0.033771369606256485
            ]
        ],
        "instance": {
            "url": "http://localhost:8000/account/usersearchimages/7/",
            "id": 7,
            "user": 20,
            "image": "http://localhost:8000/media/ScarabSeal.jpg",
            "created": "2018-06-21",
            "updated": "2018-06-21"
        },
        "count": 200,
        "next": "http://localhost:8000/account/usersearchimagefindsimilar/7/?page=2",
        "previous": null,
        "current_page": 1,
        "page_size": 30,
        "results": [
            {
                "id": 86580,
                "record_number": "33216",
                "inventory_number": "48.1557",
                "api_url": "http://art.thewalters.org/detail/33216",
                "importer_uid": "thewalters_org",
                "language_code_orig": "en",
                "department": " ",
                "title_en": [
                    "Amulet-pendant",
                    "of Taweret"
                ],
                "description_en": [
                    "Taweret"
                    "the Great [Female] One, was represented as a pregnant hippopotamus."
                ],
                "period_en": [
                    "Late Period-early Greco-Roman"
                ],
                "primary_object_type_en": "amulets;pendants",
                "object_type_en": [
                    "amulets;pendants",
                    "figurines"
                ],
                "material_en": [
                    "Egyptian faience with blue-green glaze"
                ],
                "city_en": "Misr",
                "country_en": " ",
                "title_nl": [
                    "amulet-dependant",
                    "of Taweret"
                ],
                "description_nl": [
                    "Taweret"
                    "de 'Grote [vrouwelijke]' werd voorgesteld als een zwanger nijlpaard."
                ],
                "period_nl": [
                    "late periode-ally Greco-Roman"
                ],
                "primary_object_type_nl": "amuletten",
                "object_type_nl": [
                    "amuletten",
                    "hangers",
                    "beeldjes"
                ],
                "material_nl": [
                    "Egyptische faience met blauwgroen glazuur"
                ],
                "city_nl": "Misr",
                "country_nl": " ",
                "dimensions": "H: 2 9/16 x W: 5/16 x D: 3/8 in. (6.54 x 0.87 x 1 cm)",
                "object_date_begin": "-375",
                "object_date_end": "-201",
                "location": {
                    "lat": "27.0",
                    "lon": "30.0"
                }
            },
            # ...
        ]
    }

Step 2b. Find similar items (with facets)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you want to use facets, use the following
`/api/collectionitem/?user_search_image_id={uploaded-image-id}` endpoint.

**Sample request**

.. code-block:: text

    http://localhost:8000/api/collectionitem/?user_search_image_id=23

Response would be similar to `Step 2a. Find similar items`_.

By selecting item(s)
~~~~~~~~~~~~~~~~~~~~
For finding similar items we have the
``/api/collectionitem/find_similar_items/`` endpoint. It expects ids of
items to be matched as an array of ``id`` GET params.

**Sample request**

.. code-block:: text

    GET http://localhost:8000/api/collectionitem/find_similar_items/?id=36527&id=36528

**Sample response**

.. code-block:: text

    HTTP 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

.. code-block:: javascript

    HTTP 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Type: application/json
    Vary: Accept

    {
        "classified": [
            [
                "amulet",
                0.5868679881095886
            ],
            [
                "vessel",
                0.17379513382911682
            ],
            [
                "bead",
                0.06809809803962708
            ],
            [
                "statue",
                0.04649878665804863
            ],
            [
                "ring",
                0.033771369606256485
            ]
        ],
        "instances": [
             {
                "id": 36527,
                "record_number": "125",
                "inventory_number": "AP 58",
                "api_url": "http://www.rmo.nl/collectie/zoeken?object=AP 58",
                "web_url": null,
                "importer_uid": "rmo_nl",
                "language_code_orig": "nl",
                "department": "Egypte",
                "title_en": [
                    "Psemtek",
                    "round arch"
                ],
                "description_en": [
                    "Psemtek",
                    "round arch"
                ],
                "period_en": [
                    "late period",
                    "26th dynasty"
                ],
                "primary_object_type_en": "stela",
                "object_type_en": [
                    "stela"
                ],
                "material_en": [
                    "limestone"
                ],
                "city_en": "_",
                "country_en": "Egypt",
                "title_nl": [
                    "Psemtek",
                    "rondboog"
                ],
                "description_nl": [
                    "Psemtek",
                    "rondboog"
                ],
                "period_nl": [
                    "Late Periode",
                    "26e Dynastie"
                ],
                "primary_object_type_nl": "stèle",
                "object_type_nl": [
                    "stèle"
                ],
                "material_nl": [
                    "kalksteen"
                ],
                "city_nl": "_",
                "country_nl": "Egypte",
                "dimensions": "45 x 29 cm",
                "object_date_begin": "0",
                "object_date_end": "0",
                "location": {
                    "lat": "26.820553",
                    "lon": "30.802498"
                },
                "images": [
                    "/path/to/media/collection_images_medium/5d02723.png",
                    "/path/to/media/collection_images_medium/8ad9163.png",
                    "/path/to/media/collection_images_medium/41cbdfe.png"
                ],
                "images_urls": [
                    {
                        "th": "/media/collection_images_medium/0ca20dba.jpg",
                        "lr": "/media/collection_images_medium/e8295d39.jpg"
                    },
                    {
                        "th": "/media/collection_images_medium/6026ab5c.jpg",
                        "lr": "/media/collection_images_medium/084e0706.jpg"
                    },
                    {
                        "th": "/media/collection_images_medium/75e7776c.jpg",
                        "lr": "/media/collection_images_medium/0b0b8aae.jpg"
                    }
                ],
                "classified_as": []
            },
        ],
        "count": 200,
        "next": "http://localhost:8000/account/usersearchimagefindsimilar/7/?page=2",
        "previous": null,
        "current_page": 1,
        "page_size": 30,
        "results": [
            {
                "id": 86580,
                "record_number": "33216",
                "inventory_number": "48.1557",
                "api_url": "http://art.thewalters.org/detail/33216",
                "importer_uid": "thewalters_org",
                "language_code_orig": "en",
                "department": " ",
                "title_en": [
                    "Amulet-pendant",
                    "of Taweret"
                ],
                "description_en": [
                    "Taweret"
                    "the Great [Female] One, was represented as a pregnant hippopotamus."
                ],
                "period_en": [
                    "Late Period-early Greco-Roman"
                ],
                "primary_object_type_en": "amulets;pendants",
                "object_type_en": [
                    "amulets;pendants",
                    "figurines"
                ],
                "material_en": [
                    "Egyptian faience with blue-green glaze"
                ],
                "city_en": "Misr",
                "country_en": " ",
                "title_nl": [
                    "amulet-dependant",
                    "of Taweret"
                ],
                "description_nl": [
                    "Taweret"
                    "de 'Grote [vrouwelijke]' werd voorgesteld als een zwanger nijlpaard."
                ],
                "period_nl": [
                    "late periode-ally Greco-Roman"
                ],
                "primary_object_type_nl": "amuletten",
                "object_type_nl": [
                    "amuletten",
                    "hangers",
                    "beeldjes"
                ],
                "material_nl": [
                    "Egyptische faience met blauwgroen glazuur"
                ],
                "city_nl": "Misr",
                "country_nl": " ",
                "dimensions": "H: 2 9/16 x W: 5/16 x D: 3/8 in. (6.54 x 0.87 x 1 cm)",
                "object_date_begin": "-375",
                "object_date_end": "-201",
                "location": {
                    "lat": "27.0",
                    "lon": "30.0"
                }
            },
            # ...
        ]
    }

Facets-only API
---------------
For homepage (and other places) where we need to have facets only and
no queries fired, we have a dedicated facets-only API.

.. code-block:: text

    http://localhost:3000/api/collectionitemfacetsonly/

This endpoint is exempted from throttling limits. Use it safely.

Frontend
========

DEV
--------

To run the frontend use the following code

.. code-block:: sh

    yarn start

Go to http://localhost:3000/search/


Production
-------------

To build the production version run the following command

.. code-block:: sh

    yarn build


Testing
=======

Project is covered with tests.

.. code-block:: sh

    ./runtests.py

It's assumed that you have all the requirements installed. If not, first
install the test requirements:

.. code-block:: sh

    pip install -r implementation/requirements/test.txt

Writing documentation
=====================

Keep the following hierarchy.

.. code-block:: text

    =====
    title
    =====

    header
    ======

    sub-header
    ----------

    sub-sub-header
    ~~~~~~~~~~~~~~

    sub-sub-sub-header
    ^^^^^^^^^^^^^^^^^^

    sub-sub-sub-sub-header
    ++++++++++++++++++++++

    sub-sub-sub-sub-sub-header
    **************************

License
=======
Apache 2.0.

Authors
=======
In alphabetical order (first name, last name, email).

- Artur Barseghyan <artur.barseghyan@gmail.com>
- Erick Martijn Bouma <bouma@gw20e.com>
- Haike Zegwaard <zegwaard@gw20e.com>
- Jasper Krebbers <krebbers@gw20e.com>
- Lukas Chripko <chripko@gw20e.com>
- Thomas Derksen <derksen@gw20e.com>
