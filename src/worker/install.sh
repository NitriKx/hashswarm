#!/usr/bin/env bash


# Install yum dependencies
echo "Installing yum packages..."
yum install -y p7zip jq

# Get current region
REGION=$(curl --silent 'http://169.254.169.254/latest/dynamic/instance-identity/document' | jq -r .region)

# Install hashcat
(
    echo "Installing hashcat 5.1.0..."
    mkdir -p "/opt/hashcat"
    cd "/opt/hashcat"
    wget "https://hashcat.net/files/hashcat-5.1.0.7z"
    7za x "hashcat-5.1.0.7z"
    rm -f "hashcat-5.1.0.7z"
)

# Install the python dependencies
echo "Installing python dependencies..."
pip3 install -r requirements.txt

# Install the services
echo "Installing systemd services..."
cp -f hashswarm.service /etc/systemd/system/
systemctl enable hashswarm
cp -f healthcheck.service /etc/systemd/system/
systemctl enable healthcheck
