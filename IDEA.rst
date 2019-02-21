Questions
---------

- How big is the data?

Assumptions/decisions
---------------------
- When searching, we search in both Dutch and English. Facets and results
  returned are only in English.
- Original data is always saved as is. Later on, we go through it and
  fill in the missing data (including translations and geo coordinates).

Features
--------

- Hieroglyph recognition.
- Object detection (detect what kind of objects are pictured, automatically
  classify).
- More like this (similar objects) functionality, based on image search and
  textual search.
- Translate captions to English (for the centralised database). Keep the
  original language stored. Could be done offline with use of
  http://opennmt.net, https://demo-pnmt.systran.net/production#/translation
- Implement collections (RMO would be one of them) as plugins.

What to present
---------------

- Pick an open data set (possibly with images).
- Fetch data locally.
- Make an image search.
- Show for instance what Kibana can do with analyses.
- Show some map overview of articles.
- Perhaps, do something with facets.

Sample request to RMI
---------------------

Search in all fields:

.. code-block:: text

    http://api.rmo.nl:17521/action=get&command=search&query=*egypt*&range=1-1000000&fields=*

Search in all description only:

.. code-block:: text

    http://api.rmo.nl:17521/action=get&command=search&query=Beschrijving=*egypt*&range=1-1000000&fields=*

Search in all title only:

.. code-block:: text

    http://api.rmo.nl:17521/action=get&command=search&query=Titel=*egypt*&range=1-1000000&fields=*

Steps
-----

+ Make a Django app.
+ Make a plugin system for indexing.
+ Make a generalised model for storing the data.
- Use Elasticsearch for indexing.
- Implement image search.
- Implement search (Elastic).
- Add translations (for demo, think of something simple, most likely -
  Google translate for now).
- Add image search (similar images, search by image) (research/implementation).
- See how far can we get with object classification (research/implementation).
