#!/usr/bin/env bash

# Script to get requirements and install Grader

set -e

if [ "$1" = 'grader' ]; then

    # Download CMS (if necessary) and install dependencies
    su admin
    sudo git clone --single-branch --branch it_luca https://github.com/ooemperor/PSEGrader.git || echo "The /code folder isn't empty, skipping git-clone..."
    sudo chmod -R u+rwx,g+rwx,o+rwX /code/PSEGrader
    
    # sudo python3 -m ensurepip
    
    cd /code/PSEGrader/srcCMS
     
     # Correct String to connect to database
    sudo sed 's|postgresql+psycopg2://cmsuser:your_password_here@localhost:5432/cmsdb|postgresql+psycopg2://cmsuser:cmsuser@172.16.238.11:5432/cmsdb|' ./config/cms.conf.sample \
    | sudo tee /usr/local/etc/cms.conf

    sudo python3 -m pip install -r requirements.txt
    
    # Install CMS
    sudo python3 setup.py install
    
    # Replace occurences of time.clock() with time.time
    
    find "/usr/local/lib/python3.9/dist-packages/Crypto/Random/_UserFriendlyRNG.py" -type f -name "*.py" -exec sed -i 's/time\.clock()/time.time()/g' {} +
    
    cmsInitDB 2>&1 >/dev/null || true

    
    # Create "cmsuser" group because apparently CMS needs it
    addgroup --System cmsuser || true

    # Create an admin user in the database (admin / admin)
    cmsAddAdmin admin -p admin || true
    
   if [ ! -d /var/local/cache/cms/ ]; then
    sudo mkdir -p /var/local/cache/cms/
   fi
   
   if [ ! -d /var/local/log/cms/ResourceService-0/ ]; then
    sudo mkdir -p /var/local/log/cms/ResourceService-0/
   fi
   
   # Import some example contest
   
   sudo git clone https://github.com/cms-dev/con_test /cms/con_test || echo "The /con_test folder isn't empty, skipping git-clone..."
   cd /cms/con_test
   cmsImportUser --all || true
   cmsImportContest --import-tasks . || true
   
  sudo cmsResourceService -a ALL

fi


