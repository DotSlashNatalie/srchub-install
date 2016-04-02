# Pre-install notes

The installer was created assuming it was a Debian based distro. 
If you are trying to install CentOS or any other distro then some
modifications must be made. Please contact me before running the installer.

The installer will not stop you, but will prompt, if it doesn't detect that
it is a Debian based system.

# Installing srchub

Invoking the installer is pretty simple (run as root):

    apt-get install unzip wget && wget --content-disposition https://srchub.org/p/srchub-install/source/download/master/ && unzip srchub-install-master.zip && chmod +x srchub-install-master/install.sh && srchub-install-master/install.sh
	
# Installation steps

## Start screen

![screen1](https://srchub.org/p/srchub-install/res/raw/17/?attachment=1 "screen1")

## Choose srchub or indefero to install

![screen2](https://srchub.org/p/srchub-install/res/raw/18/?attachment=1 "screen2")

## Install packages

![screen3](https://srchub.org/p/srchub-install/res/raw/19/?attachment=1 "screen3")

## Setup MySQL root password

![screen4](https://srchub.org/p/srchub-install/res/raw/20/?attachment=1 "screen4")

## Confirm MySQL root password

![screen5](https://srchub.org/p/srchub-install/res/raw/21/?attachment=1 "screen5")

## Cron job setup

![screen6](https://srchub.org/p/srchub-install/res/raw/22/?attachment=1 "screen6")

## Setup web links

![screen7](https://srchub.org/p/srchub-install/res/raw/23/?attachment=1 "screen7")

## Last screen

![screen8](https://srchub.org/p/srchub-install/res/raw/24/?attachment=1 "screen8")

## Final steps

### Edit srchub config file

vi /home/www/indefero/src/IDF/conf/idf.php

At around line 31 fill in the following variable:

    $cfg['secret_key'] = '';
	
If your install will be production replace (around line 42):

    $cfg['debug'] = true;
	
with

    $cfg['debug'] = false;
	

Line 105 replace with your *external* domain/IP:

    $cfg['url_base'] = 'http://www.mydomain.com';

Line 109 - replace with the same domain/IP:

    $cfg['url_media'] = 'https://www.mydomain.com/media';
	
Line 113 - again replace with domain/IP:

    $cfg['url_upload'] = 'https://mydomain.com/media/upload';
	
Line 211 - replace:

    $cfg['db_server'] = '';
	
with

    $cfg['db_server'] = '127.0.0.1';
	
You can create a new user (and it is advisable) for MySQL access but it is not necessary to run it.
Replace line 214

    $cfg['db_login'] = 'indefero';
	
with

    $cfg['db_login'] = 'root';
	
(Or the username of the new MySQL user)

Also add in the password of the MySQL user on line 215

After editing the config file cd to the right directory:

    cd /home/www/indefero/src/
	
Then run the following to setup the database

    php /home/www/pluf/src/migrate.php --conf=IDF/conf/idf.php -a -i -d
	
Then finally to create the initial user:

    php /home/www/indefero/scripts/bootstrap.php
	
### Edit Apache

If you have a system that has multiple sites/vhosts on it - then you will need to manually
configure your vhosts. I added some basic Apache snippets to get you started for the
different source code control systems.

However to get you started on a fresh install the following Apache snippet should get you
running with srchub:

	<VirtualHost *:80>
			Include /home/www/indefero/scripts/private_indefero.conf
			ScriptAliasMatch ^/hg(.*) /home/www/indefero/scripts/hgweb.cgi$1
			<Location /hg>
			 Options +ExecCGI
				AuthName "Restricted"
				AuthType Basic
				AuthUserFile /home/mercurial/.htpasswd
				<Limit PUT POST>
					Require valid-user
				</Limit>

			</Location>

			<Directory /home/indefero/scripts>
				Options +ExecCGI
				AuthName "Restricted"
				AuthType Basic
				AuthUserFile /home/mercurial/.htpasswd
				<Limit PUT POST>
					Require valid-user
				</Limit>
			</Directory>
			<Location /svn>
			  DAV svn
			  SVNParentPath /home/svn/repositories
			  AuthzSVNAccessFile /home/svn/dav_svn.authz
			  Satisfy Any
			  Require valid-user
			  AuthType Basic
			  AuthName "Subversion Repository"
			  AuthUserFile /home/svn/dav_svn.passwd
			</Location>
			# The ServerName directive sets the request scheme, hostname and port that
			# the server uses to identify itself. This is used when creating
			# redirection URLs. In the context of virtual hosts, the ServerName
			# specifies what hostname must appear in the request's Host: header to
			# match this virtual host. For the default virtual host (this file) this
			# value is not decisive as it is used as a last resort host regardless.
			# However, you must set it for any further virtual host explicitly.
			#ServerName www.example.com

			ServerAdmin webmaster@localhost
			DocumentRoot /var/www/html

			# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
			# error, crit, alert, emerg.
			# It is also possible to configure the loglevel for particular
			# modules, e.g.
			#LogLevel info ssl:warn

			ErrorLog ${APACHE_LOG_DIR}/error.log
			CustomLog ${APACHE_LOG_DIR}/access.log combined

			# For most configuration files from conf-available/, which are
			# enabled or disabled at a global level, it is possible to
			# include a line for only one particular virtual host. For example the
			# following line enables the CGI configuration for this host only
			# after it has been globally disabled with "a2disconf".
			#Include conf-available/serve-cgi-bin.conf
	</VirtualHost>

	# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
