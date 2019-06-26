===========================
Renewal of SSL certificates
===========================


Make sure to have set the right project and compute zone (see DEPLOYMENT.rst).

# Get the active pods

.. code-block:: sh

    kubectl get pods 
    kubectl exec -it <name-of-nginx-pod> -c nginx -- /bin/bash


# Install certbot (does not survive pod restarts):

.. code-block:: sh

    echo "deb http://ftp.debian.org/debian stretch-backports main" > \ 
        /etc/apt/sources.list.d/stretch-backports.list
    apt-get -y update
    apt-get -y install python-certbot-nginx -t stretch-backports


Log in to ISP site: https://ua.siteground.com/login_office.htm
Go to cPanel (red buttons) and choose 'Advanced DNS Zone Editor' for `*.aincient.org`.

# Create new certificates, for `www.cleo.aincient.org`:

.. code-block:: sh

    certbot -d www.cleo.aincient.org -d cleo.aincient.org --email heleen@aincient.org \
        --manual --preferred-challenges dns certonly \
        --server https://acme-v02.api.letsencrypt.org/directory

# Create new certificates, for `*.aincient.org`:

.. code-block:: sh

    certbot -d *.aincient.org --email heleen@aincient.org \
        --manual --preferred-challenges dns certonly \
        --server https://acme-v02.api.letsencrypt.org/directory

Certbot will present a challenge, that needs to be added to the corresponding TXT record.
Wait a few seconds for the DNS to be updated (TTL has been set to 1 already).

Continue the certbot prompt.

The certificate files are placed in a directory that mounted as a persistent volume, so
it will survive container restarts.



