#!/bin/bash

HOME_DIR=./

kill -2 `cat $HOME_DIR/fluentd.pid`
