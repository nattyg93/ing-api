"""Factories for common app."""
import json
import os

dir_name = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_name, "base64_images.json")) as fyle:
    base64_images = json.load(fyle)
