#define _legacy_common_support 1

Name:           smplayer
Version:        22.2.0
%global smtube_ver  21.10.0
%global smplayer_themes_ver 18.6.0
%global smplayer_skins_ver 15.2.0
Release:        7%{?dist}
Summary:        A graphical frontend for mplayer

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://smplayer.sourceforge.net/
Source0:        http://downloads.sourceforge.net/smplayer/smplayer-%{version}.tar.bz2
Source2:        https://sourceforge.net/projects/smtube/files/SMTube/%{smtube_ver}/smtube-%{smtube_ver}.tar.bz2
Source3:        https://sourceforge.net/projects/smplayer/files/SMPlayer-themes/%{smplayer_themes_ver}/smplayer-themes-%{smplayer_themes_ver}.tar.bz2
Source4:        http://downloads.sourceforge.net/smplayer/smplayer-skins-%{smplayer_skins_ver}.tar.bz2
# Fix regression in Thunar (TODO: re-check in upcoming versions!)
# https://bugzilla.rpmfusion.org/show_bug.cgi?id=1217
Patch0:         smplayer-21.8.0-desktop-files.patch
Patch2:         smplayer-14.9.0.6966-system-qtsingleapplication.patch
Patch3:         smtube-19.1.0-system-qtsingleapplication.patch
Patch4:         smplayer-18.2.0-jobserver.patch
Patch5:         smplayer-18.3.0-disable-werror.patch

BuildRequires:  desktop-file-utils
BuildRequires:	qt5-qtbase-private-devel
BuildRequires:  pkgconfig(Qt5)
BuildRequires:  pkgconfig(Qt5Concurrent)
BuildRequires:  pkgconfig(Qt5Core)
BuildRequires:  pkgconfig(Qt5DBus)
BuildRequires:  pkgconfig(Qt5Gui)
BuildRequires:  pkgconfig(Qt5Network)
BuildRequires:  pkgconfig(Qt5PrintSupport)
BuildRequires:  pkgconfig(Qt5Script)
BuildRequires:  pkgconfig(Qt5WebKitWidgets)
BuildRequires:  pkgconfig(Qt5Sql)
BuildRequires:  pkgconfig(Qt5Widgets)
BuildRequires:  pkgconfig(Qt5Xml)
BuildRequires:  pkgconfig(Qt5Designer)
BuildRequires:  pkgconfig(zlib)
BuildRequires:	pkgconfig(xext)
BuildRequires:  qt5-linguist
BuildRequires:  qtsingleapplication-qt5-devel
BuildRequires:  quazip-qt5-devel
# for smtube only
BuildRequires:  pkgconfig(Qt5WebKit)
# smplayer without mplayer is quite useless
Requires:       mplayer-backend
Requires:       hicolor-icon-theme
Recommends:     smtube

%{?_qt5_version:Requires: qt5-qtbase%{?_isa} >= %{_qt5_version}}

Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description
smplayer intends to be a complete front-end for Mplayer, from basic features
like playing videos, DVDs, and VCDs to more advanced features like support
for Mplayer filters and more. One of the main features is the ability to
remember the state of a played file, so when you play it later it will resume
at the same point and with the same settings. smplayer is developed with
the Qt toolkit, so it's multi-platform.

%package -n smtube
Summary: YouTube browser for SMPlayer
Group: Applications/Multimedia
License: GPLv2+
URL: http://www.smtube.org
Recommends:  smplayer

%description -n smtube
This is a YouTube browser for SMPlayer. You can browse, search
and play YouTube videos.

%package themes
Summary:  Themes and Skins for SMPlayer
Group:    Video/Players
Requires: smplayer

%description themes
A set of themes for SMPlayer and a set of skins for SMPlayer.

%prep
%setup -qa2 -qa3 -qa4 -qn %{name}-%{version}
%patch4 -p1
%patch5 -p1

#remove some bundle sources
rm -rf zlib
rm -rf src/qtsingleapplication/
rm -rf smtube-%{smtube_ver}/src/qtsingleapplication/
#TODO unbundle libmaia
#rm -rf src/findsubtitles/libmaia

# Turn off online update checker
sed -e 's:DEFINES += UPDATE_CHECKER:#&:' \
 -e 's:DEFINES += CHECK_UPGRADED:#&:' \
 -i src/smplayer.pro

