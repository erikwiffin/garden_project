#!/usr/bin/env bash
export SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite

python3 -m poetry run flask run --host=10.0.0.145
