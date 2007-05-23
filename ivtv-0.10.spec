%define module ivtv
%define version 0.10.2

Summary: An iTVC15/16 and CX23415/16 driver
Name: %{module}-0.10
Version: %{version}
Release:  %mkrel 1
License: GPL
Group: System/Kernel and hardware
Obsoletes:	ivtv-stable
Obsoletes:	ivtv-0.8
Obsoletes:	ivtv-0.9
Provides: %{module}
Requires: kernel >= 2.6.18
Requires: perl-Video-ivtv
Requires: perl-Video-Frequencies
Source0: http://dl.ivtvdriver.org/ivtv/stable/%{module}-%{version}.tar.bz2
Source1: ivtv-2.6.21.patch
Patch0:	ivtv-0.2.0-rc3i-utils_Makefile.patch
Patch1: ivtv-0.2.0-rc3j-software_suspend.patch
Patch2:	ivtv-0.4.1-driver_compat.h.patch
Patch3:	ivtv-0.4.0-utils_Makefile.patch
Patch4:	ivtv-0.4.1-ivtvfwextract.patch
URL: http://ivtvdriver.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root/

%description
The primary goal of the IvyTV Project is to create a kernel driver for
the iTVC15 familiy of MPEG codecs. The iTVC15 family includes the
iTVC15 (CX24315) and iTVC16 (CX24316). These chips are commonly found
on Hauppauge's WinTV PVR-250 and PVR-350 TV capture cards.

%package -n dkms-%{name}
Summary:	Kernel drivers for the iTVC15/16 and CX23415/16 driver
Group:		System/Kernel and hardware
Obsoletes:	dkms-ivtv-stable
Obsoletes:	dkms-ivtv-0.8
Obsoletes:	dkms-ivtv-0.9
Provides:	dkms-%{module}
Requires:	dkms >= 1.00
Requires:	%{name} = %{version}-%{release}
Requires:	kernel >= 2.6.18

%description -n dkms-%{name}
The primary goal of the IvyTV Project is to create a kernel driver for
the iTVC15 familiy of MPEG codecs. The iTVC15 family includes the
iTVC15 (CX24315) and iTVC16 (CX24316). These chips are commonly found
on Hauppauge's WinTV PVR-250 and PVR-350 TV capture cards.

This package provides dkms kernel drivers for this hardware

%prep
%setup -q -n %{module}-%{version}
#setup -q -n %{module}-%{version}rc1
#patch0 -p1
#patch1 -p1
#patch2 -p0
%patch3 -p0
%patch4 -p0

%build
pwd
cd utils
%make
cd ../test
%make

%install
if [ "$RPM_BUILD_ROOT" != "/" ]; then
	rm -rf $RPM_BUILD_ROOT
fi

# DKMS
mkdir -p $RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}
cp -frv	driver/* \
	$RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}
cp -fv	utils/videodev2.h \
	$RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}
mkdir -p $RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}/i2c-drivers
cp -frv	i2c-drivers/* \
	$RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}/i2c-drivers
mkdir -p $RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}/patches
cp %{SOURCE1} \
	$RPM_BUILD_ROOT/usr/src/%{module}-%{version}-%{release}/patches

cat > %{buildroot}/usr/src/%{module}-%{version}-%{release}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}-%{release}"
PATCH[0]="ivtv-2.6.21.patch"
PATCH_MATCH[0]="2\.6\.21.*"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{module}"
MAKE[0]="make -C \${kernel_source_dir} SUBDIRS=\${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build modules"
CLEAN="make -C i\${kernel_source_dir} SUBDIRS=\${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build clean"

BUILT_MODULE_NAME[0]="ivtv"
#BUILT_MODULE_NAME[1]="ivtv-fb"

DEST_MODULE_LOCATION[0]="/kernel/3rdparty/ivtv"
#DEST_MODULE_LOCATION[1]="/kernel/3rdparty/ivtv"

AUTOINSTALL=yes
EOF

export PREFIX=/usr
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/ivtv
cd utils
%makeinstall DESTDIR=%{buildroot} INSTALLDIR=%{_bindir}

# Install ivtvfwextract util
cp ivtvfwextract.pl %{buildroot}/%{_libdir}/ivtv

cd ../test
install vbi vbi-detect vbi-passthrough wss %{buildroot}%{_bindir}/

# Remove unpackaged files
rm -rf %{buildroot}%{_includedir}/linux/ivtv.h

%clean
if [ "$RPM_BUILD_ROOT" != "/" ]; then
	rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,root,root,-)
%doc doc/*
%doc utils/README*
%{_libdir}/ivtv
%{_bindir}/*

%files -n dkms-%{name}
%defattr(-,root,root,-)
/usr/src/%{module}-%{version}-%{release}

%post -n dkms-%{name}
dkms add -m	%{module} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m	%{module} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m	%{module} -v %{version}-%{release} --rpm_safe_upgrade

%preun -n dkms-%{name}
dkms remove -m	%{module} -v %{version}-%{release} --rpm_safe_upgrade --all


