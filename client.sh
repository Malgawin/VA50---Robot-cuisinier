#!/usr/bin/env bash

ROS_DISTRO=noetic
IMAGE_NAME=epan/kinova:"${ROS_DISTRO}"
USERNAME=ros

CONTAINER_NAME="${IMAGE_NAME//[\/.]/-}"
CONTAINER_NAME="${CONTAINER_NAME/:/-}-ssh"

EXEC_FLAGS=()
EXEC_FLAGS+=(-u "${USERNAME}")
EXEC_FLAGS+=(-e DISPLAY="${DISPLAY}")
EXEC_FLAGS+=(-e XAUTHORITY="${XAUTH}")

docker container exec -it "${EXEC_FLAGS[@]}" "${FWD_ARGS[@]}" "${CONTAINER_NAME}" /bin/bash
