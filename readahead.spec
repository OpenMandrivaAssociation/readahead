Summary:        Read a preset list of files into memory
Name:           readahead
Version:        1.4.1
Release:        %mkrel 1
Group:          System/Configuration/Boot and Init
License:        GPL
URL:		http://cvs.fedora.redhat.com/viewcvs/devel/readahead/
Source0:	readahead-%{version}.tar.bz2
# make early script LSB compliant so that it doesn't run at end
Patch0:		readahead-1.3-lsb-init.patch
# enable early readahead as soon there's at least 240Mb of RAM
Patch1:		readahead-1.3-lower-memteset.patch
Buildroot:      %{_tmppath}/%{name}-%{version}-root
Requires(post):    chkconfig
Requires(pre):     chkconfig
Requires:	procps /bin/gawk

BuildRequires:	e2fsprogs-devel audit-devel
BuildRequires: pkgconfig


Obsoletes:	kernel-utils

%description
readahead reads the contents of a list of files into memory,
which causes them to be read from cache when they are actually
needed. Its goal is to speed up the boot process.

%prep
%setup -q
%patch0 -p0
%patch1 -p0

%build
%configure2_5x
make CFLAGS="$RPM_OPT_FLAGS" RPM_LIB="%{_lib}" RPM_ARCH="%{_arch}"

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && [ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;

%files
%defattr(-,root,root)
%doc COPYING README scripts/readahead-check
%attr(0644,root,root) %{_sysconfdir}/readahead.d/default.early
%attr(0644,root,root) %{_sysconfdir}/readahead.d/default.later
%{_sbindir}/readahead
%{_sbindir}/readahead-collector
/etc/rc.d/init.d/readahead_later
/etc/rc.d/init.d/readahead_early
/etc/cron.daily/readahead.cron
%config(noreplace) /etc/readahead.conf

%preun
if [ "$1" = "0" ] ; then
 /sbin/chkconfig --del readahead_later
 /sbin/chkconfig --del readahead_early
fi

%post
/sbin/chkconfig --add readahead_later
/sbin/chkconfig --add readahead_early

%triggerpostun -- kernel-utils
/sbin/chkconfig --add readahead_later
/sbin/chkconfig --add readahead_early
exit 0


