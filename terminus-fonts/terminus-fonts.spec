%global fontname terminus
%global origname %{fontname}-fonts
%global fontconf 63-%{fontname}.conf

%global archivename terminus-font-%{version}


# This is the directory where we install our console fonts.
# Owned by the kbd package, which hardcodes it as /lib/kbd (without macros).
%global consolefontdir /lib/kbd/consolefonts


# The ExcludeArch from the grub2.spec file
#
# There might be a better way to detect whether this platform has
# grub2 available, but this should do the job at least for the time
# being.
%if 0%{?fedora} >= 29
%global grub2_exclude_arches s390 s390x
%else
%global grub2_exclude_arches s390 s390x %{arm}
%endif

# Owned by the grub2-common package
%global grub2fontdir   /usr/share/grub


# Font catalog
%global catalog %{_sysconfdir}/X11/fontpath.d


%global common_desc \
The Terminus Font is a clean, fixed with bitmap font designed for long\
(8 and more hours per day) work with computers.\
\
I contains more than 1300 characters, covers about 120 language sets and\
supports ISO8859-1/2/5/7/9/13/15/16, Paratype-PT154/PT254, KOI8-R/U/E/F,\
Esperanto, and many IBM, Windows and Macintosh code pages, as well as\
the IBM VGA, vt100 and xterm pseudo graphic characters.\
\
The sizes present are 6x12, 8x14, 8x16, 10x18, 10x20, 11x22, 12x24,\
14x28, and 16x32. The weights are normal and bold (except for 6x12),\
plus CRT VGA-bold for 8x14 and 8x16.


%if %{?epoch: 1}%{?!epoch: 0}
%global evr %{epoch}:%{version}-%{release}
%else
%global evr %{version}-%{release}
%endif

Name:		%{origname}-td1
Version:	4.48
Release:	5%{?dist}
Summary:	Clean fixed width font

# The source package also contains a few GPLv2+ build helper scripts.
License:	OFL
URL:		http://terminus-font.sourceforge.net/
Source0:	http://downloads.sourceforge.net/terminus-font/%{archivename}.tar.gz
Source1:	%{origname}-fontconfig.conf
Source2:	bitmapfonts2otb.py
Source10:	%{origname}-console.README.fedora
Source20:	%{origname}.README.fedora
Source21:	%{origname}.Xresources.example

Patch42:	terminus-font-opentype-bitmap-via-fonttosfnt.patch

BuildArch:	noarch
BuildRequires:	fontpackages-devel >= 1.18
Requires:	fontpackages-filesystem

Obsoletes:	%{origname}-x11 <= %{evr}
Provides:	%{name}-x11 = %{evr}
Obsoletes:	%{origname} <= %{evr}
Provides:	%{name} = %{evr}

# For generating *.otb (OpenType bitmap font)
BuildRequires:	/usr/bin/ftdump
BuildRequires:	/usr/bin/fonttosfnt
BuildRequires:	python3

BuildRequires:	python3 >= 3.5.0
BuildRequires:	/usr/bin/bdftopcf
BuildRequires:	/usr/bin/mkfontdir

%ifnarch %{grub2_exclude_arches}
BuildRequires:	/usr/bin/grub2-mkfont
%endif

%description
%common_desc

This package contains the OpenType bitmap fonts to use with
X11 and Wayland on Fedora 31 and later, and also the legacy
X11 PCF bitmap fonts for compatibility with older software.


%package console
Requires:	kbd
Summary:	Clean fixed width font (console version)
Obsoletes:	%{origname}-console <= %{evr}
Provides:	%{name}-console = %{evr}
License:	OFL

%description console
%common_desc

This package contains the fonts to use with the Linux console.


%ifnarch %{grub2_exclude_arches}
%package grub2
Requires:	grub2-common
Summary:	Clean fixed width font (grub2 version)
Obsoletes:	%{origname}-grub2 <= %{evr}
Provides:	%{name}-grub2 = %{evr}
License:	OFL

