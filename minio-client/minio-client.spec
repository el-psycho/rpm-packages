%global debug_package %{nil}
%global __os_install_post %{nil}

Name:           minio-client
Version:        2020.04.25T00.43.23Z
Release:        1%{?dist}
Summary:        MinIO CLI client
License:        Apache-2.0
Source0:        https://dl.min.io/client/mc/release/linux-amd64/mc.RELEASE.2020-04-25T00-43-23Z
ExclusiveArch:  x86_64
AutoReqProv:    no

%description
The MinIO CLI client

%prep
%setup -q -T -c %{name}-%{version}
cp %{SOURCE0} ./mc
chmod +x mc

%build

%install
mkdir -p %{buildroot}/usr/local/bin
mv mc %{buildroot}/usr/local/bin/

%files
%attr(755, root, root) /usr/local/bin/mc

