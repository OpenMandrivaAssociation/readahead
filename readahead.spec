%define git_url git://git.fedorahosted.org/readahead

Summary:        Read a preset list of files into memory
Name:           readahead
Version:        1.5.6
Release:        %mkrel 1
Group:          System/Configuration/Boot and Init
License:        GPLv2+
URL:		https://hosted.fedoraproject.org/readahead
Source0:	readahead-%{version}.tar.bz2
Source1:	readahead_early
Source2:	default.early
# (fc) 1.4.6-2mdv default values for Mandriva
Patch0:		readahead-default.patch
# (fc) 1.4.6-2mdv create a temp file to detect if collector is running, autodelect collector enabling file at end of collection
Patch1:		readahead-1.5.6-autocollector.patch
Patch3:		readahead-1.5.6-fix-missing-separator.patch
BuildRequires:	libblkid-devel
BuildRequires:	audit-devel
BuildRequires:	auparse-devel
BuildRequires:	libext2fs-devel
Requires(post):    chkconfig
Requires(pre):     chkconfig
Requires:	procps
Requires:	gawk
Requires:	util-linux-ng
Obsoletes:	kernel-utils
# easy upgrade from 2009.1 to 2010.1
Conflicts:	%mklibname audit 0
Buildroot:      %{_tmppath}/%{name}-%{version}-buildroot

%description
readahead reads the contents of a list of files into memory,
which causes them to be read from cache when they are actually
needed. Its goal is to speed up the boot process.

%prep
%setup -q
%patch0 -p1 -b .default
%patch1 -p1 -b .autocollector
%patch3 -p1
install -m644 %{SOURCE2} lists/

%build
%configure2_5x \
	--sbindir=/sbin \
	--disable-rpath

%make

make rpm-lists-rebuild FILES="default.early" RPM_LIB="%{_lib}" RPM_ARCH="%{_arch}"


%install
rm -rf %{buildroot}
%makeinstall_std
%find_lang %{name}

install -m755 %{SOURCE1} %{buildroot}/sbin
install -m755 %{SOURCE1} %{buildroot}/sbin/readahead_later
sed -i -e 's/early/later/g' %{buildroot}/sbin/readahead_later

mkdir -p %{buildroot}%{_var}/lib/readahead
install -m644 lists/default.early %{buildroot}%{_var}/lib/readahead

# we don't use upstart
rm -rf %{buildroot}/etc/event.d
rm -rf %{buildroot}%{_sysconfdir}/init

%pre
if [ -f /etc/rc.d/init.d/readahead_early ]; then
  /sbin/chkconfig --del readahead_early > /dev/null 2>&1 
  /sbin/chkconfig --del readahead_later
fi

%post
if [ "$1" = "1" ]; then
 touch /.readahead_collect
fi

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc README lists/README.lists
/sbin/readahead
/sbin/readahead-collector
/sbin/readahead_early
/sbin/readahead_later
/etc/cron.daily/readahead.cron
/etc/cron.monthly/readahead-monthly.cron
%config(noreplace) %{_sysconfdir}/sysconfig/readahead
%config(noreplace) %{_sysconfdir}/readahead.conf
%dir /var/lib/readahead
%attr(0644,root,root) %{_var}/lib/readahead/default.early