# Turn off intrusive share widget
sed -e 's:DEFINES += SHARE_WIDGET:#&:' \
 -i src/smplayer.pro

%patch0 -p1
%patch2 -p1 -b .qtsingleapplication
pushd smtube-%{smtube_ver}
#patch3 -p1 -b .qtsingleapplication
# correction for wrong-file-end-of-line-encoding on smtube
%{__sed} -i 's/\r//' *.txt
popd

# correction for wrong-file-end-of-line-encoding
%{__sed} -i 's/\r//' *.txt

# change rcc binary
%{__sed} -e 's/rcc -binary/rcc-qt5 -binary/' -i smplayer-themes-%{smplayer_themes_ver}/themes/Makefile
%{__sed} -e 's/rcc -binary/rcc-qt5 -binary/' -i smplayer-skins-%{smplayer_skins_ver}/themes/Makefile

%build
pushd src
    %{qmake_qt5}
    %make_build DATA_PATH=\\\"%{_datadir}/%{name}\\\" \
        TRANSLATION_PATH=\\\"%{_datadir}/%{name}/translations\\\" \
        DOC_PATH=\\\"%{_docdir}/%{name}\\\" \
        THEMES_PATH=\\\"%{_datadir}/%{name}/themes\\\" \
        SHORTCUTS_PATH=\\\"%{_datadir}/%{name}/shortcuts\\\"
        QMAKE_OPTS=DEFINES+=NO_DEBUG_ON_CONSOLE \
    %{_bindir}/lrelease-qt5 %{name}.pro
popd

pushd smtube-%{smtube_ver}/src
    %{qmake_qt5}
    %make_build TRANSLATION_PATH=\\\"%{_datadir}/smtube/translations\\\"
    QMAKE_OPTS=DEFINES+=NO_DEBUG_ON_CONSOLE \
    %{_bindir}/lrelease-qt5 smtube.pro
popd

pushd smplayer-themes-%{smplayer_themes_ver}
    %make_build V=0
popd

pushd smplayer-skins-%{smplayer_skins_ver}
    mv README.txt README-skins.txt
    mv Changelog Changelog-skins.txt
    %make_build V=0
popd

pushd webserver
export CFLAGS_EXTRA="%{__global_compiler_flags}"
%make_build
popd

%install
%make_install PREFIX=%{_prefix} DOC_PATH=%{_docdir}/%{name}

# License docs go to another place
rm -r %{buildroot}%{_docdir}/%{name}/Copying*

pushd smtube-%{smtube_ver}
    %make_install PREFIX=%{_prefix} DOC_PATH=%{_docdir}/%{name}/smtube
popd

pushd smplayer-themes-%{smplayer_themes_ver}
    %make_install PREFIX=%{_prefix}
popd

pushd smplayer-skins-%{smplayer_skins_ver}
    %make_install PREFIX=%{_prefix}
popd

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%post
/usr/bin/update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%license Copying*
%{_bindir}/smplayer
%{_bindir}/simple_web_server
%{_datadir}/applications/smplayer*.desktop
%{_datadir}/icons/hicolor/*/apps/smplayer.png
%{_datadir}/icons/hicolor/*/apps/smplayer.svg
%{_datadir}/smplayer
%exclude %{_datadir}/smplayer/themes/
%{_mandir}/man1/%{name}.1.*
%{_docdir}/%{name}
%{_datadir}/metainfo/*.appdata.xml

%files -n smtube
%doc smtube-%{smtube_ver}/Readme.txt
%license smtube-%{smtube_ver}/Copying.txt
%{_bindir}/smtube
%{_datadir}/applications/smtube.desktop
%{_datadir}/icons/hicolor/*/apps/smtube.png
%{_datadir}/smtube

%files themes
%doc smplayer-themes-%{smplayer_themes_ver}/README.txt
%doc smplayer-themes-%{smplayer_themes_ver}/Changelog
%doc smplayer-skins-%{smplayer_skins_ver}/README-skins.txt
%doc smplayer-skins-%{smplayer_skins_ver}/Changelog-skins.txt
%license smplayer-themes-%{smplayer_themes_ver}/COPYING*
%{_datadir}/smplayer/themes/

%changelog

* Tue Mar 01 2022 Unitedrpms Project <unitedrpms AT protonmail DOT com> 22.2.0-7  
- Updated to 22.2.0

