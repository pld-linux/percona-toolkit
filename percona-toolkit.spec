# TODO
# - the programs spit in to the face for security, hardcoded paths writing to /tmp:
#   $ grep -r /tmp/ bin | wc -l
#   187
#   so unless you're masohist never run the programs as root or in host where
#   you have hostile users
#   https://bugs.launchpad.net/percona-toolkit/+bug/871438
# - TODO is to patch code to use mktemp-related or private workdirs
# - TODO # Mounted Filesystems ########################################
#/usr/bin/pt-summary[1189]: typeset: %5s: not identifier

%include	/usr/lib/rpm/macros.perl
Summary:	Essential command-line utilities for MySQL
Name:		percona-toolkit
Version:	2.0.3
Release:	1
License:	GPL v2
Group:		Applications/Databases
Source0:	https://www.percona.com/downloads/percona-toolkit/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	10f394c101067b6bf28427c5d4833330
URL:		http://www.percona.com/software/percona-toolkit/
BuildRequires:	perl-ExtUtils-MakeMaker
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	sed >= 4.0
Requires:	perl-DBD-mysql >= 1.0
Requires:	perl-DBI >= 1.13
Requires:	perl-Term-ReadKey >= 2.10
Obsoletes:	maatkit
Obsoletes:	mysqldumpgrants
Obsoletes:	mysqltoolkit
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Percona Toolkit is a collection of advanced command-line tools used by
Percona support staff to perform a variety of MySQL and system tasks
that are too difficult or complex to perform manually, including:

- Verify master and replica data consistency
- Efficiently archive rows
- Find duplicate indexes
- Summarize MySQL servers
- Analyze queries from logs and tcpdump
- Collect vital system information when problems occur

Percona Toolkit is derived from Maatkit and Aspersa, two of the
best-known utility toolkits for MySQL server administration.

%prep
%setup -q

# change shebang to be actual interpreter for rpm to generate deps on the
# interpreters.
%{__sed} -i -e '1s,^#!.*env perl,#!%{__perl},' bin/pt-*
%{__sed} -i -e '1s,^#!.*env bash,#!/bin/bash,' bin/pt-*

# insecure programs, see TODO above
cd bin
rm pt-pmp

%build
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
%{__make} pure_install \
	PERL_INSTALL_ROOT=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{perl_vendorarch}/auto/%{name}/.packlist

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc Changelog README
%dir %{_sysconfdir}/%{name}
%attr(755,root,root) %{_bindir}/pt-*
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/pt-*.1*
