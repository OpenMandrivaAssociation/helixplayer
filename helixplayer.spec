%define name	helixplayer
%define version	1.0.9
%define release	%mkrel 1

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	A multimedia player
Source0:	https://helixcommunity.org/download.php/1950/hxplay-%version-source.tar.bz2
Source1:	HelixPlayer-buildrc
# imported from fedora
Patch0:		HelixPlayer-1.0.beta20040615-cvs-no-update.patch
Patch1:		HelixPlayer-1.0.3-disable-asm.patch
Patch2:		HelixPlayer-1.0.4-nptl.patch
Patch3:		HelixPlayer-1.0.5-missing-header.patch
Patch4:		HelixPlayer-1.0.7-ogg.patch
# imported from fedora
Patch5:		hxplay-1.0.9-desktop-file.patch
License:	GPL
Group:		Video
Url:		http://www.helixcommunity.org
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	libtheora-devel
BuildRequires:	libogg-devel
BuildRequires:	gtk+2-devel >= 2.2.0
BuildRequires:	libalsa-devel
BuildRequires: 	X11-devel
BuildRequires:  libvorbis-devel
BuildRequires:  python
BuildRequires:	desktop-file-utils
BuildRequires:	prelink
Requires:	helixplayer-codecs = %{version}
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description
The Helix Player is the Helix Community's open source media player for 
consumers. It is being developed to have a rich and usable graphical 
interface and support a variety of open media formats like Ogg Vorbis, 
Theora etc.

%package mozilla-plugin
Summary:	Mozilla plugin for %{name}
Group:		Networking/WWW
Requires:	%{name} == %{version}
Requires:	mozilla-firefox
%description mozilla-plugin
Mozilla plugin for %{name}.

%package helix-codecs
Summary:	Codecs pack for %{name}
Group:		Video
Requires:	%{name}
Provides:	helixplayer-codecs = %{version}
%description helix-codecs
Codecs pack for %{name}

%prep
%setup -q -n hxplay-%version
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p0
%patch5 -p0

%build
# Change hxplay_gtk_release to whatever string is in the Makefile
BUILDRC=%{SOURCE1} BUILD_ROOT="`pwd`/build" \
	PATH="$PATH:$$BUILD_ROOT/bin" \
	python build/bin/build.py -v -t release -k -y \
	%{_smp_mflags} -m hxplay_gtk_release \
	-p green -P helix-client-all-defines-free \
	player_all 