* Fri Nov 05 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 21.10.0-7  
- Updated to 21.10.0

* Mon Aug 23 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 21.8.0-7  
- Updated to 21.8.0

* Mon Jan 11 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> 21.1.0-7  
- Updated to 21.1.0

* Fri Jul 03 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 20.6.0-7  
- Updated to 20.6.0

* Thu Apr 23 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 20.4.2-8  
- Rebuilt

* Wed Apr 15 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 20.4.2-7  
- Updated to 20.4.2

* Sat Apr 11 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 20.4.0-7  
- Updated to 20.4.0

* Wed Nov 13 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 19.10.2-7  
- Updated to 19.10.2

* Tue Oct 29 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 19.10.0-1  
- Updated to 19.10.0

* Thu May 16 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 19.5.0-1  
- Updated to 19.5.0

* Tue Jan 29 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 19.1.0-1  
- Updated to 19.1.0

* Mon Oct 22 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.10.0-1  
- Updated to 18.10.0

* Sun Sep 16 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.9.0-1  
- Updated to 18.9.0

* Sat Jun 23 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.6.0-1  
- Updated to 18.6.0

* Thu May 24 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.5.0-1  
- Updated to 18.5.0

* Mon Apr 23 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.4.0-1  
- Updated to 18.4.0

* Wed Mar 21 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.3.0-1  
- Updated to 18.3.0

* Sun Feb 18 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.2.2-1  
- Updated to 18.2.2

* Wed Jan 24 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.2.0-1  
- Updated to 18.2.0

* Wed Jan 10 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 18.1.0-1  
- Updated to 18.1.0

* Thu Nov 16 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.11.2-1  
- Updated to 17.11.2

* Sun Nov 05 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.11.0-1  
- Updated to 17.11.0

* Sat Oct 21 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.10.2-1  
- Updated to 17.10.2

* Sat Sep 30 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.10.0-1  
- Updated to 17.10.0

* Sun Sep 03 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.9.0-1  
- Updated to 17.9.0

* Thu Aug 24 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.8.0-1  
- Updated to 17.8.0
- Turn off online update checker
- Turn off intrusive share widget

* Thu Jul 06 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.7.0-1  
- Updated to 17.7.0

* Wed May 31 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 17.6.0-1  
- Updated to 17.6.0

* Fri Nov 25 2016 Pavlo Rudyi <paulcarroty at riseup.net> - 17.3.0-1
- Update to 17.3

* Mon Sep 12 2016 Pavlo Rudyi <paulcarroty at riseup.net> - 16.9.0-1
- Update to 16.9

* Fri Aug 05 2016 Pavlo Rudyi <paulcarroty at riseup.net> - 16.8.0-1
- Update to 16.8  

* Sat Jul 23 2016 Sérgio Basto <sergio@serjux.com> - 16.7.0-3
- Package scriplets review, based on RussianFedora work
  https://github.com/RussianFedora/smplayer

* Tue Jul 19 2016 Sérgio Basto <sergio@serjux.com> - 16.7.0-2
- Add patch to fix build in rawhide

* Sun Jul 17 2016 Sérgio Basto <sergio@serjux.com> - 16.7.0-1
- Update smplayer to 16.7.0 and smtube to 16.7.2
- Install smplayer-themes and smplayer-skins
- Few more cleanup, especially in docs and licenses.

* Sun Jul 17 2016 Sérgio Basto <sergio@serjux.com> - 16.6.0-2
- Switch builds to Qt5
- Do not apply a vendor tag to .desktop files (using --vendor).
- Drop old smplayer_enqueue.desktop

* Wed Jun 22 2016 Sérgio Basto <sergio@serjux.com> - 16.6.0-1
- Update to 16.6.0

* Fri Apr 01 2016 Sérgio Basto <sergio@serjux.com> - 16.4.0-1
- Update to 16.4.0

* Sun Jan 17 2016 Sérgio Basto <sergio@serjux.com> - 16.1.0-1
- Update 16.1.0

* Sun Dec 06 2015 Sérgio Basto <sergio@serjux.com> - 15.11.0-1
- Update smplayer and smtube 15.11.0

* Fri Oct 02 2015 Sérgio Basto <sergio@serjux.com> - 15.9.0-1
- Update smplayer to 15.9.0 and smtube to 15.9.0 .

