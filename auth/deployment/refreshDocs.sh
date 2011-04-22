#!/bin/bash
pushd docs
rm -Rf _build
make html
popd
mkdir -p auth/public/docs
rm -Rf auth/public/docs/*
cp -R docs/_build/html/* auth/public/docs