chmod -x build/*.txt

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p %{buildroot}/%{_bindir}

cat > %{buildroot}/%{_bindir}/hxplay <<EOF
#!/bin/sh
HELIX_LIBS=%{_libdir}/helix
export HELIX_LIBS
exec %{_bindir}/hxplay.bin "\$@"
EOF

install -p -m 755 release/hxplay.bin %{buildroot}/%{_bindir}/
chmod a+x %{buildroot}/%{_bindir}/*

mkdir -p %{buildroot}/%{_libdir}/helix/common
install -p -m 755 player/installer/archive/temp/common/*.so %{buildroot}/%{_libdir}/helix/common/
mkdir -p %{buildroot}/%{_libdir}/helix/plugins
install -p -m 755 player/installer/archive/temp/plugins/*.so %{buildroot}/%{_libdir}/helix/plugins/

mkdir -p %{buildroot}/%{_libdir}/helix
install -p -m 644 player/installer/archive/temp/LICENSE %{buildroot}/%{_libdir}/helix/
install -p -m 644 player/installer/archive/temp/README %{buildroot}/%{_libdir}/helix/
(cd %{buildroot}/%{_docdir}/%{name}-%{version} && ln -s %{_libdir/helix} .)

mkdir -p %{buildroot}/%{_libdir}/helix/codecs
install -p -m 755 player/installer/archive/temp/codecs/*.so %{buildroot}/%{_libdir}/helix/codecs/
mkdir -p %{buildroot}/%{_libdir}/mozilla/plugins
install -p -m 755 player/installer/archive/temp/mozilla/nphelix.so %{buildroot}/%{_libdir}/mozilla/plugins/
install -p -m 644 player/installer/archive/temp/mozilla/nphelix.xpt %{buildroot}/%{_libdir}/mozilla/plugins
mkdir -p %{buildroot}/%{_datadir}/application-registry/
install -p -m 644 player/installer/common/hxplay.applications %{buildroot}/%{_datadir}/application-registry/
# Desktop file
mkdir -p %{buildroot}/%{_datadir}/applications/
cp -p player/installer/common/hxplay.desktop player/installer/common/realplay.desktop
desktop-file-install  --vendor="" \
        --dir %{buildroot}%{_datadir}/applications \
        player/installer/common/hxplay.desktop

mkdir -p %{buildroot}/%{_datadir}/mime-info/
install -p -m 644 player/installer/common/hxplay.keys %{buildroot}/%{_datadir}/mime-info/
install -p -m 644 player/installer/common/hxplay.mime %{buildroot}/%{_datadir}/mime-info/

mkdir -p %{buildroot}/%{_libdir}/helix/share/hxplay
(cd %{buildroot}/%{_libdir}/helix/share/ && ln -s %{_datadir}/icons/hicolor/48x48/apps/hxplay.png .)
install -p -m 644 player/app/gtk/res/default/*.png %{buildroot}/%{_libdir}/helix/share/hxplay/
install -p -m 644 player/app/gtk/res/hxplay/*.png %{buildroot}/%{_libdir}/helix/share/hxplay/

for LANGUAGE in "de" "es" "fr" "it" "ja" "ko" "pt_BR" "zh_CN" "zh_TW"; do
	dir=%{buildroot}/%{_datadir}/locale/$LANGUAGE/LC_MESSAGES/
	mkdir -p $dir
	install -p -m 644 "player/installer/archive/temp/share/locale/$LANGUAGE/player.mo" "$dir/hxplay.mo"
	install -p -m 644 "player/installer/archive/temp/share/locale/$LANGUAGE/widget.mo" "$dir/libgtkhx.mo"
done

for SIZE in "16x16" "32x32" "48x48" "128x128" "192x192" ; do
	mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/$SIZE
	mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/$SIZE/apps
	mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/$SIZE/mimetypes

	ICON=player/app/gtk/res/icons/hxplay/hxplay_${SIZE}.png
	if [ -f "$ICON" ] ; then
		mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/${SIZE}/apps
		install -p -m 644 "$ICON" %{buildroot}/%{_datadir}/icons/hicolor/${SIZE}/apps/hxplay.png
	fi

	for MIME in \
		"application-ram"     \
		"application-rpm"     \
		"application-rm"      \
		"audio-ra"            \
		"video-rv" ; do

		ICON=player/app/gtk/res/icons/hxplay/mime-${MIME}_${SIZE}.png
		if [ -f "$ICON" ] ; then
			mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/${SIZE}/mimetypes
			install -p -m 644 "$ICON" %{buildroot}/%{_datadir}/icons/hicolor/${SIZE}/mimetypes/hxplay-${MIME}.png
		fi
	done
done

# Hack to get rid of executable stack on shared object files
execstack -c %{buildroot}/%{_libdir}/helix/codecs/colorcvt.so
execstack -c %{buildroot}/%{_libdir}/helix/codecs/cvt1.so
execstack -c %{buildroot}/%{_libdir}/helix/plugins/vidsite.so

chmod -x %{buildroot}/%{_datadir}/application-registry/hxplay.applications
chmod -x %{buildroot}/%{_datadir}/mime-info/hxplay.mime
chmod -x %{buildroot}/%{_libdir}/helix/LICENSE
chmod -x %{buildroot}/%{_datadir}/mime-info/hxplay.keys

%find_lang %{name} hxplay libgtkhx

%post
%{update_menus}
%{update_desktop_database}

%postun
%{clean_menus}
%{clean_desktop_database}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %name.lang
%defattr(-,root,root)
%doc build/*.txt
%{_bindir}/hxplay*
%{_libdir}/helix
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/mime-info/*
%{_datadir}/applications/*.desktop
%{_datadir}/application-registry/hxplay.applications
%exclude %{_libdir}/helix/common
%exclude %{_libdir}/helix/plugins
%exclude %{_libdir}/helix/codecs

# Mozilla plugin
%files mozilla-plugin
%defattr(-,root,root)
%{_libdir}/mozilla/plugins/*

# Codecs
%files helix-codecs
%defattr(-,root,root)
%{_libdir}/helix/common
%{_libdir}/helix/plugins
%{_libdir}/helix/codecs
