# Setting up the cms server

This is a short Guide on how to Install the CMS Version on a Debian Server. As long as there is nothing specified, do run all the commands as root. 

## Prepartion of the server

Install Postgres:

<code>sudo apt-get install postgresql-13</code>

Install missing packages on the server:

<code>apt update</code>

<code>apt full-upgrade</code>

This includes the dist-upgrade

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
Within the package of pycrypto you have to correct all occurences of time.clock() to time.time()


## Create Admin user
<code>cmsAddAdmin username</code>

The password for the user will be shown in the commandline. 
Use this for later login. 


## Starting all the services in Headless Mode

<code>nohup cmsAdminWebServer &</code>

<code>nohup cmsResourceService -a XXX" &</code>

<code>nohup cmsLogService &</code>

Replace XXX with the row number of the contest you want to run. The cmsResourceService will automatically start the cmsContestWebServer. 


## Redeploying a newer Version. 
We can redeploy a new Version of CMS with or without deleting all the Contests, Submissions etc in the database. 

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
<code>nohup cmsAdminWebServer &</code>

<code>nohup cmsResourceService -a XXX" &</code>

<code>nohup cmsLogService &</code>

Replace XXX with the row number of the contest you want to run. The cmsResourceService will automatically start the cmsContestWebServer. 