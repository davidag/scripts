#!/bin/sh

set -ex

# todo: switch to testing
apt update && sudo apt dist-upgrade
apt autoremove

# etckeeper & basic tools
apt install --yes etckeeper git vim sudo

# network manager
apt install --yes network-manager

# i3 window manager
apt install --yes i3 xorg

# xrandr gui frontend
apt install --yes arandr

# firefox stable
apt install --yes libgtk-3-0 libdbus-glib-1-2 libavcodec58

# keepass2
apt install keepass2

# command-line tools
apt install --yes tree unzip curl lsof

