import locale
from dialog import Dialog
from subprocess import call
import sys
import os

# This is almost always a good thing to do at the beginning of your programs.
import subprocess

locale.setlocale(locale.LC_ALL, '')

"""
    @name: srchub-install
    @description: Used to bootstrap a system with srchub or indefero
    @notes: This replaces the Debian package - it seemed like a good idea at the time but didn't really work.
            And this will allow support for other distros
            This script will never work on Windows and unless there is extreme demand for it - one will probably never
            exist.
"""

INDEFERO_BASE_APACHE = """
Include /home/www/indefero/scripts/private_indefero.conf
"""

INDEFERO_HG_APACHE = """
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
"""

INDEFERO_SVN_APACHE = """
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
"""

GIT_DAEMON_CONF = """#!/bin/sh
exec 2>&1
echo 'git-daemon starting.'
exec chpst -ugit:git \
  "$(git --exec-path)"/git-daemon --verbose --base-path=/home/git/repositories /home/git/repositories
"""

HTACCESS = """
Options +FollowSymLinks
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*) /index.php/$1
"""

FINAL_MSG = """
I did NOT modify Apache for you -
In /etc/apache2/sites-available you should find 3 files:
[1] - indefero.base - this is what is needed for private repos
[2] - indefero.svn - this is what is needed for subversion repos
[3] - indefero.hg - this is what is needed for mercurial repos
Add what you want into your virtualhost config
SUBVERSION AND MERCURIAL WILL NOT WORK OTHERWISE!

Please add the following to your sudoers (visudo) file - this grants Apache the ability to reload itself:
www-data ALL=(ALL) NOPASSWD: /etc/init.d/apache2 reload

You will need to edit /home/www/indefero/src/IDF/conf/idf.php and fill in your database information
Then run:
 php /home/www/pluf/src/migrate.php --conf=IDF/conf/idf.php -a -i -d
Then finally to create the user:
 php /home/www/indefero/scripts/bootstrap.php
to create the admin user (username: admin, password: admin)
"""

AUTHBASIC_PATCH = """
--- Authbasic.php       2013-07-23 22:33:50.000000000 -0500
+++ /usr/share/php/File/Passwd/Authbasic.php    2013-06-03 19:07:37.000000000 -0500
@@ -17,7 +17,7 @@
  * @author     Michael Wallner <mike@php.net>
  * @copyright  2003-2005 Michael Wallner
  * @license    http://www.php.net/license/3_0.txt  PHP License 3.0
- * @version    CVS: $Id$
+ * @version    CVS: $Id: Authbasic.php,v 1.17 2005/03/30 18:33:33 mike Exp $
  * @link       http://pear.php.net/package/File_Passwd
  */

@@ -52,7 +52,7 @@
 *
 * @author   Michael Wallner <mike@php.net>
 * @package  File_Passwd
-* @version  $Revision$
+* @version  $Revision: 1.17 $
 * @access   public
 */
 class File_Passwd_Authbasic extends File_Passwd_Common
@@ -79,7 +79,7 @@
     * @var array
     * @access private
     */
-    var $_modes = array('md5' => 'm', 'des' => 'd', 'sha' => 's');
+    var $_modes = array('plain' => 'p', 'md5' => 'm', 'des' => 'd', 'sha' => 's');

     /**
     * Constructor
@@ -298,7 +298,7 @@
         $mode = strToLower($mode);
         if (!isset($this->_modes[$mode])) {
             return PEAR::raiseError(
-                sprintf(FILE_PASSWD_E_INVALID_ENC_MODE_STR, $mode),
+                sprintf(FILE_PASSWD_E_INVALID_ENC_MODE_STR, $this->_mode),
                 FILE_PASSWD_E_INVALID_ENC_MODE
             );
         }
@@ -326,7 +326,9 @@
             return File_Passwd::crypt_des($pass, $salt);
         } elseif ($mode == 'sha') {
             return File_Passwd::crypt_sha($pass, $salt);
-        }
+        } elseif ($mode == 'plain') {
+               return $pass;
+       }

         return PEAR::raiseError(
             sprintf(FILE_PASSWD_E_INVALID_ENC_MODE_STR, $mode),

"""

CRON_JOB_SCRIPT = """
*/5 * * * * /bin/sh /home/www/indefero/scripts/SyncMercurial.sh
15 * * * * /usr/bin/php5 /home/www/indefero/scripts/calculateforgecron.php
0 1 * * * /usr/bin/php5 /home/www/indefero/scripts/activitycron.php
*/5 * * * * /usr/bin/php5 /home/www/indefero/scripts/queuecron.php
"""

d = Dialog(dialog="dialog", autowidgetsize=True)
distro = ""
FNULL = open(os.devnull, 'w')

def exit_msg():
    print "Thank you for using the srchub installer\n"
    print "Please send feedback to adamsna@datanethost.net"

def install_cron_jobs():
    answer = d.yesno("Do you want me to attempt to install the cron jobs?")
    if answer == d.DIALOG_OK:
        d.infobox("Setting up cron jobs...")
        with open('/tmp/cron', 'w') as content_file:
            content_file.write(CRON_JOB_SCRIPT)
        call("crontab -u www-data /tmp/cron".split(" "))
        call(["rm", "/tmp/cron"])

