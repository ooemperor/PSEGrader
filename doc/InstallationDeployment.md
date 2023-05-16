# Installation Guide for PSEGrader

This is a short Guide on how to Install the CMS Version on a Debian Server. As long as there is nothing specified, do run all the commands as root. 

Everyone who uses MobaXterm, please see the paragraph about automation first, to make the installation faster. 

## Preparation of the server

Install Postgres:

<code>sudo apt-get install postgresql-13</code>

Install missing packages on the server:

<code>apt update</code>

<code>apt full-upgrade</code>

This includes the dist-upgrade

Then install the following packages:

<code>sudo apt-get install libcap-dev libcups2-dev libpq-dev python3-dev libcgroup-dev openjdk-17-jdk openjdk-17-jre zip -y</code>

This documentation has been tested and found working correctly under Python 3.9.2

## Getting the repository
Cloning via HTTPs so no ssh key is needed:

<code>git clone https://github.com/ooemperor/PSEGrader.git </code>

Setting the right permissions on the folder:

<code>sudo chmod -R u+rwx,g+rwx,o+rwX /PSEGrader</code>


## Installing CMS
Run the following commands as the postgres user with sudo permission (in sudoer group)

<code>sudo su - postgres</code>

<code> cd /PSEGrader/srcCSM </code>

<code>sudo python3 prerequisites.py install</code>

<code>sudo pip3 install -r requirements.txt</code>


<code>sudo python3 setup.py install</code>

<code>cd /</code>

<code>createuser --username=postgres --pwprompt cmsuser</code>

<code>createdb --username=postgres --owner=cmsuser cmsdb</code>

<code>psql --username=postgres --dbname=cmsdb --command='ALTER SCHEMA public OWNER TO cmsuser'</code>

<code>psql --username=postgres --dbname=cmsdb --command='GRANT SELECT ON pg_largeobject TO cmsuser'</code>

Switch back to root:
<code>exit</code>

Then:
<code>cmsInitDB</code>

Then last:
Within the package of pycrypto you have to correct all occurrences of time.clock() to time.time()


## Create Admin user
<code>cmsAddAdmin username</code>

The password for the user will be shown in the commandline. 
Use this for later login. 


## Starting all the services in Headless Mode
All these commands need to run in Headless mode (nohup) because, if not in headless each of these following commands will block the commandline. 
Further if the command are not run in headless, and the terminal to the server is closed, the services will stop working. 

<code>nohup cmsAdminWebServer &</code>

<code>nohup cmsResourceService -a ALL &</code>

<code>nohup cmsLogService &</code>

The cmsResourceService will automatically start the cmsContestWebServer. 


## Redeploying a newer Version. 
We can redeploy a new Version of CMS with or without deleting all the Contests, Submissions etc. in the database. 

### Deleting all the data
before doing anything run 

<code>cmsDropDB</code>

The rest of the Process is identical to redeploying without data deletion. Except, that at the end before restarting the services you have to run:

<code>cmsInitDB</code>

### Redeploying
Run the following commands as following (as root if not specified other way):

<code>cd / </code>

<code>rm -R /PSEGrader</code>

Cloning via HTTPs so no ssh key is needed:

<code>git clone https://github.com/ooemperor/PSEGrader.git </code>

Setting the right permissions on the folder:

<code>sudo chmod -R u+rwx,g+rwx,o+rwX /PSEGrader</code>

Then:

<code>sudo su - postgres</code>

<code> cd /PSEGrader/srcCSM </code>

<code>sudo python3 prerequisites.py install</code>

<code>sudo pip3 install -r requirements.txt</code>


<code>sudo python3 setup.py install</code>

Switch back to root:

<code>exit</code>

Last start the services:

If the services are already running you can kill them all with the command:
<code>pkill -f cms*</code> and then continue to start the services. 

All these commands need to run in Headless mode (nohup) because, if not in headless each of these following commands will block the commandline. 


<code>nohup cmsAdminWebServer &</code>

<code>nohup cmsResourceService -a ALL &</code>

<code>nohup cmsLogService &</code>

The cmsResourceService will automatically start the cmsContestWebServer. 
All the available Contests are now hosted and online. 

## Automation
For everyone who uses MobaXterm, there is a .mxtmacros file included in this doc folder. You can import this files as macros. 
Included you will find two macros. One is for the deployment with Autostart. This will automatically start up, the AdminWebServer, the ResourceService for all the Contests and the LogService. 
The second macro will just deploy everything. This is the better choice, if you need to create the database first, before starting up.

Before using them, you will need to find the step where the password of the postgres user is entered and change the value. 
The value to replace is `<INSERTYOURPASSWORDHERE>` for both macros. 

PS: Use of the macros on your own risk. 


