%include	/usr/lib/rpm/macros.perl
Summary:	Essential command-line utilities for MySQL
Name:		percona-toolkit
Version:	3.0.5
Release:	1
License:	GPL v2
Group:		Applications/Databases
Source0:	https://www.percona.com/downloads/percona-toolkit/%{version}/source/tarball/%{name}-%{version}.tar.gz
# Source0-md5:	18aff435b050fe0d0e63acbcd280db55
Source1:	%{name}.conf
Source2:	%{name}.tmpfiles
Source3:	pt-kill.init
Patch0:		no-versioncheck.patch
Patch1:		bug-1314696.patch
URL:		https://www.percona.com/software/mysql-tools/percona-toolkit
BuildRequires:	perl-ExtUtils-MakeMaker
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	perl-DBD-mysql >= 1.0
Requires:	perl-DBI >= 1.13
Requires:	perl-Term-ReadKey >= 2.10
Requires:	rc-scripts
Provides:	group(percona-toolkit)
Provides:	user(percona-toolkit)
Obsoletes:	mysqldumpgrants
Obsoletes:	mysqltoolkit
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Percona Toolkit for MySQL is a collection of advanced command-line
tools used by Percona MySQL Support staff to perform a variety of
MySQL server and system tasks that are too difficult or complex to
perform manually, including:
- Verify master and replica data consistency
- Efficiently archive rows
- Find duplicate indexes
- Summarize MySQL servers
- Analyze queries from logs and tcpdump
- Collect vital system information when problems occur

Percona Toolkit for MySQL is derived from Maatkit and Aspersa, two of
the best-known MySQL management software utility toolkits for MySQL
server administration.

%prep
%setup -q
%patch0 -p1
%patch1 -p2

find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -v

# change shebang to be actual interpreter for rpm to generate deps on the
# interpreters.
%{__sed} -i -e '1s,^#!.*env *perl,#!%{__perl},' bin/pt-*
%{__sed} -i -e '1s,^#!.*env bash,#!/bin/bash,' bin/pt-*

%build
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/%{name},%{systemdtmpfilesdir},/etc/rc.d/init.d} \
	$RPM_BUILD_ROOT/var/run/%{name}

%{__make} pure_install \
	PERL_INSTALL_ROOT=$RPM_BUILD_ROOT

install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/pt-kill

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/percona-version-check

ln -s pt-show-grants $RPM_BUILD_ROOT%{_bindir}/mysqldumpgrants
echo '.so man1/pt-show-grants.1p' > $RPM_BUILD_ROOT%{_mandir}/man1/mysqldumpgrants.1

%{__rm} $RPM_BUILD_ROOT%{perl_vendorarch}/auto/%{name}/.packlist

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 310 percona-toolkit
%useradd -u 310 -d /etc/percona-toolkit -g percona-toolkit -c "Percona Toolkit User" percona-toolkit


%postun
if [ "$1" = "0" ]; then
	%userremove percona-toolkit
	%groupremove percona-toolkit
fi

%files
%defattr(644,root,root,755)
%doc Changelog README.md
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%ghost %{_sysconfdir}/%{name}/percona-version-check
%attr(754,root,root) /etc/rc.d/init.d/pt-kill
%attr(755,root,root) %{_bindir}/pt-*
%attr(755,root,root) %{_bindir}/mysqldumpgrants
%{systemdtmpfilesdir}/%{name}.conf
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/pt-*.1*
%{_mandir}/man1/mysqldumpgrants.1
%dir %attr(770,root,percona-toolkit) /var/run/%{name}
