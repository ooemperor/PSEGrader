# The following commands are necessary in order to be able to run the install process
on the error that isolate must be run first: berechtigungsproblem:
sudo chmod -R u+rwx,g+rwx,o+rwX /PSEGrader

Install Missing packages. 
sudo apt-get install libcap-dev libcups2-dev libpq-dev python3-dev libcgroup-dev openjdk-17-jdk openjdk-17-jre zip -y


created users on the server at home:
- postgres
- cmsuser
- mkaiser
- root

more notes to be added. 
conf files at the wrong place at the moment. 

update t = time.clock() in pycrpyt files, because not running. 


sudo python3 prerequisites.py install
sudo pip3 install -r requirements.txt
sudo python3 setup.py install


then switch to postgres:
createuser --username=postgres --pwprompt cmsuser
createdb --username=postgres --owner=cmsuser cmsdb
psql --username=postgres --dbname=cmsdb --command='ALTER SCHEMA public OWNER TO cmsuser'
psql --username=postgres --dbname=cmsdb --command='GRANT SELECT ON pg_largeobject TO cmsuser'

cmsInitDB
cmsAddAdmin username
cmsAdminWebServer
cmsContestWebServer
cmsResourceService -a 1 (number of the contest)

nohup cmsAdminWebServer &
nohup cmsResourceService -a 2 &
nohup cmsLogService &

cms/conf.py usecgroup set to False. 


isolate --box-id=10 --cg --cg-timing --chdir=/tmp --dir=/tmp=/tmp/cms-compile-ptx0v8bb/home:rw --dir=/etc/alternatives=/etc/alternatives --dir=/etc=/etc --full-env --env=HOME=/tmp --cg-mem=524288 --stdout=/tmp/compilation_stdout_0.txt --processes=1000 --stderr=/tmp/compilation_stderr_0.txt --time=10 --wall-time=21 --meta=/tmp/cms-compile-ptx0v8bb/run.log.0 --run -- /usr/bin/python3 -m compileall -b .

