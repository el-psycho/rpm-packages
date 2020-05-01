%global debug_package %{nil}

Name:           helm3
Version:        3.0.3
Release:        1%{?dist}
Summary:        The Kubernetes Package Manager
License:        Apache 2.0
Source0:        https://get.helm.sh/helm-v%{version}-linux-amd64.tar.gz
ExclusiveArch:  x86_64
Provides:       helm3 = %{version}
AutoReqProv:    no

%description
Helm is a tool for managing Kubernetes charts.
Charts are packages of pre-configured Kubernetes resources.

%prep
%setup -q -T -c helm-%{version}
tar -xf "%{SOURCE0}" -C ./
mv linux-amd64/helm ./helm3
chmod +x helm3
./helm3 completion bash > helm3_completion.sh

%build

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/etc/profile.d
cp helm3 %{buildroot}/usr/bin/
cp helm3_completion.sh %{buildroot}/etc/profile.d/


%files
%attr(0755, root, root) /usr/bin/helm3
%attr(0644, root, root) /etc/profile.d/helm3_completion.sh

