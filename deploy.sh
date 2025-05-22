#!/bin/bash

echo "Deploying updates..."

# Go to application directory
cd /var/www/extractor

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart extractor
sudo systemctl restart nginx

echo "Deployment completed!"

# Check service status
sudo systemctl status extractor 