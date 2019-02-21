Deployment
==========

Install Google Clould SDK
-------------------------

See the `quickstart <https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu>`_

.. code-block:: sh

    # Create environment variable for correct distribution
    export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"

    # Add the Cloud SDK distribution URI as a package source
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

    # Import the Google Cloud Platform public key
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

    # Update the package list and install the Cloud SDK
    sudo apt-get update && sudo apt-get install google-cloud-sdk

Configure Google Cloud SDK
--------------------------
Type in terminal:

.. code-block:: sh

    gcloud init

Copy the link from terminal to your browser. Authorise Google Could SDK.

- Pick cloud project to use: 3 (gothic-depth-160720)
- Which Google Compute Engine zone would you like to use as project
  default?: [14] europe-west4-a

Install Kubernetes
------------------

.. code-block:: sh

    sudo apt-get install kubectl

Docker
------

docker and docker-compose
~~~~~~~~~~~~~~~~~~~~~~~~~
Install docker and docker-compose:

.. code-block:: sh

    sudo sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
    sudo sh -c "echo deb http://get.docker.io/ubuntu docker main\ > /etc/apt/sources.list.d/docker.list"
    sudo aptitude update
    sudo aptitude install lxc-docker

Run compose (ensure you have at least 20Gb free space before you start):

.. code-block:: sh

    docker-compose build django

Run all containers:

.. code-block:: sh

    docker-compose up -d

Start the docker terminal for django docker image:

.. code-block:: sh

    docker exec -ti muses_django_1 bash

Create/migrate database:

.. code-block:: sh

    python3 ./implementation/server/manage.py migrate

Rebuild index:

.. code-block:: sh

    python3 ./implementation/server/manage.py search_index --rebuild

Common commands
---------------

**Configure Kubernettes**

.. code-block:: sh

    gcloud auth login [your-email]
    gcloud config set project gothic-depth-160720
    gcloud config set compute/zone europe-west1-c
    kubectl get pod

**Shell**

.. code-block:: sh

    kubectl exec -ti muses -c django bash

**Start server**

.. code-block:: sh

    kubectl ???

Further
-------

Current host/load-balancer: 35.205.49.44:80

The setup runs on GCP (Google Cloud Platform).

Requirements for deployment:

- https://docs.docker.com/install/
- https://docs.docker.com/compose/install/
- https://cloud.google.com/sdk/

Read to understand authentication and zone setup:

- https://cloud.google.com/kubernetes-engine/docs/quickstart

Current GCP settings:

.. code-block:: text

    PROJECT_ID: gothic-depth-160720
    ZONE: europe-west1-c

    Cluster: aincient-cluster-1

Building images
---------------
Perform the following steps:

(1) Build the image
~~~~~~~~~~~~~~~~~~~
Build the image using `docker-compose build`:

.. code-block:: sh

    docker-compose build [django/frontend/postgres/elasticapi/nginx]

For frontend:

.. code-block:: sh

    docker-compose build frontend

For backend:

.. code-block:: sh

    docker-compose build django

(2) Tag image with version number you want to push/deploy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tag the image with version number you want to push/deploy. See `muses-pod.yaml`
for current deployed version.

For frontend:

.. code-block:: sh

    docker tag eu.gcr.io/gothic-depth-160720/muses-frontend-app eu.gcr.io/gothic-depth-160720/muses-frontend-app:v5

For backend:

.. code-block:: sh

    docker tag eu.gcr.io/gothic-depth-160720/muses-backend-app eu.gcr.io/gothic-depth-160720/muses-backend-app:v5

(3) Push container into google registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For frontend:

.. code-block:: sh

    gcloud docker -- push eu.gcr.io/gothic-depth-160720/muses-frontend-app:v5

For backend:

.. code-block:: sh

    gcloud docker -- push eu.gcr.io/gothic-depth-160720/muses-backend-app:v5

Deploying containers to the cluster
-----------------------------------
Steps
~~~~~
Perform the following steps:

(1) Go to `console.cloud.google.com <https://console.cloud.google.com/>`__

(2) Go to the ``Kubernetess engine``.

(3) Go to ``Workloads``.

(4) Open ``staging`` or ``production`` workflow.

(5) Click on ``Actions``.

(6) Click on ``Rolling updates``.

(7) Change version of container you want to update.

Direct link
~~~~~~~~~~~
https://console.cloud.google.com/kubernetes/pod/europe-west1-c/aincient-cluster-1
and update POD configuration (press ``Edit``).

.. note::

    Updates are not instant. It's recommended to check online interface for
    status.

Checking status
---------------

Web interface
~~~~~~~~~~~~~
.. code-block:: text

    https://console.cloud.google.com/kubernetes/workload?project=gothic-depth-160720&workload_list_tablesize=50

Command line
~~~~~~~~~~~~
See `useful kubectl commands
<https://kubernetes.io/docs/reference/kubectl/cheatsheet/>`_.

.. code-block:: sh

    kubectl get pod
    kubectl get pods --all-namespaces

    kubectl exec -ti muses -c django bash

    # To attach to a running container:
    kubectl exec -ti muses\-backend -c frontend /bin/sh

    gcloud container clusters get-credentials aincient-production-1 --zone europe-west1-c --project gothic-depth-160720
    kubectl -ti exec muses-production-6f8794476-9cmfb -c muses-backend-app /bin/bash

    kubectl get pods
    kubectl -ti exec muses-staging-1-fd8967664-bbl4p -c muses-backend-app /bin/bash
