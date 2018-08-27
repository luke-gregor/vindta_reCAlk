#!/usr/bin/env bash

# remove previous builds and distributions
rm -rf ./dist ./build ./*.egg-info

# create a new distribution after setup has been changed
python "setup.py" -q sdist bdist_wheel

twine upload --repository pypi dist/*

rm -rf ./dist ./build ./*.egg-info
