#!/usr/bin/env bash

cd frontend
npm i
npm run build
npm run start

cd ../backend
rm -rf venv*
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