def update_mercurial_hooks():
    hgconf = ""
    d.infobox("Checking for mercurial hooks...")
    with open('/etc/mercurial/hgrc', 'r') as content_file:
        hgconf = content_file.read()
    if "hgchangegroup" not in hgconf:
        hgconf += "\n[hooks]\nchangegroup = /home/www/indefero/scripts/hgchangegroup.php"
    with open('/etc/mercurial/hgrc', 'w') as content_file:
        content_file.write(hgconf)

def setup_git_daemon():
    d.infobox("Setting up git daemon...")
    if not os.path.isfile("/etc/sv/git-daemon/run.srchub"):
        call(["mv", "/etc/sv/git-daemon/run", "/etc/sv/git-daemon/run.srchub"])
        with open('/etc/sv/git-daemon/run', 'w') as content_file:
            content_file.write(GIT_DAEMON_CONF)
    call(["adduser", "git"])

def setup_web_links():
    code, user_input = d.inputbox("I need to setup some web links. Where is your web root? (no leading slash)", init="/var/www/html")
    call(["ln", "-s", "/home/www/indefero/www/index.php", "%s/index.php" % user_input])
    call(["ln", "-s", "/home/www/indefero/www/media", "%s/media" % user_input])
    with open("%s/.htaccess" % user_input, 'w') as content_file:
        content_file.write(HTACCESS)

def install_pear_modules():
    call(["pear", "install", "File_Passwd"], stderr=subprocess.STDOUT, stdout=FNULL)
    call(["pear", "upgrade-all"], stderr=subprocess.STDOUT, stdout=FNULL)
    call(["pear", "install", "--alldeps", "Mail"], stderr=subprocess.STDOUT, stdout=FNULL)
    call(["pear", "install", "--alldeps", "Mail_mime"], stderr=subprocess.STDOUT, stdout=FNULL)

def fix_auth_basic():
    with open('/tmp/patch', 'w') as content_file:
        content_file.write(AUTHBASIC_PATCH)
    call(["patch", "-N", "/usr/share/php/File/Passwd/Authbasic.php", "<", "/tmp/Authbasic.patch"])
    call(["rm /tmp/patch"])

def prep_apache():
    call(["a2enmod", "rewrite"])
    with open('/etc/apache2/sites-available/indefero.base', 'w') as content_file:
        content_file.write(INDEFERO_BASE_APACHE)
    with open('/etc/apache2/sites-available/indefero.hg', 'w') as content_file:
        content_file.write(INDEFERO_HG_APACHE)
    with open('/etc/apache2/sites-available/indefero.svn', 'w') as content_file:
        content_file.write(INDEFERO_SVN_APACHE)

def final_msg():
    os.chdir("/home/www/indefero/src")
    call("mv /home/www/indefero/src/IDF/conf/path.php-dist /home/www/indefero/src/IDF/conf/path.php".split(" "))
    call("mv /home/www/indefero/src/IDF/conf/idf.php-dist /home/www/indefero/src/IDF/conf/idf.php".split(" "))
    d.msgbox(FINAL_MSG)

def install_package(package):
    if distro == "Debian":
        if package == "mariadb-server":
            call(["apt-get", "--assume-yes", "-y", "install", package])
        else:
            call(["apt-get", "--assume-yes", "-y", "install", package], stderr=subprocess.STDOUT, stdout=FNULL)

def install_packages():
    code = d.yesno("Do you want me to attempt to install the needed packages?")
    if code == d.OK:
        d.gauge_start("Installing...")
        packages = ["git", "mercurial", "subversion", "mariadb-client", "libapache2-mod-php5",
                        "php5-curl", "php5-mysql", "php5-cli", "git-daemon-run", "gitweb", "php-pear", "patch", "mariadb-server"]
        percent = 0
        i = 0.0
        for package in packages:
            d.gauge_update(percent, "Installing " + package, update_text=True)
            install_package(package)
            i += 1.0
            percent = int((i / len(packages)) * 100)
        d.gauge_stop()


d.set_background_title("Srchub Installer")

d.msgbox("""This will guide you through installing srchub
Any comments should be directed towards
adamsna@datanethost.net""")

with open('/etc/issue', 'r') as content_file:
    issue_file = content_file.read()

if "Debian" in issue_file or "Ubuntu" in issue_file:
    distro = "Debian"
else:
    code = d.yesno("""This script was designed for Debian/Ubuntu but it seems you are using a different distro.\n
However - you may still attempt to run it if you know what you are doing.\n\n

I recommend canceling and emailing the author and telling them the name of your distro which is:\n """ + issue_file)
    if code == d.CANCEL:
        exit_msg()
        sys.exit()

code, tag = d.menu("Choose carefully:", choices=[
    ("1", "Install srchub"),
    ("2", "Install indefero")
])

if code == d.OK:
    install_packages()
    if tag == "1":  # Install srchub
        call(["git", "clone", "git://srchub.org/srchub-git.git", "/home/www"])

        install_cron_jobs()
        update_mercurial_hooks()
        setup_git_daemon()
        setup_web_links()
        install_pear_modules()
        fix_auth_basic()
        prep_apache()
        final_msg()
        print FINAL_MSG
    else:  # Install indefero vanilla
        call(["git", "clone", "git://srchub.org/indefero.git", "/home/www/indefero"])
        call(["git", "clone", "git://srchub.org/pluf2.git", "/home/www/pluf"])

        install_cron_jobs()
        update_mercurial_hooks()
        setup_git_daemon()
        setup_web_links()
        install_pear_modules()
        prep_apache()
        final_msg()
        print FINAL_MSG





exit_msg()
sys.exit()