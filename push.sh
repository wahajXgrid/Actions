#!/bin/bash
git add .
git commit -m "updated"
git push

kubectl delete pod -n robusta --all --force

