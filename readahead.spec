%define git_url git://git.fedorahosted.org/readahead

Summary:        Read a preset list of files into memory
Name:           readahead
Version:        1.5.7
Release:        10
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
BuildRequires:	libblkid-devel
BuildRequires:	audit-devel
BuildRequires:	auparse-devel
BuildRequires:	ext2fs-devel
Requires(post):    chkconfig
Requires(pre):     chkconfig
Requires(pre):   systemd
Requires:	procps
Requires:	gawk
Requires:	util-linux-ng
Obsoletes:	kernel-utils
# easy upgrade from 2009.1 to 2010.1
Conflicts:	%mklibname audit 0

%description
readahead reads the contents of a list of files into memory,
which causes them to be read from cache when they are actually
needed. Its goal is to speed up the boot process.

%prep
%setup -q
%patch0 -p1 -b .default
%patch1 -p1 -b .autocollector
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

# (bor) disable for now, it is done in rc.sysinit
rm -rf %{buildroot}/lib/systemd/system/default.target.wants
%pre
if [ -f /etc/rc.d/init.d/readahead_early ]; then
  /sbin/chkconfig --del readahead_early > /dev/null 2>&1 
  /sbin/chkconfig --del readahead_later
fi

%post
if [ "$1" = "1" ]; then
 touch /.readahead_collect
fi

%files -f %{name}.lang
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
/lib/readahead/%{name}-*.sh
# (bor) disable for now, it is done in rc.sysinit
#/lib/systemd/system/default.target.wants/readahead-*.service
/lib/systemd/system/readahead-*.service


%changelog
* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 1.5.7-3mdv2011.0
+ Revision: 669413
- mass rebuild

* Sat Oct 09 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 1.5.7-2mdv2011.0
+ Revision: 584445
- do not enable systemd units by default; they fail currently and
  readahead is called by rc.sysinit anyway

* Sun Oct 03 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1.5.7-1mdv2011.0
+ Revision: 582713
- update to new version 1.5.7
- update file list
- drop patch 3

* Sun Aug 29 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1.5.6-1mdv2011.0
+ Revision: 574121
- update to new version 1.5.6
- drop patch 2, fixed by upstream
- rediff patch 1
- Patch3: fix missing separatos
- update deafult.early list

* Wed May 26 2010 Frederic Crozat <fcrozat@mandriva.com> 1.5.4-5mdv2010.1
+ Revision: 546291
- Add conflicts to ease upgrade from 2009.1

* Tue Mar 23 2010 Olivier Blin <oblin@mandriva.com> 1.5.4-4mdv2010.1
+ Revision: 526775
- properly kill daemon when audit is not available

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.5.4-3mdv2010.1
+ Revision: 523876
- adjust deps

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 1.5.4-2mdv2010.1
+ Revision: 521626
- rebuilt for 2010.1

* Fri Nov 20 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1.5.4-1mdv2010.1
+ Revision: 467759
- drop patch 2, applied by upstream
- update to new version 1.5.4

* Sat Sep 26 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1.5.1-1mdv2010.0
+ Revision: 449493
- update to new version 1.5.1
- Patch2: remove console owner

* Sun Aug 30 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1.5.0-1mdv2010.0
+ Revision: 422599
- add buildrequires on libext2fs-devel
- update default.early list
- update to new version 1.5.0
- rediff patch 0
- spec file clean

* Wed Jun 24 2009 Frederic Crozat <fcrozat@mandriva.com> 1.4.9-4mdv2010.0
+ Revision: 388881
- Change default configuration to split early / later lists correctly when using autologin from gdm / kdm
- Make readahead_early/later calls blocking, better performance this way

* Tue Jun 09 2009 Frederic Crozat <fcrozat@mandriva.com> 1.4.9-3mdv2010.0
+ Revision: 384368
- Switch to libblkid-devel

* Mon Mar 23 2009 Frederic Crozat <fcrozat@mandriva.com> 1.4.9-2mdv2009.1
+ Revision: 360730
- Update default configuration for file to track to start collector and early/later split

* Fri Mar 20 2009 Frederic Crozat <fcrozat@mandriva.com> 1.4.9-1mdv2009.1
+ Revision: 359161
- Release 1.4.9
- Put back readahead_later (for usage by speedboot)
- Tweak a little default configuration

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 1.4.6-5mdv2009.1
+ Revision: 351575
- rebuild

* Wed Oct 01 2008 Frederic Crozat <fcrozat@mandriva.com> 1.4.6-4mdv2009.0
+ Revision: 290492
- Try to avoid collecting dkms events (discovered in Mdv bug #44471)

* Fri Sep 26 2008 Frederic Crozat <fcrozat@mandriva.com> 1.4.6-3mdv2009.0
+ Revision: 288689
- Create auto-collector file when first installing the package

* Fri Sep 26 2008 Frederic Crozat <fcrozat@mandriva.com> 1.4.6-2mdv2009.0
+ Revision: 288678
- Remove initscripts, will be handle directly in rc.sysinit
- Don't generate / use later lists, preload is better for this
- Patch0: change default values for readahead-collector
- Patch1: improve collector for usage as autocollector
- Patch2: don't try to sort later list in cron.daily
- Remove upstart events files

* Wed Sep 17 2008 Frederic Crozat <fcrozat@mandriva.com> 1.4.6-1mdv2009.0
+ Revision: 285385
- Release 1.4.6
- Add initscripts (since we don't use upstart)
- tune readahead_early for MandrivaLinux

  + Thierry Vignaud <tv@mandriva.org>
    - drop patch 1
    - new release

* Mon Aug 25 2008 Frederic Crozat <fcrozat@mandriva.com> 1.4.4-1mdv2009.0
+ Revision: 275762
- Release 1.4.4
- Remove patch0 (merged upstream)
- fix location of readahead-collector

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Wed Sep 05 2007 Thierry Vignaud <tv@mandriva.org> 1.4.1-1mdv2008.1
+ Revision: 80160
- new release

* Thu Aug 23 2007 Thierry Vignaud <tv@mandriva.org> 1.3-2mdv2008.0
+ Revision: 69939
- kill file require on chkconfig


* Wed Nov 22 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.3-1mdv2007.0
+ Revision: 86175
- Import readahead

* Wed Nov 22 2006 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.3-1mdv2007.1
- new release

* Thu Aug 11 2005 Thierry Vignaud <tvignaud@mandriva.com> 1.1-1mdk
- stolen from fedora
- make it --short-circuit aware
- status: provided lists are gnome oriented, fedora oriented, ...

