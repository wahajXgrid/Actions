#!/bin/bash
kubectl scale deployment -n robusta robusta-runner --replicas 0
kubectl scale deployment -n robusta robusta-runner --replicas 1

