%global debug_package %{nil}
%global __os_install_post %{nil}
%global _python_bytecompile_errors_terminate_build 0

%define full_version 16.2.1
%define major_version 16

Name:           davinci-resolve%{major_version}
Version:        %{full_version}
Release:        1%{?dist}
Summary:        Davinci Resolve %{major_version}
License:        Proprietary
Source0:        https://minio.infra.local:9000/rpm-sources/davinci-resolve/DaVinci_Resolve_%{version}_Linux.zip
ExclusiveArch:  x86_64
AutoReqProv:    no
BuildRequires:  sed
BuildRequires:  unzip
BuildRequires:  desktop-file-utils
BuildRequires:  xorriso
Requires:       desktop-file-utils

%description
DaVinci Resolve %{major_version} is the world’s only solution that combines
professional 8K editing, color correction, visual effects and audio post
production all in one software tool

%prep
%setup -q -T -c %{name}-%{version}
unzip %{SOURCE0}
mv *Resolve*.run resolve.run
xorriso -osirrox on -indev resolve.run -extract / ./resolve
sed -i "s|RESOLVE_INSTALL_LOCATION|/opt/%{name}|g" resolve/share/*.desktop
sed -i "s|\(.*Name.*=.*\)|\1 %{major_version}|g" resolve/share/*.desktop

%build

%install
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/opt/%{name}/Fairlight
mkdir -p %{buildroot}/opt/%{name}/easyDCP
mkdir -p %{buildroot}/opt/%{name}/.license
mkdir -p %{buildroot}/var/log/%{name}
cp resolve/share/blackmagicraw-player.desktop %{buildroot}/usr/share/applications/
cp resolve/share/blackmagicraw-speedtest.desktop %{buildroot}/usr/share/applications/
cp resolve/share/DaVinciResolveCaptureLogs.desktop %{buildroot}/usr/share/applications/
cp resolve/share/DaVinciResolve.desktop %{buildroot}/usr/share/applications/
cp resolve/share/DaVinciResolvePanelSetup.desktop %{buildroot}/usr/share/applications/
mv resolve/* %{buildroot}/opt/%{name}/
ln -s /var/log/%{name} %{buildroot}/opt/%{name}/logs
/usr/bin/desktop-file-validate %{buildroot}/usr/share/applications/*.desktop

%post
/usr/bin/update-desktop-database

%files
%defattr(-, root, root, -)
%dir /opt/%{name}
%dir /var/log/%{name}
%attr(775, root, users) /var/log/%{name}
%attr(775, root, users) /opt/%{name}/.license
%attr(775, root, users) /opt/%{name}/easyDCP
%attr(775, root, users) /opt/%{name}/Fairlight
%attr(775, root, users) /opt/%{name}/LUT
/usr/share/applications/*.desktop
/opt/%{name}/*

