#!/bin/bash

set -e

pytest --tracing on -v --template=html1/index.html --report=test-results/report.html --video on
