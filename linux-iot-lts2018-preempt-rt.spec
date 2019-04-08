# This is a linux kernel with the preempt_rt patch set plus PK patches

Name:           linux-iot-lts2018-preempt-rt
Version:        4.19.13
Release:        3
License:        GPL-2.0
Summary:        The Linux kernel
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.19.13.tar.xz
Source2:        config
Source3:        cmdline

%define ktarget0 iot-lts2018-preempt-rt
%define kversion0 %{version}-%{release}.%{ktarget0}

BuildRequires:  buildreq-kernel

Requires: systemd-bin

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# quilt.url: https://github.com/intel/linux-intel-quilt
# quilt.branch: 4.19/preempt-rt
# quilt.tag:  lts-v4.19.13-preempt-rt-190114T183036

# PK XXXX: Series
Patch2276: 2276-net-sched-rename-qdisc_put-to-qdisc_destroy.patch
Patch2277: 2277-net-sched-sch_taprio-file-needed-to-be-updated.patch
Patch2278: 2278-net-sched-fix-build-issue-on-sch_taprio-file.patch
#END XXXX: PK Series

# Bug fixes
Patch8001: 8001-add-include-irq-h-vmbus_drv.patch
Patch8002: 8002-cpu-intel-rdt-update-cpus_allowed.patch

# Clear Linux patch
# needs to add to PK series
Patch9001: 9001-init-wait-for-partition-and-retry-scan.patch

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.19.13

#patchXXXX PK Series
%patch2276 -p1
%patch2277 -p1
%patch2278 -p1
# End XXXX PK Series

%patch8001 -p1
%patch8002 -p1

%patch9001 -p1

cp %{SOURCE2} .
cp %{SOURCE3} .
cp -a /usr/lib/firmware/i915 firmware/
cp -a /usr/lib/firmware/intel-ucode firmware/
cp -a /usr/lib/firmware/intel firmware/

%build
BuildKernel() {

    Target=$1
    Arch=x86_64
    ExtraVer="-%{release}.${Target}"
    Config=config

    rm -f localversion-rt

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile
    perl -p -i -e "s/^CONFIG_LOCALVERSION=.*/CONFIG_LOCALVERSION=\"\"/" ${Config}

    make O=${Target} -s mrproper
    cp ${Config} ${Target}/.config

    make O=${Target} -s ARCH=${Arch} olddefconfig
    make O=${Target} -s ARCH=${Arch} CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} %{?sparse_mflags}
}

BuildKernel %{ktarget0}

%install

InstallKernel() {

    Target=$1
    Kversion=$2
    Arch=x86_64
    KernelDir=%{buildroot}/usr/lib/kernel
    CmdLine=cmdline

    mkdir   -p ${KernelDir}
    install -m 644 ${Target}/.config    ${KernelDir}/config-${Kversion}
    install -m 644 ${Target}/System.map ${KernelDir}/System.map-${Kversion}
    install -m 644 ${Target}/vmlinux    ${KernelDir}/vmlinux-${Kversion}
    install -m 644 ${CmdLine}           ${KernelDir}/cmdline-${Kversion}
    cp  ${Target}/arch/x86/boot/bzImage ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules
    make O=${Target} -s ARCH=${Arch} INSTALL_MOD_PATH=%{buildroot}/usr modules_install

    rm -f %{buildroot}/usr/lib/modules/${Kversion}/build
    rm -f %{buildroot}/usr/lib/modules/${Kversion}/source

    ln -s org.clearlinux.${Target}.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-${Target}
}

InstallKernel %{ktarget0} %{kversion0}

rm -rf %{buildroot}/usr/lib/firmware

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion0}
/usr/lib/kernel/config-%{kversion0}
/usr/lib/kernel/cmdline-%{kversion0}
/usr/lib/kernel/org.clearlinux.%{ktarget0}.%{version}-%{release}
/usr/lib/kernel/default-%{ktarget0}
/usr/lib/modules/%{kversion0}/kernel
/usr/lib/modules/%{kversion0}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion0}
/usr/lib/kernel/vmlinux-%{kversion0}
