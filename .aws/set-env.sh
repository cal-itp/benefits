#!/usr/bin/env bash
set -eu

task_file=$1

# make replacements using env vars

sed -i "s/<aws_account>/$AWS_ACCOUNT/g" $task_file
sed -i "s/<aws_bucket>/$AWS_BUCKET/g" $task_file
sed -i "s/<aws_region>/$AWS_REGION/g" $task_file