%description grub2
%common_desc

This package contains the fonts to use with the grub2 boot loader.
%endif


%prep
%setup -q -n %{archivename}
cp -p "%{SOURCE2}" ./bin
%patch42 -p1 -b .opentype-bitmap-via-fonttosfnt
patch -s -p1 -b --suffix .dv1 -fuzz=0 -i alt/dv1.diff
patch -s -p1 -b --suffix .ij1 -fuzz=0 -i alt/ij1.diff

# Applies "centered" tilde patch
patch -s -p1 -b --suffix .td1 -fuzz=0 -i alt/td1.diff

chmod 755 configure
iconv -f WINDOWS-1251 -t utf-8 -o README-BG README-BG

%build
# The libdir is just to shut up rpmlint. Configure is nice enough to
# just ignore it.
./configure --prefix=%{_prefix} --libdir=%{_libdir} \
	--x11dir=%{_fontdir} --psfdir=%{consolefontdir}
env GZIP=--best make %{?_smp_mflags} PCF='$(PCF_10646_1) $(PCF_8BIT)' pcf psf psf-vgaw otb

%ifnarch %{grub2_exclude_arches}
# generate *.pf2 for the grub2 bootloader
for bdf in ter-*[bn].bdf; do
  /usr/bin/grub2-mkfont -o "$(basename "$bdf" .bdf).pf2" "$bdf"
done
%endif

# Fedora specific docs and examples
mkdir -p docs/console docs/x11
cp -p "%{SOURCE10}" docs/console/README.fedora
cp -p "%{SOURCE20}" docs/x11/README.fedora
cp -p "%{SOURCE21}" docs/x11/Xresources.example


%install
make DESTDIR="%{buildroot}" PCF='$(PCF_10646_1) $(PCF_8BIT)' install-psf install-psf-ref install-psf-vgaw install-pcf install-otb

%ifnarch %{grub2_exclude_arches}
# install *.pf2 for the grub2 bootloader
install -m 0755 -d %{buildroot}%{grub2fontdir}
install -m 0644 -t %{buildroot}%{grub2fontdir} ter-*.pf2
%endif

# hook the OTB and legacy PCF fonts into fontconfig
install -m 0755 -d \
	%{buildroot}%{_fontconfig_templatedir} \
	%{buildroot}%{_fontconfig_confdir}

install -m 0644 -p %{SOURCE1} \
	%{buildroot}%{_fontconfig_templatedir}/%{fontconf}
ln -s \
	%{_fontconfig_templatedir}/%{fontconf} \
	%{buildroot}%{_fontconfig_confdir}/%{fontconf}

# We cannot run mkfontdir in %%post because %%post is generated by %%_font_pkg
install -m 0755 -d %{buildroot}%{catalog}
ln -s %{_fontdir} %{buildroot}%{catalog}/%{fontname}:unscaled
/usr/bin/mkfontdir %{buildroot}%{_fontdir}


%_font_pkg -f %{fontconf} ter-*.pcf.gz Terminus.otb Terminus-Bold.otb
%doc README
%doc README-BG
%doc docs/x11/README.fedora
%doc docs/x11/Xresources.example
%{catalog}/%{fontname}:unscaled
%{_fontdir}/fonts.dir


