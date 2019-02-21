import json
import os
import uuid
import logging

from bs4 import BeautifulSoup

from django.conf import settings

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from muses.collection.conf import (
    COLLECTION_IMAGES_BASE_PATH,
    COLLECTION_IMAGES_BASE_URL,
)

__all__ = (
    'firefox_get',
    'firefox_download_image',
    'obtain_image',
)

FIREFOX_BIN_PATH = getattr(settings, 'FIREFOX_BIN_PATH', None)
FIREFOX_BINARY = FirefoxBinary(FIREFOX_BIN_PATH)
LOGGER = logging.getLogger(__name__)


def firefox_get(url, raw=False):
    """Get.

    :param url:
    :return:
    """
    # Open a PhantomJS
    driver = webdriver.Firefox(firefox_binary=FIREFOX_BINARY)
    # Get URL
    driver.get(url)
    # Extract the raw HTML
    html_source = driver.page_source
    # Exit PhantomJS
    driver.quit()
    # Make sure PhantomJS is unloaded from memory

    if raw:
        return html_source

    # Get clean JSON
    soup = BeautifulSoup(html_source, "lxml")
    json_source = soup.get_text()

    # Convert to dict
    try:
        dict_data = json.loads(json_source)
    except (TypeError, json.JSONDecodeError):
        return {}
    return dict_data


def firefox_download_image(url, destination_directory):
    """Get.

    :param url:
    :param destination_directory:
    :return:
    """
    # Start virtual display
    display = Display(visible=0, size=(1024, 768))
    display.start()

    # Open a PhantomJS
    driver = webdriver.Firefox(firefox_binary=FIREFOX_BINARY)
    # Get URL
    driver.get(url)
    # Save the image (as PNG), since firefox can save them as png only.
    filename = os.path.join(
        destination_directory,
        "{}.{}".format(str(uuid.uuid4()), 'png')
    )
    driver.save_screenshot(filename)
    LOGGER.info("Saved as {}.".format(filename))
    # Exit browser
    driver.quit()

    # Stop display
    display.stop()

    return filename


def obtain_image(image_source,
                 save_to=COLLECTION_IMAGES_BASE_PATH,
                 media_url=COLLECTION_IMAGES_BASE_URL,
                 force_update=False,
                 expiration_interval=None,
                 debug=False):
    res = firefox_download_image(
        url=image_source,
        destination_directory=save_to
    )
    res = res.replace(settings.MEDIA_ROOT, '')
    if res.startswith('/'):
        res = res[1:]
    return res, None, None