* Thu Aug 20 2015 Sérgio Basto <sergio@serjux.com> - 14.9.0.6994-2
- Update smtube to 15.8.0 .
- Removed version of package from _docdir directory (following the guidelines).

* Wed Jun 17 2015 Sérgio Basto <sergio@serjux.com> - 14.9.0.6994-1
- Update to 4.9.0.6994 .
- Drop smplayer-14.9.0-get_svn_revision.patch .

* Mon Jun 08 2015 Sérgio Basto <sergio@serjux.com> - 14.9.0.6966-3
- Added smplayer-14.9.0-get_svn_revision.patch, I think is better have a
  hardcore version than (svn r0UNKNOWN)

* Sun Jun 07 2015 Sérgio Basto <sergio@serjux.com> - 14.9.0.6966-2
- Update to smtube-15.5.17

* Sat Jun 06 2015 Sérgio Basto <sergio@serjux.com> - 14.9.0.6966-1
- Update to smplayer-14.9.0.6966 and smtube-15.5.10
- Fix warning "The desktop entry file "ServiceMenus/smplayer_enqueue.desktop
  has an empty mimetype! " .
- Rebase patches 2 and 3 .

* Wed Mar 25 2015 Sérgio Basto <sergio@serjux.com> - 14.9.0.6690-1
- Update smplayer to smplayer-14.9.0.6690 and smtube to smtube-15.1.26

* Mon Sep 15 2014 Sérgio Basto <sergio@serjux.com> - 14.9.0-1
- New upstream releases smplayer 14.9.0 and smtube 14.8.0
- Rebase patches 1 and 3 .

* Mon Sep 01 2014 Sérgio Basto <sergio@serjux.com> - 14.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Apr 04 2014 Sérgio Basto <sergio@serjux.com> - 14.3.0-1
- New upstream release, Previous version was 0.8.6, this new release is 14.3...
  What happened? Now the version is just the year and month of the release.
- Patches refactor.

* Tue Oct 01 2013 Sérgio Basto <sergio@serjux.com> - 0.8.6-1
- Update smplayer to 0.8.6 and smtube to 1.8

* Mon May 27 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.8.5-2
- Rebuilt for x264/FFmpeg

* Sat May 11 2013 Sérgio Basto <sergio@serjux.com> - 0.8.5-1
- Update smplayer to 0.8.5 and smtube to 1.7
- Fix patches smplayer-0.8.3-smtube-system-qtsingleapplication and
  smplayer-0.8.1-system-qtsingleapplication.patch for 0.8.5 and smtube 1.7

* Mon Mar 25 2013 Sérgio Basto <sergio@serjux.com> - 0.8.4-2
- New tag 

* Mon Mar 25 2013 Sérgio Basto <sergio@serjux.com> - 0.8.4-1
- New upsteam release.
- Drop "updates *.desktop with video/webm;" on patch smplayer-0.8.3-desktop-files.patch.
- Fix patch smplayer-0.8.3-smtube-system-qtsingleapplication.patch 
- Fix dates on changelog specs.

* Thu Jan 10 2013 Sérgio Basto <sergio@serjux.com> - 0.8.3-2
- bug #2635, Update *.desktop with video/webm; mimetype support, as upstream do in svn r5005.

* Mon Dec 24 2012 Sérgio Basto <sergio@serjux.com> - 0.8.3-1
- New updates to smplayer-0.8.3 and smtube-1.5 . Fix for Youtube playback.

* Mon Dec 17 2012 Sérgio Basto <sergio@serjux.com> - 0.8.2.1-1
- New updates to smplayer-0.8.2.1 and smtube-1.4 .

* Sun Nov 25 2012 Sérgio Basto <sergio@serjux.com> - 0.8.2-3
- now smtube new source b372bd396c068aa28798bf2b5385bf59  smtube-1.3.tar.bz2 .

* Sun Nov 25 2012 Sérgio Basto <sergio@serjux.com> - 0.8.2-2
- 0.8.2 new source 0dee3f9a4f0d87d37455efc800f9bba7 smplayer-0.8.2.tar.bz2 this one has some minor
  fixes ... , smplayer-0.8.2.tar.bz2 was announced at 2012-11-24. 

* Thu Nov 22 2012 Sérgio Basto <sergio@serjux.com> - 0.8.2-1
- New upsteam release.

* Thu Sep 27 2012 Sérgio Basto <sergio@serjux.com> - 0.8.1-2
- fix rfbz #2488

