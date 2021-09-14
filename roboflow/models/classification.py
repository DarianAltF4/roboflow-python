import base64
import io
import os
import urllib
import json

import requests
from PIL import Image

from roboflow.util.image_utils import check_image_url
from roboflow.util.prediction import PredictionGroup
from roboflow.config import CLASSIFICATION_MODEL


class ClassificationModel:
    def __init__(self, api_key, id, dataset_slug=None, version=None, local=False):
        """

        :param api_key:
        :param dataset_slug:
        :param version:
        """
        # Instantiate different API URL parameters
        self.api_key = api_key
        self.id=id
        self.dataset_slug = dataset_slug
        self.version = version
        if not local:
            self.base_url = "https://classify.roboflow.com/"
        else:
            self.base_url = "http://localhost:9001/"

        if dataset_slug is not None and version is not None:
            self.__generate_url()

    def predict(self, image_path, hosted=False):
        """

        :param image_path:
        :param hosted:
        :return:
        """
        self.__generate_url()
        self.__exception_check(image_path_check=image_path)
        # If image is local image
        if not hosted:
            # Open Image in RGB Format
            image = Image.open(image_path).convert("RGB")
            # Create buffer
            buffered = io.BytesIO()
            image.save(buffered, quality=90, format="JPEG")
            # Base64 encode image
            img_str = base64.b64encode(buffered.getvalue())
            img_str = img_str.decode("ascii")
            # Post to API and return response
            resp = requests.post(self.api_url, data=img_str, headers={
                "Content-Type": "application/x-www-form-urlencoded"
            })
        else:
            # Create API URL for hosted image (slightly different)
            self.api_url += "&image=" + urllib.parse.quote_plus(image_path)
            # POST to the API
            resp = requests.get(self.api_url)

        if resp.status_code != 200:
            raise Exception(resp.text)

        return PredictionGroup.create_prediction_group(resp.json(),
                                                       image_path=image_path,
                                                       prediction_type=CLASSIFICATION_MODEL)

    def load_model(self, dataset_slug, version):
        """

        :param dataset_slug:
        :param version:
        :return:
        """
        # Load model based on user defined characteristics
        self.dataset_slug = dataset_slug
        self.version = version
        self.__generate_url()

    def __generate_url(self):
        """

        :return:
        """

        # Generates URL based on all parameters
        splitted = self.id.rsplit("/")
        without_workspace = splitted[1]

        self.api_url = "".join([
            self.base_url + without_workspace + '/' + str(self.version),
            "?api_key=" + self.api_key,
            "&name=YOUR_IMAGE.jpg"])

    def __exception_check(self, image_path_check=None):
        """

        :param image_path_check:
        :return:
        """
        # Checks if image exists
        if image_path_check is not None:
            if not os.path.exists(image_path_check) and not check_image_url(image_path_check):
                raise Exception("Image does not exist at " + image_path_check + "!")

    def __str__(self):
        json_value = {'name': self.dataset_slug,
                      'version': self.version,
                      'base_url': self.base_url}

        return json.dumps(json_value, indent=2)
