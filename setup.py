import json

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("setup.json", "r") as js:
    setupJSON = json.loads(js.read())
setupJSON["long_description"] = long_description
setupJSON["packages"] = setuptools.find_packages()

setuptools.setup(
    **setupJSON
)