#!/bin/bash

echo "Deploying updates..."

# Go to application directory
cd /var/www/extractor

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Update package list and install prerequisites
sudo apt-get update
sudo apt-get install -y wget curl gnupg2 apt-transport-https ca-certificates

# Remove any existing Chrome repository configuration
sudo rm -f /etc/apt/sources.list.d/google-chrome.list

# Add Google Chrome repository properly
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update package list again after adding new repository
sudo apt-get update

# Install Chrome and additional dependencies
sudo apt-get install -y google-chrome-stable xvfb libxi6 libgconf-2-4

# Verify Chrome installation
if ! command -v google-chrome &> /dev/null; then
    echo "Chrome installation failed. Trying alternative method..."
    # Alternative installation method
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
    rm google-chrome-stable_current_amd64.deb
fi

# Verify Chrome is installed and get version
google-chrome --version || echo "Chrome installation failed"

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