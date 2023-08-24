#!/bin/bash
set -e


pwd

echo $TAG_CANDIDATE_NAME > .version
./build.sh
ls -la ./dist