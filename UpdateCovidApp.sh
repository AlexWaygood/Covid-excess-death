#!/bin/sh
git checkout master
git commit -am "$"
git push origin HEAD:main
gcloud app deploy
read varname