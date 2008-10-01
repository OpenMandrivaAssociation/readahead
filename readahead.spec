Summary:        Read a preset list of files into memory
Name:           readahead
Version:        1.4.6
Release:        %mkrel 4
Group:          System/Configuration/Boot and Init
License:        GPLv2+
URL:		https://hosted.fedoraproject.org/readahead
Source0:	readahead-%{version}.tar.bz2
Source1:	readahead_early
Source2:	default.early
# (fc) 1.4.6-2mdv default values for Mandriva
Patch0:		readahead-1.4.6-default.patch
# (fc) 1.4.6-2mdv create a temp file to detect if collector is running, autodelect collector enabling file at end of collection
Patch1:		readahead-1.4.6-autocollector.patch
# (fc) 1.4.6-2mdv don't generate later list
Patch2:		readahead-1.4.6-nolater.patch
Buildroot:      %{_tmppath}/%{name}-%{version}-root
Requires(post):    chkconfig
Requires(pre):     chkconfig
Requires:	procps gawk

BuildRequires:	e2fsprogs-devel audit-devel
BuildRequires: pkgconfig


Obsoletes:	kernel-utils

%description
readahead reads the contents of a list of files into memory,
which causes them to be read from cache when they are actually
needed. Its goal is to speed up the boot process.

%prep
%setup -q
%patch0 -p1 -b .default
%patch1 -p1 -b .autocollector
%patch2 -p1 -b .nolater
install -m644 %{SOURCE2} lists/

%build
%configure2_5x --sbindir=/sbin
%make 
make rpm-lists-rebuild FILES="default.early" RPM_LIB="%{_lib}" RPM_ARCH="%{_arch}"


%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std
%find_lang %{name}

install -m755 %{SOURCE1} $RPM_BUILD_ROOT/sbin

# we don't use upstart
rm -fr $RPM_BUILD_ROOT/etc/event.d
rm -f $RPM_BUILD_ROOT/etc/readahead.d/default.later

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && [ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;

%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING README 
%attr(0644,root,root) %{_sysconfdir}/readahead.d/default.early
/sbin/readahead
/sbin/readahead-collector
/sbin/readahead_early
/etc/cron.daily/readahead.cron
/etc/cron.monthly/readahead-monthly.cron
%config(noreplace) %{_sysconfdir}/sysconfig/readahead
%config(noreplace) /etc/readahead.conf
%dir /etc/readahead.d

%pre
if [ -f /etc/rc.d/init.d/readahead_early ]; then
  /sbin/chkconfig --del readahead_early > /dev/null 2>&1 
  /sbin/chkconfig --del readahead_later
fi

%post
if [ "$1" = "1" ]; then
 touch /.readahead_collect
fi
