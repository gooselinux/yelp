%define gnome_doc_utils_version 0.17.2
%define gtk2_version 2.10.0
%define libglade_version 2.0.0
%define libgnomeui_version 2.14.0
%define libxml_version 2.6.5
%define libxslt_version 1.1.4
%define startup_notification_version 0.8
%define rarian_version 0.7.0
%define gecko_version 1.9.2

%define pango_version 1.0.99
%define desktop_file_utils_version 0.3-7

Summary: Help browser for the GNOME desktop
Name: yelp
Version: 2.28.1
Release: 8%{?dist}.goose.1
Source: http://download.gnome.org/sources/yelp/2.28/%{name}-%{version}.tar.bz2
URL: http://live.gnome.org/Yelp
Patch1: yelp-2.15.5-fedora-docs.patch
Patch2: yelp-2.13.2-add-mime-handling.patch
Patch3: yelp-use-pango.patch
# http://bugzilla.gnome.org/show_bug.cgi?id=497559
# Patch6: hp.patch

# http://bugzilla.gnome.org/show_bug.cgi?id=431077
# XXX Does this no longer apply to yelp >= 2.19.1 ?
#Patch8: yelp-2.18.1-posix-man.patch

# Patch12: libxul.patch

# http://bugzilla.gnome.org/show_bug.cgi?id=592762
Patch13: ellipsis.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=614029
Patch14: yelp-dir-prefix.patch

# Patch from https://bugs.launchpad.net/ubuntu/+source/yelp/+bug/425709
Patch15: yelp-xulrunner-fix.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=575674
Patch16: yelp-2.28.1-el6-translation-updates.patch

