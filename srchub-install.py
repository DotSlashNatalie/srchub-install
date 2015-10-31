import locale
from dialog import Dialog
from subprocess import call
import sys

# This is almost always a good thing to do at the beginning of your programs.
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
d = Dialog(dialog="dialog", autowidgetsize=True)
distro = ""

def install_debian_package(package):
    d.infobox(package, title="Installing...")
    # install package


def exit_msg():
    print "Thank you for using the srchub installer\n"
    print "Please send feedback to adamsna@datanethost.net"

def install_cron_jobs():
    return d.yesno("Do you want me to attempt to install the cron jobs?")

def install_package(package):
    if distro == "Debian":
        call(["apt-get", "--assume-yes", "-y", "install", package])

def install_packages():
    code = d.yesno("Do you want me to attempt to install the needed packages?")
    if code == d.OK:
        d.gauge_start("Installing...")
        packages = ["git", "mercurial", "subversion", "mariadb-server", "mariadb-client", "libapache2-mod-php5",
                        "php5-curl", "php5-mysql", "php5-cli", "git-daemon-run", "gitweb", "php-pear"]
        percent = 0
        i = 0
        for package in packages:
            d.gauge_update(percent, "Installing " + package)
            install_package(package)
            i += 1
            percent = (i / len(packages)) * 100



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
    if tag == "1":  # Install srchub
        pass
    else:  # Install indefero vanilla
        pass


exit_msg()