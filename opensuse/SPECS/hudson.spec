# TODO:
# - how to add to the trusted service of the firewall?

%define _prefix	%{_usr}/lib/hudson
%define workdir	%{_var}/lib/hudson

Name:		hudson
Version:	%{ver}
Release:	1.1
Summary:	Continous Build Server
Source:		hudson.war
Source1:	hudson.init.in
Source2:	hudson.sysconfig.in
Source3:	hudson.logrotate
Source4:    hudson.repo
URL:		http://hudson-ci.org/
Group:		Development/Tools/Building
License:	MIT/X License, GPL/CDDL, ASL2
BuildRoot:	%{_tmppath}/build-%{name}-%{version}
# see the comment below from java-1.6.0-openjdk.spec that explains this dependency
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons,
# and this change was brought into RHEL-4.  java-1.5.0-ibm packages
# also included the epoch in their virtual provides.  This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0".  In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0.  So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages.  Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".
#
# java-1_6_0-sun provides this at least
Requires:	java >= 1.6.0
PreReq:		/usr/sbin/groupadd /usr/sbin/useradd
#PreReq:		%{fillup_prereq}
BuildArch:	noarch

%description
Hudson monitors executions of repeated jobs, such as building a software
project or jobs run by cron. Among those things, current Hudson focuses on the
following two jobs:
- Building/testing software projects continuously, just like CruiseControl or
  DamageControl. In a nutshell, Hudson provides an easy-to-use so-called
  continuous integration system, making it easier for developers to integrate
  changes to the project, and making it easier for users to obtain a fresh
  build. The automated, continuous build increases the productivity.
- Monitoring executions of externally-run jobs, such as cron jobs and procmail
  jobs, even those that are run on a remote machine. For example, with cron,
  all you receive is regular e-mails that capture the output, and it is up to
  you to look at them diligently and notice when it broke. Hudson keeps those
  outputs and makes it easy for you to notice when something is wrong.




Authors:
--------
    Hudson Community <dev@hudson.java.net>

%prep
%setup -q -T -c

%build

%install
rm -rf "%{buildroot}"
%__install -D -m0644 "%{SOURCE0}" "%{buildroot}%{_prefix}/%{name}.war"
%__install -d "%{buildroot}%{workdir}"
%__install -d "%{buildroot}%{workdir}/plugins"

%__install -d "%{buildroot}/var/log/hudson"

%__install -D -m0755 "%{SOURCE1}" "%{buildroot}/etc/init.d/%{name}"
%__sed -i 's,@@WAR@@,%{_prefix}/%{name}.war,g' "%{buildroot}/etc/init.d/%{name}"
%__install -d "%{buildroot}/usr/sbin"
%__ln_s "../../etc/init.d/%{name}" "%{buildroot}/usr/sbin/rc%{name}"

%__install -D -m0600 "%{SOURCE2}" "%{buildroot}/etc/sysconfig/%{name}"
%__sed -i 's,@@HOME@@,%{workdir},g' "%{buildroot}/etc/sysconfig/%{name}"

%__install -D -m0644 "%{SOURCE3}" "%{buildroot}/etc/logrotate.d/%{name}"

%__install -D -m0644 "%{SOURCE4}" "%{buildroot}/etc/zypp/repos.d/hudson.repo"
%pre
/usr/sbin/groupadd -r hudson &>/dev/null || :
# SUSE version had -o here, but in Fedora -o isn't allowed without -u
/usr/sbin/useradd -g hudson -s /bin/false -r -c "Hudson Continuous Build server" \
	-d "%{workdir}" hudson &>/dev/null || :

%post
/sbin/chkconfig --add hudson

%preun
if [ "$1" = 0 ] ; then
    # if this is uninstallation as opposed to upgrade, delete the service
    /sbin/service hudson stop > /dev/null 2>&1
    /sbin/chkconfig --del hudson
fi
exit 0

%postun
if [ "$1" -ge 1 ]; then
    /sbin/service hudson condrestart > /dev/null 2>&1
fi
exit 0

%clean
%__rm -rf "%{buildroot}"

%files
%defattr(-,root,root)
%dir %{_prefix}
%{_prefix}/%{name}.war
%attr(0755,hudson,hudson) %dir %{workdir}
%attr(0750,hudson,hudson) /var/log/hudson
%config /etc/logrotate.d/%{name}
%config /etc/init.d/%{name}
%config /etc/sysconfig/%{name}
/etc/zypp/repos.d/hudson.repo
/usr/sbin/rc%{name}

%changelog
%changelog
* Fri Jan 05 2013 Winston Prakash <winston.prakash@gmail.com> - 3.0.0
  - Complete change log is available at http://hudson-ci.org/changelog.html

 