License: GPLv2+
Group: Applications/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: docbook-dtds
Requires: gecko-libs >= %{gecko_version}
Requires: libxslt >= %{libxslt_version}
Requires: gnome-doc-utils-stylesheets >= %{gnome_doc_utils_version}
Requires: gnome-user-docs
Requires: rarian >= %{rarian_version}
Requires(pre): GConf2
Requires(post): GConf2
Requires(post): desktop-file-utils
Requires(preun): GConf2
Requires(postun): desktop-file-utils
BuildRequires: pango-devel >= %{pango_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: gecko-devel-unstable >= %{gecko_version}
BuildRequires: libgnomeui-devel >= %{libgnomeui_version}
BuildRequires: libglade2-devel >= %{libglade_version}
BuildRequires: libxml2-devel >= %{libxml_version}
BuildRequires: libxslt-devel >= %{libxslt_version}
BuildRequires: libgcrypt-devel
BuildRequires: fontconfig
BuildRequires: GConf2-devel
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: gnome-doc-utils-stylesheets >= %{gnome_doc_utils_version}
BuildRequires: startup-notification-devel >= %{startup_notification_version}
BuildRequires: libXt-devel
BuildRequires: dbus-devel
BuildRequires: gettext-devel
BuildRequires: rarian-devel >= %{rarian_version}
BuildRequires: intltool
BuildRequires: gnome-common
BuildRequires: automake autoconf libtool

%description
Yelp is the help browser for the GNOME desktop. It is designed
to help you browse all the documentation on your system in
one central tool, including traditional man pages, info pages and
documentation written in DocBook.

%prep
%setup -q
%patch1 -p1 -b .fedora-docs
%patch2 -p1 -b .add-mime-handling
%patch3 -p1 -b .use-pango
#%patch6 -p1 -b .hp
#%patch12 -p1 -b .libxul
%patch13 -p1 -b .ellipsis
%patch14 -p1 -b .dir-prefix
%patch15 -p1 -b .xulrunner-fix
%patch16 -p1 -b .el6-translation-updates

# force regeneration
rm data/yelp.schemas

autoreconf -i -f -i

%build
%configure 			\
	--with-mozilla=libxul-embedding	\
	--disable-schemas-install

# drop unneeded direct library deps with --as-needed
# libtool doesn't make this easy, so we do it the hard way
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' -e 's/    if test "$export_dynamic" = yes && test -n "$export_dynamic_flag_spec"; then/      func_append compile_command " -Wl,-O1,--as-needed"\n      func_append finalize_command " -Wl,-O1,--as-needed"\n\0/' libtool

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

desktop-file-install --vendor gnome --delete-original	\
	--dir $RPM_BUILD_ROOT%{_datadir}/applications	\
	--remove-category Application			\
	$RPM_BUILD_ROOT%{_datadir}/applications/*

mkdir -p -m 755 $RPM_BUILD_ROOT/%{_datadir}/gnome/help

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/yelp.schemas >& /dev/null || :
update-desktop-database &> /dev/null ||:

# update icon themes
touch %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/yelp.schemas >& /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/yelp.schemas >& /dev/null || :
fi

%postun
update-desktop-database &> /dev/null ||:

%files -f %{name}.lang
%defattr(-,root,root)
%doc ChangeLog AUTHORS COPYING MAINTAINERS NEWS README
%{_sysconfdir}/gconf/schemas/yelp.schemas
%{_bindir}/*
%{_datadir}/applications/*
%dir %{_datadir}/gnome/help
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/yelp

%changelog
* Fri Oct 14 2011 Clint Savage <clint@gooseproject.org> - 2.28.1-8.goose.1
- Remove dependency on libbeagle-devel and WITH_MONO macro

* Fri Aug 27 2010 Jan Horak <jhorak@redhat.com> - 2.28.1-8
- Rebuild against newer gecko

* Fri Jun 11 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.1-7
- Translation updates for Red Hat Supported Languages (RH bug #575674).
- This also includes the fix for the or_IN crasher (RH bug #578094).

* Tue Jun 08 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.1-6
- Crash on startup in or_IN locale (RH bug #578094).

* Mon May 24 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.1-5
- Require gnome-user-docs so that Help->Contents works (RH bug #580002).

* Fri Apr 16 2010 Martin Stransky <stransky@redhatcom> 2.28.1-4
- regenerated xulrunner patch

* Thu Apr  1 2010 Matthias Clasen <mclasen@redhatcom> 2.28.1-3
- Fix loading the TOC with xulrunner 1.9.2
  Resolves: #577331

* Fri Mar 26 2010 Ray Strode <rstrode@redhat.com> 2.28.1-2
- Support relocatable .gnome2 directory
  Resolves: #577295

* Fri Dec  4 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-1
- Update to 2.28.1

* Wed Dec  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- make mono dep more automatic

* Mon Sep 21 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Mon Aug 24 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Sun Aug 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.3-2
- Remove space before ellipsis in menuitems

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.3-1
- Update to 2.27.3

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat Jul 18 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.2-3
- Drop unused direct dependencies

* Thu Jul  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.2-2
- Shrink GConf schemas

* Mon Jun 29 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.2-1
- Update to 2.27.2
- Bump gnome_doc_utils requirement to 0.17.2.

* Mon Jun 15 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.1-1
- Update to 2.27.1

* Mon Apr 27 2009 Christopher Aillon <caillon@redhat.com> - 2.26.0-3
- Rebuild against newer gecko

* Mon Apr  6 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-2
- Clean up Requires a bit

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.1-1
- Update to 2.25.1

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.24.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Dec 21 2008 Christopher Aillon <caillon@redhat.com> - 2.24.0-5
- Rebuild against newer gecko

* Sat Dec 20 2008 Caolán McNamara <caolanm@redhat.com> - 2.24.0-4
- rebuild for gecko

* Fri Nov 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-3
- %%summary and %%description tweakage

* Wed Sep 24 2008 Christopher Aillon <caillon@redhat.com> - 2.24.0-2
- Rebuild against newer gecko

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update ot 2.24.0

* Mon Sep 01 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2-1
- Update to 2.23.2

* Tue Jul 22 2008 Martin Stransky <stransky@redhat.com> - 2.23.1-3
- rebuild for xulrunner update

* Fri Jun 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.1-2
- Use a standard icon name in the desktop file

* Tue Jun 03 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.1-1
- Update to 2.23.1

* Mon May 19 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.1-2
- Require docbook-dtds (RH bug #447209).

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Mon Mar 31 2008 Jon McCann <jmccann@redhat.com> - 2.22.0-4
- Disallow launchers when running under GDM.

* Mon Mar 31 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-3
- Update patch for RH bug #437328.

* Thu Mar 13 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-2
- Add patch for RH bug #437328 (searching with Beagle broken).

* Sun Mar 09 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Thu Feb 28 2008 Martin Stransky <stransky@redhat.com> - 2.21.90-4
- updated xulrunner patch, rebuild against xulrunner

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.21.90-3
- Autorebuild for GCC 4.3

* Sun Feb 17 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.90-2
- Rebuild with GCC 4.3

* Mon Jan 28 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Tue Jan 08 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.2-2
- Look for new-style xulrunner pkg-config files.
- Build requires gecko-devel-unstable.

* Tue Jan 08 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Sun Dec 30 2007 Jeremy Katz <katzj@redhat.com> - 2.21.1-3
- Rebuild for new xulrunner

* Sat Dec  8 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.1-2
- Rebuild against new libbeagle

* Mon Dec  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.1-1
- Update to 2.21.1

* Mon Dec  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-9
- Rebuild against xulrunner again

* Thu Nov 22 2007 Martin Stransky <stransky@redhat.com> - 2.20.0-8
- rebuild against xulrunner

* Fri Nov 16 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-7
- Handle .HP tags in man pages

* Fri Nov 09 2007 Matthew Barnes <mbarnes@redhat.com> - 2.20.0-6
- Rebuild against gecko-libs 1.8.1.9.

* Mon Nov  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-5
- Fix a crash in search (#361041)

* Sun Nov  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-4
- Fix a crash when loading the rarian docs

* Thu Nov 01 2007 Matthew Barnes <mbarnes@redhat.com> - 2.20.0-3
- Rebuild against gecko-libs 1.8.1.8.

* Mon Oct 22 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-2
- Rebuild against new dbus-glib

* Mon Sep 17 2007 Matthew Barnes <mbarnes@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Thu Aug 28 2007 Matthew Barnes <mbarnes@redhat.com> - 2.19.90-3
- Remove --add-only-show-in from desktop-file-install (RH bug #258821).

* Wed Aug 22 2007 Matthew Barnes <mbarnes@redhat.com> - 2.19.90-2
- Mass rebuild

* Mon Aug 13 2007 Matthew Barnes <mbarnes@redhat.com> - 2.19.90-1
- Update to 2.19.90
- Remove "info-gnutls" patch (fixed upstream).
- Remove patch for GNOME bug #370167 (fixed upstream).
- Remove patch for GNOME bug #430365 (fixed upstream).
- Remove patch for GNOME bug #431078 (fixed upstream).

* Wed Aug  8 2007 Christopher Aillon <caillon@redhat.com> - 2.19.1-4
- Rebuild against newer gecko

* Fri Aug 03 2007 Matthew Barnes <mbarnes@redhat.com> - 2.19.1-3
- Require rarian-devel for building.

* Fri Aug  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-2
- Update the license field

* Thu Aug 02 2007 Matthew Barnes <mbarnes@redhat.com> - 2.19.1-1
- Update to 2.19.1
- Adapt the "apropos" patch for 2.19.1.
- The "posix-man" patch appears to no longer apply.
- Update dependencies based on configure.ac.

* Wed Jul 25 2007 Jeremy Katz <katzj@redhat.com> - 2.18.1-7
- rebuild for toolchain bug

* Mon Jul 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-6
- Require gnome-doc-utils-stylesheets instead of gnome-doc-utils

* Fri Jul 20 2007 Kai Engert <kengert@redhat.com> - 2.18.1-5
- Rebuild against newer gecko

* Wed May 25 2007 Christopher Aillon <caillon@redhat.com> - 2.18.1-4
- Rebuild against newer gecko

* Wed Apr 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-3
- Improve the man parser a bit
- Fix another crash in the info parser 

* Tue Apr 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-2
- Fix a crash in the info parser (#216308)

* Mon Apr 09 2007 Matthew Barnes <mbarnes@redhat.com> - 2.18.1-1
- Update to 2.18.1

* Fri Mar 23 2007 Christopher Aillon <caillon@redhat.com> - 2.18.0-2
- Rebuild against newer gecko

* Tue Mar 13 2007 Matthew Barnes <mbarnes@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Wed Feb 28 2007 Matthew Barnes <mbarnes@redhat.com> - 2.16.2-5
- Rebuild against newer gecko.

* Fri Feb 23 2007 Matthias Clasen <mclasen@redhat.com> 2.16.2-4
- Don't own /usr/share/icons/hicolor

* Tue Feb 13 2007 Bill Nottingham <notting@redhat.com> 2.16.2-3
- own %%{_datadir}/gnome/help (#205799)
- rpmlint silencing:
 - add a URL: tag
 - add some docs

* Thu Dec 21 2006 Christopher Aillon <caillon@redhat.com> 2.16.2-2
- Rebuild against newer gecko

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.2-1
- Update to 2.16.2
- Drop obsolete patch

* Fri Nov  3 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-6
- Improve the whatis parser

* Fri Nov  3 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-5
- Silence %%pre

* Sun Oct 29 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-4
- Improve the previous fix

* Sun Oct 29 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-3
- Fix some crashes (#212888)

* Fri Oct 27 2006 Christopher Aillon <caillon@redhat.com> - 2.16.1-2
- Rebuild against newer gecko

* Sun Oct 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-5
- Fix scripts according to the packaging guidelines

* Thu Oct 12 2006 Christopher Aillon <caillon@redhat.com> - 2.16.0-4.fc6
- Update requires to the virtual gecko version instead of a specific app

* Thu Sep 14 2006 Christopher Aillon <caillon@redhat.com> - 2.16.0-3.fc6
- Rebuild

* Wed Sep  6 2006 Matthias Clasen  <mclasen@redhat.com> - 2.16.0-2.fc6
- Actually apply the Pango patch

* Mon Sep  4 2006 Matthias Clasen  <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0

* Tue Aug 29 2006 Matthias Clasen  <mclasen@redhat.com> - 2.15.91-3.fc6
- Use Pango 

* Wed Aug 23 2006 Matthew Barnes <mbarnes@redhat.com> - 2.15.91-2
- Rebuild

* Thu Aug 10 2006 Matthew Barnes <mbarnes@redhat.com> - 2.15.91-1
- Update to 2.15.91

* Thu Jul 27 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.5-1
- Update to 2.15.5
- Rebuild against firefox-devel

* Tue Jul 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2-2
- Go back to 2.15.2, since gecko 1.8 is still missing

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.15.3-1.1
- rebuild

* Tue Jun 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.3-1
- Update to 2.15.3

* Tue May 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2-1
- Update to 2.15.2

* Mon May 15 2006 Matthew Barnes <mbarnes@redhat.com> - 2.15.1-3
- Bump mozilla_version from 1.7.12 to 1.7.13 (closes #190880).

* Mon May 15 2006 Matthew Barnes <mbarnes@redhat.com> - 2.15.1-2
- Add build requirements: startup-notification-devel
                          libgnomeprintui22-devel
                          libXt-devel

* Tue May  9 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-1
- Update to 2.15.1

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Mon Feb 27 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.6-1
- Update to 2.13.6

* Sun Feb 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-2
- Turn on info and man support for test3

* Sun Feb 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-1
- Update to 2.13.5

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.4-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.4-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.4-1
- Update to 2.13.4

* Thu Jan 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.3-1
- Update to 2.13.3
- enable search

* Wed Jan 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.2-3
- Disable search, since it doesn't compile against 
  current beagle

* Thu Dec 15 2005 David Malcolm <dmalcolm@redhat.com> - 2.13.2-2
- Patched to include DocBook mimetype in desktop file, and added preun and post
  hooks to update-desktop-database (#175880)
- Patched to ensure that Yelp recognizes that it can handle the mimetype of the
  documentation as reported by gnomevfs (also #175880) 

* Thu Dec 15 2005 Matthias Clasen <mclasen@redhat.com> 2.13.2-1
- Update to 2.13.2

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 30 2005 Matthias Clasen <mclasen@redhat.com> - 2.13.1-6
- Update to 2.13.1

* Wed Oct 19 2005 Jeremy Katz <katzj@redhat.com> - 2.12.1-5
- build on ppc64 now that we have mozilla there again

* Tue Oct 18 2005 Christopher Aillon <caillon@redhat.com> - 2.12.1-4
- Rebuild

* Mon Oct 17 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.1-3
- Include the category General|Linux|Distributions|Other on the
  title page

* Mon Oct 17 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.1-2
- Fix a double-free bug

* Thu Sep 29 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.1-1
- Update to 2.12.1

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-1
- Update to 2.12.0

* Wed Aug 17 2005 Jeremy Katz <katzj@redhat.com> - 2.11.1-5
- rebuild

* Wed Aug 17 2005 Ray Strode <rstrode@redhat.com> 2.11.1-4
- rebuild

* Sun Jul 31 2005 Christopher Aillon <caillon@redhat.com> 2.11.1-3
- Rebuild against newer mozilla

* Tue Jul 19 2005 Christopher Aillon <caillon@redhat.com> 2.11.1-2
- Rebuild against newer mozilla

* Wed Jul 13 2005 Matthias Clasen <mclasen@redhat.com> 2.11.1-1
- Newer upstream version

* Thu May 19 2005 Ray Strode <rstrode@redhat.com> 2.10.0-1
- Update to 2.10.0 (bug 157752, 146862).

* Thu May 19 2005 Christopher Aillon <caillon@redhat.com> 2.9.3-7
- Depend on mozilla 1.7.8

* Thu Apr 28 2005 Ray Strode <rstrode@redhat.com> 2.9.3-6
- Disable man support
- Disable info support
- Don't try to install schemas during install (bug 154035)

* Mon Apr 18 2005 Ray Strode <rstrode@redhat.com> 2.9.3-5
- Depend on mozilla 1.7.7

* Mon Apr  4 2005 Ray Strode <rstrode@redhat.com> 2.9.3-4
- rebuilt

* Wed Mar  9 2005 Christopher Aillon <caillon@redhat.com> 2.9.3-3
- Depend on mozilla 1.7.6

* Sat Mar  5 2005 Christopher Aillon <caillon@redhat.com> 2.9.3-2
- Rebuild against GCC 4.0

* Fri Jan 28 2005 Matthias Clasen <mclasen@redhat.com> 2.9.3-1
- Update to 2.9.3

* Mon Dec 20 2004 Christopher Aillon <caillon@redhat.com> 2.6.5-1
- Update to 2.6.5

* Sat Nov  6 2004 Marco Pesenti Gritti <mpg@redhat.com> 2.6.4-1
- Update to 2.6.4

* Wed Sep 22 2004 Christopher Aillon <caillon@redhat.com> 2.6.3-1
- Update to 2.6.3

* Fri Sep 03 2004 Matthias Clasen <mclasen@redhat.com> 2.6.2-2
- fix an translation problem

* Tue Aug 31 2004 Alex Larsson <alexl@redhat.com> 2.6.2-1
- update to 2.6.2

* Wed Jun 30 2004 Christopher Aillon <caillon@redhat.com> 2.6.1-1
- Update to 2.6.1

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Apr  1 2004 Alex Larsson <alexl@redhat.com> 2.6.0-1
- update to 2.6.0

* Mon Mar 15 2004 Alex Larsson <alexl@redhat.com> 2.5.90-2
- Fix requirements

* Wed Mar 10 2004 Alex Larsson <alexl@redhat.com> 2.5.90-1
- update to 2.5.90

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 25 2004 Alexander Larsson <alexl@redhat.com> 2.5.6-1
- update to 2.5.6

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 28 2004 Alexander Larsson <alexl@redhat.com> 2.5.3-1
- update to 2.5.3

* Wed Dec 24 2003 Tim Waugh <twaugh@redhat.com> 2.4.0-2
- Fix g_strdup_printf usage in info2html (bug #111200, patch from
  Miloslav Trmac).

* Tue Sep  9 2003 Alexander Larsson <alexl@redhat.com> 2.4.0-1
- update to 2.4.0 (only code change is bugfix from me)
- Fixed the utf8 manpage patch (#91689)

* Wed Aug 27 2003 Alexander Larsson <alexl@redhat.com> 2.3.6-2
- info and manpages are utf8

* Wed Aug 20 2003 Alexander Larsson <alexl@redhat.com> 2.3.6-1
- Update for gnome 2.3

* Wed Jul  9 2003 Alexander Larsson <alexl@redhat.com> 2.2.3-1.E
- Rebuild

* Mon Jul  7 2003 Alexander Larsson <alexl@redhat.com> 2.2.3-1
- update to 2.2.3

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 14 2003 Jeremy Katz <katzj@redhat.com> 2.2.0-3
- fix buildrequires

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 21 2003 Alexander Larsson <alexl@redhat.com> 2.2.0-1
- Update to 2.2.0
- Add libglade dependency

* Tue Jan  7 2003 Alexander Larsson <alexl@redhat.com> 2.1.4-1
- Updated to 2.1.4

* Mon Nov 18 2002 Tim Powers <timp@redhat.com>
- rebuild for all arches

* Mon Aug 12 2002 Alexander Larsson <alexl@redhat.com>
- Remove the strange copyright on the start page. Fixes #69106

* Thu Aug  8 2002 Havoc Pennington <hp@redhat.com>
- 1.0.2
- include libexecdir stuff

* Sat Jul 27 2002 Havoc Pennington <hp@redhat.com>
- rebuild with new gail
- 1.0.1

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Jun 18 2002 Havoc Pennington <hp@redhat.com>
- put all the binaries in the file list... why is this package so hard?

* Mon Jun 17 2002 Havoc Pennington <hp@redhat.com>
- put images in file list, this thing will be non-ugly yet

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- 1.0
- use desktop-file-install to install/munge .desktop files
- put the sgml stuff in file list

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 0.10

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 0.8

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- 0.6.1

* Fri Apr 19 2002 Havoc Pennington <hp@redhat.com>
- 0.6

* Wed Jan 30 2002 Owen Taylor <otaylor@redhat.com>
- Rebuild for new gnome2 libraries

* Mon Jan 28 2002 Alex Larsson <alexl@redhat.com>
- Initial build.
