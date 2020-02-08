#!/usr/bin/env bash

mkdir -p dist
rm -rf dist/package.zip
(
  # shellcheck disable=SC2164
  cd src/lambda/splitter/
  zip -r ../../../dist/package.zip .
)
aws lambda update-function-code --function-name test-hashcat-keyspace --zip-file fileb://dist/package.zip