* Thu Sep 20 2012 Sérgio Basto <sergio@serjux.com> - 0.8.1-1
- New upsteam release.
- rfbz #2113, all done by Nucleo.

* Sat Apr 28 2012 Sérgio Basto <sergio@serjux.com> - 0.8.0-2
- fix smtube translations.
- drop support for Fedora < 9 and EPEL 5, since we need kde4.

* Sat Apr 28 2012 Sérgio Basto <sergio@serjux.com> - 0.8.0-1 
- New release
- add smtube support
- use system qtsingleapplication
- a little review with: fedora-review -n smplayer --mock-config fedora-16-i386

* Sat Mar 24 2012 Sérgio Basto <sergio@serjux.com> - 0.7.1-1
- New upstream version: 0.7.1, changelog says "This version includes some bug fixes, 
  some of them important. It's highly recommended to update." 
- Remove some bundle sources.
- Small fixes in patches to fit on 0.7.1.

* Sat Mar 24 2012 Sérgio Basto <sergio@serjux.com> - 0.7.0-3
- Add a patch to remove bundled quazip shlibs and Requires kde-filesystem, bug rfbz #1164
- Removed tag BuildRoot.

* Fri Mar 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.7.0-2
- Rebuilt for c++ ABI breakage

* Tue Feb 7 2012 Sérgio Basto <sergio@serjux.com> - 0.7.0-1
- new upstream version: 0.7.0

* Mon May 24 2010 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.9-2
- #1217: fix regression in Thunar

* Sat Apr 24 2010 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.9-1
- new upstream version: 0.6.9

* Sun Jun 28 2009 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.8-1
- new upstream version: 0.6.8

* Sun Mar 29 2009 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.7-1
- new upstream version: 0.6.7

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.6.6-2
- rebuild for new F11 features

* Sat Jan 10 2009 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.6-1
- new upstream version: 0.6.6

* Thu Nov 13 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.5.1-1
- new upstream version: 0.6.5.1

* Wed Oct 29 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.4-1
- new upstream version: 0.6.4

* Mon Sep 29 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.3-1
- new upstream version: 0.6.3

* Fri Aug 15 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.2-1
- new upstream version: 0.6.2
- add servicemenus depending on the KDE version

* Wed Jul 30 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.6.1-4
- rebuild for buildsys cflags issue

* Tue Jul 22 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.1-3
- import into rpmfusion

* Tue Jul 08 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.1-2
- fix packaging of FAQs

* Tue Jun 17 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.1-1
- update to latest upstream version

* Sun Feb 24 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.0-0.3.rc2
- add %%{?_smp_mflags} in Makefile to really use it
- finally fix usage of macros
- mode 0644 for desktop-file isn't needed anymore

* Sat Feb 23 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.0-0.2.rc2
- Update %%post and %%postun scriplets
- use %%{?_smp_mflags} in make
- change vendor to rpmfusion in desktop-file-install
- some minor spec cleanups

* Thu Feb 14 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.0-0.1.rc2
- new upstream version: 0.6.0rc2

* Tue Feb 12 2008 Sebastian Vahl <fedora@deadbabylon.de> - 0.6.0-0.1.rc1
- new upstream version: 0.6.0rc1
- added docs: Changelog Copying.txt Readme.txt Release_notes.txt
- fix path of %%docdir in Makefile

* Tue Dec 18 2007 Sebastian Vahl <fedora@deadbabylon.de> - 0.5.62-1
- new version: 0.5.62
- specify license as GPLv2+

* Thu Sep 20 2007 Sebastian Vahl <fedora@deadbabylon.de> - 0.5.60-1
- Update to development version of qt4

* Thu Sep 20 2007 Sebastian Vahl <fedora@deadbabylon.de> - 0.5.21-1
- new upstream version: 0.5.21
- don't add category "Multimedia" to desktop-file
- correct url of Source0

* Sun Jul 29 2007 Sebastian Vahl <fedora@deadbabylon.de> - 0.5.20-1
- new upstream version: 0.5.20

* Mon Jun 18 2007 Sebastian Vahl <fedora@deadbabylon.de> - 0.5.14-1
- new upstream version: 0.5.14

* Thu Jun 14 2007 Sebastian Vahl <fedora@deadbabylon.de> - 0.5.7-1
- Initial Release
