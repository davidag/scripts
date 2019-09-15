#!/bin/sh

USER=david

set -ex

# todo: switch to testing
apt update && sudo apt dist-upgrade
apt autoremove

# etckeeper & basic tools
apt install --yes etckeeper git gitk vim sudo

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

# file manager and pdf viewer
apt install xfe xpdf

# command-line tools
apt install --yes tree unzip curl lsof colordiff p7zip unison dnsutils ccd2iso duc

# debian tools
# - debconf-utils: installs debconf-get-selections to automate package installation
apt install debconf-utils
# - apt-file: search files on any package (whether installed or not)
#   The package cache must be updated after installing apt-file
apt install apt-file
apt update

# watson for time logging
apt install watson
wget -O /etc/bash_completion.d/watson https://raw.githubusercontent.com/TailorDev/Watson/master/watson.completion

# vagrant with qemu-kvm
apt install vagrant
apt install qemu-kvm libvirt-daemon-system

adduser $USER libvirt
adduser $USER libvirt-qemu

# sound
apt install pulseaudio pavucontrol

# avoid entering ssh keys on every terminal
apt install keychain

# protonvpn
apt install openvpn dialog wget python
wget -O protonvpn-cli.sh https://raw.githubusercontent.com/ProtonVPN/protonvpn-cli/master/protonvpn-cli.sh
chmod +x protonvpn-cli.sh
./protonvpn-cli.sh --install
rm protonvpn-cli.sh

# general development
apt-get install exuberant-ctags

# php & composer
apt install php php-xml php-gd php-mbstring php-curl
wget -O composer-setup.php https://getcomposer.org/installer
php composer-setup.php --install-dir=/usr/local/bin --filename=composer
rm composer-setup.php

# python3 development
apt-get install python3 python3-venv
