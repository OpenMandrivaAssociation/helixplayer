%define name	helixplayer
%define version	1.0.8
%define release	%mkrel 1

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	A multimedia player
Source0:	https://helixcommunity.org/download.php/1950/hxplay-%version-source.tar.bz2
Patch0:		helixplayer-1.0.5-fix-include.patch.bz2
# imported from fedora
Patch1:		HelixPlayer-1.0.3-disable-asm.patch.bz2
Patch2:		helixplayer-1.0.5-gcc4-detection-fix.patch.bz2
Patch3:		helixplayer-1.0.8-nptl.patch.bz2
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
%patch0
%patch1 -p1
%patch2
%patch3 -p0
%build
echo 'SetSDKPath("oggvorbissdk", "/usr")' > buildrc

export BUILD_ROOT=$PWD/build
export BUILDRC=$PWD/buildrc
export PATH="$BUILD_ROOT/bin;$PATH"
python $PWD/build/bin/build.py -m hxplay_gtk_release -P helix-client-all-defines-free  player_all

#%make

# for the %doc section.
cp ./player/installer/archive/temp/{README,LICENSE} ./

%install
rm -rf $RPM_BUILD_ROOT

# this build system leave the program in: 
# %buildroot/player/installer/archive/temp

# preparing directory structure
install -d -m 755 $RPM_BUILD_ROOT%{_bindir}
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/plugins
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/lib
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/default
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/hxplay
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/common
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/codecs
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/locale
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/locale

# Let's go !

# since all that we want to install is in this directory ...
pushd player/installer/archive/temp

