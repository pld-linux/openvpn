
# Conditional build:
%bcond_without	pkcs11		# build without PKCS#11 support

Summary:	VPN Daemon
Summary(pl.UTF-8):	Serwer VPN
Name:		openvpn
Version:	2.3.0
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://swupdate.openvpn.net/community/releases/%{name}-%{version}.tar.gz
# Source0-md5:	56cffde5d5320e0b1ec364d3e486aca9
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.tmpfiles
Patch0:		%{name}-pam.patch
URL:		http://www.openvpn.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libselinux-devel
BuildRequires:	lzo-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
%{?with_pkcs11:BuildRequires:	pkcs11-helper-devel}
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	/sbin/ip
Requires:	rc-scripts >= 0.4.3.0
Conflicts:	kernel < 2.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var

%description
OpenVPN is a robust and highly configurable VPN (Virtual Private
Network) daemon which can be used to securely link two or more private
networks using an encrypted tunnel over the internet.

%description -l pl.UTF-8
OpenVPN jest mocnym i silnie konfigurowalnym serwerem VPN (Wirtualne
Sieci Prywatne), który może być użyty do bezpiecznego łączenia dwóch
lub więcej prywatnych sieci używając zaszyfrowanego tunelu poprzez
internet.

%package devel
Summary:	Header files for OpenVPN plugins development
Summary(pl.UTF-8):	Pliki nagłówkowe do tworzenia wtyczek OpenVPN
Group:		Development/Libraries

%description devel
This is the package containing the header files for OpenVPN plugins
development.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe do tworzenia wtyczek OpenVPN.

%prep
%setup -q
%patch0 -p1

sed -e 's,/''usr/lib/openvpn,%{_libdir}/%{name},' %{SOURCE3} > contrib/update-resolv-conf

%build
%{__aclocal} -I m4
%{__autoheader}
%{__autoconf}
%{__automake}

%configure \
	%{!?with_pkcs11:--disable-pkcs11} \
	--enable-password-save \
	--enable-iproute2 \
	--enable-selinux \
	--enable-systemd \
	IFCONFIG=/sbin/ifconfig \
	IPROUTE=/sbin/ip \
	ROUTE=/sbin/route \
	NETSTAT=/bin/netstat

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/openvpn,%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},/var/run/openvpn,%{_includedir}} \
	$RPM_BUILD_ROOT{%{_libdir}/%{name}/plugins,/usr/lib/tmpfiles.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add openvpn
%service openvpn restart "OpenVPN"

%preun
if [ "$1" = "0" ]; then
	%service openvpn stop
	/sbin/chkconfig --del openvpn
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README* ChangeLog sample/sample-{config-files,keys,scripts} doc/management-notes.txt
%doc *.IPv6 src/plugins/*/README.*
%dir %{_sysconfdir}/openvpn
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,root,root) %{_sbindir}/openvpn
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins/*.so
%{_mandir}/man?/*
%dir /var/run/openvpn
/usr/lib/tmpfiles.d/%{name}.conf

%files devel
%defattr(644,root,root,755)
%doc doc/README.plugins sample/sample-plugins
%{_includedir}/*.h
