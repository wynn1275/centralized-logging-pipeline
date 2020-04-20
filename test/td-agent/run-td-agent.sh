#!/bin/bash

HOME_DIR=./

/usr/local/bin/fluentd -c ${HOME_DIR}/td-agent.conf -d ${HOME_DIR}/fluentd.pid