# install and correct the .mo, populate the %name.lang with locale files
rm -f  ../../../../%name.lang
cd share/locale
for i in *; do \
( install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/locale/$i; \
  install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/locale/$i
  install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/locale/$i/LC_MESSAGES ; \
  install -m 644 $i/*.mo -D $RPM_BUILD_ROOT%{_datadir}/locale/$i/LC_MESSAGES ;\
  mv $RPM_BUILD_ROOT%{_datadir}/locale/$i/LC_MESSAGES/player.mo $RPM_BUILD_ROOT%{_datadir}/locale/$i/LC_MESSAGES/hxplay.mo ; \
  mv $RPM_BUILD_ROOT%{_datadir}/locale/$i/LC_MESSAGES/widget.mo $RPM_BUILD_ROOT%{_datadir}/locale/$i/LC_MESSAGES/libgtkhx.mo; \
  if [ -f $i/README ]; then \
	install -m 644 $i/README $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/locale/$i/README ; \
	echo "%{_libdir}/%{name}-%{version}/share/locale/$i/README" >> ../../../../../../%name.lang ; \
  fi; \
  if [ -f $i/LICENSE ]; then \
	install -m 644 $i/LICENSE $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/locale/$i/LICENSE ; \
	echo "%{_libdir}/%{name}-%{version}/share/locale/$i/LICENSE" >> ../../../../../../%name.lang ; \
  fi; \
  echo "%dir %{_libdir}/%{name}-%{version}/share/locale/$i" >> ../../../../../../%name.lang; )
done

cd ../..

# get locale
%find_lang hxplay
%find_lang libgtkhx
# add locale files to dir.
cat hxplay.lang libgtkhx.lang >> ../../../../%name.lang

# Set the HELIX_LIBS var in the script:

perl -pi -e 's|# HELIX_LIBS="/usr/local/HelixPlayer"|HELIX_LIBS=%{_libdir}/%{name}-%{version}|' hxplay

install -m755 {hxplay.bin,hxplay} -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}
install -m755 lib/libgtkhx.so -D  $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/lib/libgtkhx.so
install -m755 plugins/*.so -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/plugins
install -m755 common/*.so -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/common
install -m644 share/hxplay/*.png -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/hxplay
install -m644 share/default/*.png -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/share/default


# Create the link in %{_bindir} ( hxplay binary must be in his directory with 
# plugin and ressources
ln -s %{_libdir}/%{name}-%{version}/hxplay $RPM_BUILD_ROOT%{_bindir}/hxplay

# mozilla plugin
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins
install -m755 mozilla/* -D $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins

# codecs
install -m755 codecs/*.so -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/codecs
install -m755 plugins/*.so -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/plugins
install -m755 common/*.so -D $RPM_BUILD_ROOT%{_libdir}/%{name}-%{version}/common


# Menu icons
install -m644 share/icons/hxplay_16x16.png -D $RPM_BUILD_ROOT%{_miconsdir}/%{name}.png
install -m644 share/icons/hxplay_32x32.png -D $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
install -m644 share/icons/hxplay_48x48.png -D $RPM_BUILD_ROOT%{_liconsdir}/%{name}.png

popd

# menu entries
mkdir -p  $RPM_BUILD_ROOT%{_menudir}
cat << EOF > $RPM_BUILD_ROOT%{_menudir}/%{name}
?package(%{name}):command="/usr/bin/hxplay" \
icon="helixplayer.png" needs="X11"\
section="Multimedia/Video" startup_notify="false" \
title="HelixPlayer" longtitle="A multimedia player" \
mimetypes="application/x-ogg,application/ogg,text/vnd.rn-realtext,image/vnd.rn-realpix,application/smil,application/streamingmedia,application/sdp,video/3gpp,video/3gpp-encrypted,audio/3gpp,audio/3gpp-encrypted,audio/amr,audio/amr-encrypted,audio/amr-wb,audio/amr-wb-encrypted,audio/x-rn-3gpp-amr,audio/x-rn-3gpp-amr-encrypted,audio/x-rn-3gpp-amr-wb,audio/x-rn-3gpp-amr-wb-encrypted,video/3gpp2,audio/3gpp2" accept_url="true" \
multiple_files="true" xdg="true"
EOF

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=HelixPlayer
Comment=HelixPlayer multimedia player
Exec=%{_bindir}/hxplay %U
Icon=%{name}
Terminal=false
Type=Application
Categories=GTK;AudioVideo;Audio;Video;Player;X-MandrivaLinux-Multimedia-Video;
MimeType=application/x-ogg;application/ogg;audio/mp3;audio/x-mp3;audio/mpeg;audio/mpg;audio/x-mpeg;audio/x-mpg;audio/mpegurl;audio/x-mpegurl;audio/wav;audio/x-wav;audio/x-pn-wav;audio/x-pn-windows-acm;audio/x-pn-windowspcm;text/vnd.rn-realtext;application/vnd.rn-realmedia-secure;application/vnd.rn-realaudio-secure;audio/x-realaudio-secure;video/vnd.rn-realvideo-secure;audio/vnd.rn-realaudio;audio/x-realaudio;application/vnd.rn-realmedia;application/vnd.rn-realmedia-vbr;image/vnd.rn-realpix;audio/x-pn-realaudio;video/vnd.rn-realvideo;application/vnd.rn-realsystem-rmj;application/vnd.rn-realsystem-rmx;audio/aac;audio/x-aac;audio/m4a;audio/x-m4a;audio/mp2;audio/x-mp2;audio/mp1;audio/x-mp1;audio/rn-mpeg;audio/scpls;audio/x-scpls;application/smil;application/x-smil;application/streamingmedia;application/x-streamingmedia;application/sdp;audio/basic;audio/x-pn-au;audio/aiff;audio/x-aiff;audio/x-pn-aiff;video/3gpp;video/3gpp-encrypted;audio/3gpp;audio/3gpp-encrypted;audio/amr;audio/amr-encrypted;audio/amr-wb;audio/amr-wb-encrypted;audio/x-rn-3gpp-amr;audio/x-rn-3gpp-amr-encrypted;audio/x-rn-3gpp-amr-wb;audio/x-rn-3gpp-amr-wb-encrypted;video/3gpp2;audio/x-3gpp2
EOF


mkdir -p $RPM_BUILD_ROOT/%{_datadir}/mime-info/
cp player/installer/common/hxplay.keys $RPM_BUILD_ROOT/%{_datadir}/mime-info
cp player/installer/common/hxplay.mime $RPM_BUILD_ROOT/%{_datadir}/mime-info

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/application-registry/
cp player/installer/common/hxplay.applications $RPM_BUILD_ROOT/%{_datadir}/application-registry/


for SIZE in "16x16" "32x32" "48x48" "128x128" "192x192" ; do
    
    ICON=player/app/gtk/res/icons/hxplay/hxplay_${SIZE}.png
    if [ -f "$ICON" ] ; then
        mkdir -p $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/${SIZE}/apps
        cp "$ICON" $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/${SIZE}/apps/hxplay.png
    fi

    for MIME in \
        "application-ram"     \
        "application-rpm"     \
        "application-rm"      \
        "audio-ra"            \
        "video-rv" ; do
      ICON=player/app/gtk/res/icons/hxplay/mime-${MIME}_${SIZE}.png
      if [ -f "$ICON" ] ; then
          mkdir -p $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/${SIZE}/mimetypes
          cp "$ICON" $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/${SIZE}/mimetypes/hxplay-${MIME}.png
      fi
    done
done

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
%doc README LICENSE

%dir %{_libdir}/%{name}-%{version}
%dir %{_libdir}/%{name}-%{version}/share
%dir %{_libdir}/%{name}-%{version}/lib
%dir %{_libdir}/%{name}-%{version}/common
%dir %{_libdir}/%{name}-%{version}/plugins
%dir %{_libdir}/%{name}-%{version}/codecs
%dir %{_libdir}/%{name}-%{version}/share/default
%dir %{_libdir}/%{name}-%{version}/share/hxplay
%dir %{_libdir}/%{name}-%{version}/share/locale

%{_libdir}/%{name}-%{version}/hxplay
%{_libdir}/%{name}-%{version}/hxplay.bin
%{_libdir}/%{name}-%{version}/share/default/*
%{_libdir}/%{name}-%{version}/share/hxplay/*
%{_libdir}/%{name}-%{version}/lib/*
%{_bindir}/hxplay

#menu stuff
%{_menudir}/%{name}
%{_miconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
%{_datadir}/mime-info/*
%{_datadir}/application-registry/*
%{_datadir}/icons/hicolor/*/*/*.png


# Mozilla plugin
%files mozilla-plugin
%defattr(-,root,root)
%{_libdir}/mozilla/plugins/*

# Codecs
%files helix-codecs
%defattr(-,root,root)
%{_libdir}/%{name}-%{version}/common/*
%{_libdir}/%{name}-%{version}/plugins/*
%{_libdir}/%{name}-%{version}/codecs/*
