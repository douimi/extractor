#!/bin/bash

echo "Deploying updates..."

# Go to application directory
cd /var/www/extractor

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Update package list
sudo apt-get update

# Install Chrome and its dependencies
sudo apt-get install -y wget gnupg2
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories with correct permissions
sudo mkdir -p /var/lib/chrome_data
sudo chown -R www-data:www-data /var/lib/chrome_data
sudo chmod 755 /var/lib/chrome_data

# Create and set permissions for log directory
sudo mkdir -p /var/log/extractor
sudo chown -R www-data:www-data /var/log/extractor
sudo chmod 755 /var/log/extractor

# Copy service file
sudo cp extractor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable extractor
sudo systemctl restart extractor

# Copy and enable Nginx configuration
sudo cp extractor_nginx.conf /etc/nginx/sites-available/extractor
sudo ln -sf /etc/nginx/sites-available/extractor /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "Deployment completed!"

# Check service status
sudo systemctl status extractor 