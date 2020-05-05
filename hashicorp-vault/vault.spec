%global debug_package %{nil}

Name:          vault
Version:       1.4.1
Release:       1%{?dist}
Summary:       HashiCorp Vault
License:       Mozilla Public License 2.0
Source0:       https://releases.hashicorp.com/vault/%{version}/vault_%{version}_linux_amd64.zip
ExclusiveArch: x86_64
AutoReqProv:   no
BuildRequires: unzip

%description
Vault secures, stores, and tightly controls access to tokens, passwords,
certificates, API keys, and other secrets in modern computing.

%prep
%setup -q -T -c vault-%{version}
unzip "%{SOURCE0}"
chmod +x vault

%build

%install
mkdir -p %{buildroot}/usr/local/bin
cp vault %{buildroot}/usr/local/bin/

%files
%attr(0755, root, root) /usr/local/bin/vault