%files console
%doc README
%doc README-BG
%doc docs/console/README.fedora
%doc %{consolefontdir}/README.terminus
# VGAW fonts
%{consolefontdir}/ter-114v.psf.gz
%{consolefontdir}/ter-116v.psf.gz
%{consolefontdir}/ter-214v.psf.gz
%{consolefontdir}/ter-216v.psf.gz
%{consolefontdir}/ter-714v.psf.gz
%{consolefontdir}/ter-716v.psf.gz
%{consolefontdir}/ter-914v.psf.gz
%{consolefontdir}/ter-916v.psf.gz
%{consolefontdir}/ter-c14v.psf.gz
%{consolefontdir}/ter-c16v.psf.gz
%{consolefontdir}/ter-d14v.psf.gz
%{consolefontdir}/ter-d16v.psf.gz
%{consolefontdir}/ter-g14v.psf.gz
%{consolefontdir}/ter-g16v.psf.gz
%{consolefontdir}/ter-h14v.psf.gz
%{consolefontdir}/ter-h16v.psf.gz
%{consolefontdir}/ter-i14v.psf.gz
%{consolefontdir}/ter-i16v.psf.gz
%{consolefontdir}/ter-k14v.psf.gz
%{consolefontdir}/ter-k16v.psf.gz
%{consolefontdir}/ter-m14v.psf.gz
%{consolefontdir}/ter-m16v.psf.gz
%{consolefontdir}/ter-p14v.psf.gz
%{consolefontdir}/ter-p16v.psf.gz
%{consolefontdir}/ter-u14v.psf.gz
%{consolefontdir}/ter-u16v.psf.gz
%{consolefontdir}/ter-v14v.psf.gz
%{consolefontdir}/ter-v16v.psf.gz
# normal and bold (non-VGAW specific) fonts
%{consolefontdir}/ter-112n.psf.gz
%{consolefontdir}/ter-114b.psf.gz
%{consolefontdir}/ter-114n.psf.gz
%{consolefontdir}/ter-116b.psf.gz
%{consolefontdir}/ter-116n.psf.gz
%{consolefontdir}/ter-118b.psf.gz
%{consolefontdir}/ter-118n.psf.gz
%{consolefontdir}/ter-120b.psf.gz
%{consolefontdir}/ter-120n.psf.gz
%{consolefontdir}/ter-122b.psf.gz
%{consolefontdir}/ter-122n.psf.gz
%{consolefontdir}/ter-124b.psf.gz
%{consolefontdir}/ter-124n.psf.gz
%{consolefontdir}/ter-128b.psf.gz
%{consolefontdir}/ter-128n.psf.gz
%{consolefontdir}/ter-132b.psf.gz
%{consolefontdir}/ter-132n.psf.gz
%{consolefontdir}/ter-212n.psf.gz
%{consolefontdir}/ter-214b.psf.gz
%{consolefontdir}/ter-214n.psf.gz
%{consolefontdir}/ter-216b.psf.gz
%{consolefontdir}/ter-216n.psf.gz
%{consolefontdir}/ter-218b.psf.gz
%{consolefontdir}/ter-218n.psf.gz
%{consolefontdir}/ter-220b.psf.gz
%{consolefontdir}/ter-220n.psf.gz
%{consolefontdir}/ter-222b.psf.gz
%{consolefontdir}/ter-222n.psf.gz
%{consolefontdir}/ter-224b.psf.gz
%{consolefontdir}/ter-224n.psf.gz
%{consolefontdir}/ter-228b.psf.gz
%{consolefontdir}/ter-228n.psf.gz
%{consolefontdir}/ter-232b.psf.gz
%{consolefontdir}/ter-232n.psf.gz
%{consolefontdir}/ter-712n.psf.gz
%{consolefontdir}/ter-714b.psf.gz
%{consolefontdir}/ter-714n.psf.gz
%{consolefontdir}/ter-716b.psf.gz
%{consolefontdir}/ter-716n.psf.gz
%{consolefontdir}/ter-718b.psf.gz
%{consolefontdir}/ter-718n.psf.gz
%{consolefontdir}/ter-720b.psf.gz
%{consolefontdir}/ter-720n.psf.gz
%{consolefontdir}/ter-722b.psf.gz
%{consolefontdir}/ter-722n.psf.gz
%{consolefontdir}/ter-724b.psf.gz
%{consolefontdir}/ter-724n.psf.gz
%{consolefontdir}/ter-728b.psf.gz
%{consolefontdir}/ter-728n.psf.gz
%{consolefontdir}/ter-732b.psf.gz
%{consolefontdir}/ter-732n.psf.gz
%{consolefontdir}/ter-912n.psf.gz
%{consolefontdir}/ter-914b.psf.gz
%{consolefontdir}/ter-914n.psf.gz
%{consolefontdir}/ter-916b.psf.gz
%{consolefontdir}/ter-916n.psf.gz
%{consolefontdir}/ter-918b.psf.gz
%{consolefontdir}/ter-918n.psf.gz
%{consolefontdir}/ter-920b.psf.gz
%{consolefontdir}/ter-920n.psf.gz
%{consolefontdir}/ter-922b.psf.gz
%{consolefontdir}/ter-922n.psf.gz
%{consolefontdir}/ter-924b.psf.gz
%{consolefontdir}/ter-924n.psf.gz
%{consolefontdir}/ter-928b.psf.gz
%{consolefontdir}/ter-928n.psf.gz
%{consolefontdir}/ter-932b.psf.gz
%{consolefontdir}/ter-932n.psf.gz
%{consolefontdir}/ter-c12n.psf.gz
%{consolefontdir}/ter-c14b.psf.gz
%{consolefontdir}/ter-c14n.psf.gz
%{consolefontdir}/ter-c16b.psf.gz
%{consolefontdir}/ter-c16n.psf.gz
%{consolefontdir}/ter-c18b.psf.gz
%{consolefontdir}/ter-c18n.psf.gz
%{consolefontdir}/ter-c20b.psf.gz
%{consolefontdir}/ter-c20n.psf.gz
%{consolefontdir}/ter-c22b.psf.gz
%{consolefontdir}/ter-c22n.psf.gz
%{consolefontdir}/ter-c24b.psf.gz
%{consolefontdir}/ter-c24n.psf.gz
%{consolefontdir}/ter-c28b.psf.gz
%{consolefontdir}/ter-c28n.psf.gz
%{consolefontdir}/ter-c32b.psf.gz
%{consolefontdir}/ter-c32n.psf.gz
%{consolefontdir}/ter-d12n.psf.gz
%{consolefontdir}/ter-d14b.psf.gz
%{consolefontdir}/ter-d14n.psf.gz
%{consolefontdir}/ter-d16b.psf.gz
%{consolefontdir}/ter-d16n.psf.gz
%{consolefontdir}/ter-d18b.psf.gz
%{consolefontdir}/ter-d18n.psf.gz
%{consolefontdir}/ter-d20b.psf.gz
%{consolefontdir}/ter-d20n.psf.gz
%{consolefontdir}/ter-d22b.psf.gz
%{consolefontdir}/ter-d22n.psf.gz
%{consolefontdir}/ter-d24b.psf.gz
%{consolefontdir}/ter-d24n.psf.gz
%{consolefontdir}/ter-d28b.psf.gz
%{consolefontdir}/ter-d28n.psf.gz
%{consolefontdir}/ter-d32b.psf.gz
%{consolefontdir}/ter-d32n.psf.gz
%{consolefontdir}/ter-g12n.psf.gz
%{consolefontdir}/ter-g14b.psf.gz
%{consolefontdir}/ter-g14n.psf.gz
%{consolefontdir}/ter-g16b.psf.gz
%{consolefontdir}/ter-g16n.psf.gz
%{consolefontdir}/ter-g18b.psf.gz
%{consolefontdir}/ter-g18n.psf.gz
%{consolefontdir}/ter-g20b.psf.gz
%{consolefontdir}/ter-g20n.psf.gz
%{consolefontdir}/ter-g22b.psf.gz
%{consolefontdir}/ter-g22n.psf.gz
%{consolefontdir}/ter-g24b.psf.gz
%{consolefontdir}/ter-g24n.psf.gz
%{consolefontdir}/ter-g28b.psf.gz
%{consolefontdir}/ter-g28n.psf.gz
%{consolefontdir}/ter-g32b.psf.gz
%{consolefontdir}/ter-g32n.psf.gz
%{consolefontdir}/ter-h12n.psf.gz
%{consolefontdir}/ter-h14b.psf.gz
%{consolefontdir}/ter-h14n.psf.gz
%{consolefontdir}/ter-h16b.psf.gz
%{consolefontdir}/ter-h16n.psf.gz
%{consolefontdir}/ter-h18b.psf.gz
%{consolefontdir}/ter-h18n.psf.gz
%{consolefontdir}/ter-h20b.psf.gz
%{consolefontdir}/ter-h20n.psf.gz
%{consolefontdir}/ter-h22b.psf.gz
%{consolefontdir}/ter-h22n.psf.gz
%{consolefontdir}/ter-h24b.psf.gz
%{consolefontdir}/ter-h24n.psf.gz
%{consolefontdir}/ter-h28b.psf.gz
%{consolefontdir}/ter-h28n.psf.gz
%{consolefontdir}/ter-h32b.psf.gz
%{consolefontdir}/ter-h32n.psf.gz
%{consolefontdir}/ter-i12n.psf.gz
%{consolefontdir}/ter-i14b.psf.gz
%{consolefontdir}/ter-i14n.psf.gz
%{consolefontdir}/ter-i16b.psf.gz
%{consolefontdir}/ter-i16n.psf.gz
%{consolefontdir}/ter-i18b.psf.gz
%{consolefontdir}/ter-i18n.psf.gz
%{consolefontdir}/ter-i20b.psf.gz
%{consolefontdir}/ter-i20n.psf.gz
%{consolefontdir}/ter-i22b.psf.gz
%{consolefontdir}/ter-i22n.psf.gz
%{consolefontdir}/ter-i24b.psf.gz
%{consolefontdir}/ter-i24n.psf.gz
%{consolefontdir}/ter-i28b.psf.gz
%{consolefontdir}/ter-i28n.psf.gz
%{consolefontdir}/ter-i32b.psf.gz
%{consolefontdir}/ter-i32n.psf.gz
%{consolefontdir}/ter-k12n.psf.gz
%{consolefontdir}/ter-k14b.psf.gz
%{consolefontdir}/ter-k14n.psf.gz
%{consolefontdir}/ter-k16b.psf.gz
%{consolefontdir}/ter-k16n.psf.gz
%{consolefontdir}/ter-k18b.psf.gz
%{consolefontdir}/ter-k18n.psf.gz
%{consolefontdir}/ter-k20b.psf.gz
%{consolefontdir}/ter-k20n.psf.gz
%{consolefontdir}/ter-k22b.psf.gz
%{consolefontdir}/ter-k22n.psf.gz
%{consolefontdir}/ter-k24b.psf.gz
%{consolefontdir}/ter-k24n.psf.gz
%{consolefontdir}/ter-k28b.psf.gz
%{consolefontdir}/ter-k28n.psf.gz
%{consolefontdir}/ter-k32b.psf.gz
%{consolefontdir}/ter-k32n.psf.gz
%{consolefontdir}/ter-m12n.psf.gz
%{consolefontdir}/ter-m14b.psf.gz
%{consolefontdir}/ter-m14n.psf.gz
%{consolefontdir}/ter-m16b.psf.gz
%{consolefontdir}/ter-m16n.psf.gz
%{consolefontdir}/ter-m18b.psf.gz
%{consolefontdir}/ter-m18n.psf.gz
%{consolefontdir}/ter-m20b.psf.gz
%{consolefontdir}/ter-m20n.psf.gz
%{consolefontdir}/ter-m22b.psf.gz
%{consolefontdir}/ter-m22n.psf.gz
%{consolefontdir}/ter-m24b.psf.gz
%{consolefontdir}/ter-m24n.psf.gz
%{consolefontdir}/ter-m28b.psf.gz
%{consolefontdir}/ter-m28n.psf.gz
%{consolefontdir}/ter-m32b.psf.gz
%{consolefontdir}/ter-m32n.psf.gz
%{consolefontdir}/ter-p12n.psf.gz
%{consolefontdir}/ter-p14b.psf.gz
%{consolefontdir}/ter-p14n.psf.gz
%{consolefontdir}/ter-p16b.psf.gz
%{consolefontdir}/ter-p16n.psf.gz
%{consolefontdir}/ter-p18b.psf.gz
%{consolefontdir}/ter-p18n.psf.gz
%{consolefontdir}/ter-p20b.psf.gz
%{consolefontdir}/ter-p20n.psf.gz
%{consolefontdir}/ter-p22b.psf.gz
%{consolefontdir}/ter-p22n.psf.gz
%{consolefontdir}/ter-p24b.psf.gz
%{consolefontdir}/ter-p24n.psf.gz
%{consolefontdir}/ter-p28b.psf.gz
%{consolefontdir}/ter-p28n.psf.gz
%{consolefontdir}/ter-p32b.psf.gz
%{consolefontdir}/ter-p32n.psf.gz
%{consolefontdir}/ter-u12n.psf.gz
%{consolefontdir}/ter-u14b.psf.gz
%{consolefontdir}/ter-u14n.psf.gz
%{consolefontdir}/ter-u16b.psf.gz
%{consolefontdir}/ter-u16n.psf.gz
%{consolefontdir}/ter-u18b.psf.gz
%{consolefontdir}/ter-u18n.psf.gz
%{consolefontdir}/ter-u20b.psf.gz
%{consolefontdir}/ter-u20n.psf.gz
%{consolefontdir}/ter-u22b.psf.gz
%{consolefontdir}/ter-u22n.psf.gz
%{consolefontdir}/ter-u24b.psf.gz
%{consolefontdir}/ter-u24n.psf.gz
%{consolefontdir}/ter-u28b.psf.gz
%{consolefontdir}/ter-u28n.psf.gz
%{consolefontdir}/ter-u32b.psf.gz
%{consolefontdir}/ter-u32n.psf.gz
%{consolefontdir}/ter-v12n.psf.gz
%{consolefontdir}/ter-v14b.psf.gz
%{consolefontdir}/ter-v14n.psf.gz
%{consolefontdir}/ter-v16b.psf.gz
%{consolefontdir}/ter-v16n.psf.gz
%{consolefontdir}/ter-v18b.psf.gz
%{consolefontdir}/ter-v18n.psf.gz
%{consolefontdir}/ter-v20b.psf.gz
%{consolefontdir}/ter-v20n.psf.gz
%{consolefontdir}/ter-v22b.psf.gz
%{consolefontdir}/ter-v22n.psf.gz
%{consolefontdir}/ter-v24b.psf.gz
%{consolefontdir}/ter-v24n.psf.gz
%{consolefontdir}/ter-v28b.psf.gz
%{consolefontdir}/ter-v28n.psf.gz
%{consolefontdir}/ter-v32b.psf.gz
%{consolefontdir}/ter-v32n.psf.gz

%ifnarch %{grub2_exclude_arches}
%files grub2
%doc README README-BG
%{grub2fontdir}/ter-u12b.pf2
%{grub2fontdir}/ter-u12n.pf2
%{grub2fontdir}/ter-u14b.pf2
%{grub2fontdir}/ter-u14n.pf2
%{grub2fontdir}/ter-u16b.pf2
%{grub2fontdir}/ter-u16n.pf2
%{grub2fontdir}/ter-u18b.pf2
%{grub2fontdir}/ter-u18n.pf2
%{grub2fontdir}/ter-u20b.pf2
%{grub2fontdir}/ter-u20n.pf2
%{grub2fontdir}/ter-u22b.pf2
%{grub2fontdir}/ter-u22n.pf2
%{grub2fontdir}/ter-u24b.pf2
%{grub2fontdir}/ter-u24n.pf2
%{grub2fontdir}/ter-u28b.pf2
%{grub2fontdir}/ter-u28n.pf2
%{grub2fontdir}/ter-u32b.pf2
%{grub2fontdir}/ter-u32n.pf2
%endif
