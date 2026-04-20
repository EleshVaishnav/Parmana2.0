#!/bin/bash

echo ""
echo -e "\e[34m  ____   _    ____  __  __    _    _   _    _      ____     ___  \e[0m"
echo -e "\e[34m |  _ \ / \  |  _ \|  \/  |  / \  | \ | |  / \    |___ \   / _ \ \e[0m"
echo -e "\e[34m | |_) / _ \ | |_) | |\/| | / _ \ |  \| | / _ \     __) | | | | |\e[0m"
echo -e "\e[34m |  __/ ___ \|  _ <| |  | |/ ___ \| |\  |/ ___ \   / __/ _| |_| |\e[0m"
echo -e "\e[34m |_| /_/   \_\_| \_\_|  |_/_/   \_\_| \_/_/   \_\ |_____(_)\___/ \e[0m"
echo ""
echo "Bootstrapping Deep Claw 2.0 Installer..."

# If we are running this via one-liner over the web, clone the repo automatically!
if [ ! -f "setup.py" ]; then
    echo -e "\e[33mRemote execution detected. Cloning repository...\e[0m"
    git clone https://github.com/EleshVaishnav/DeepClaw2.0.git
    cd DeepClaw2.0 || exit 1
fi

# Create virtual environment
python3 -m venv .venv

# Activate it and run interactive setup
source .venv/bin/activate
python3 setup.py
