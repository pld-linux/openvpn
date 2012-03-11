
# Conditional build:
%bcond_without	pkcs11		# build without PKCS#11 support
%bcond_with	ipv6_payload	# build with ipv6 payload support in server
				# mode

Summary:	VPN Daemon
Summary(pl.UTF-8):	Serwer VPN
Name:		openvpn
Version:	2.2.2
Release:	3
License:	GPL
Group:		Networking/Daemons
Source0:	http://swupdate.openvpn.net/community/releases/%{name}-%{version}.tar.gz
# Source0-md5:	c5181e27b7945fa6276d21873329c5c7
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}-update-resolv-conf
Source4:	%{name}.tmpfiles
Patch0:		%{name}-optflags.patch
Patch1:		easy-rsa2.patch
Patch2:		%{name}-pam.patch
# http://www.greenie.net/ipv6/openvpn-2.1-ipv6-20100307-1.patch.gz
Patch3:		%{name}-ipv6_payload.patch
URL:		http://www.openvpn.net/
BuildRequires:	autoconf
BuildRequires:	automake
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

%package -n easy-rsa
Summary:	Small RSA key management package
Summary(pl.UTF-8):	Mały pakiet do zarządzania kluczami RSA
Group:		Applications
Requires:	grep
Requires:	openssl-tools

%description -n easy-rsa
This is a small RSA key management package, based on the openssl
command line tool, that can be found in the easy-rsa subdirectory of
the OpenVPN distribution.

For step-by-step instructions, see the HOWTO:
<http://www.openvpn.net/index.php/documentation/howto.html>.

%description -n easy-rsa -l pl.UTF-8
To jest mały pakiet do zarządzania kluczami RSA, oparty na narzędziu
linii poleceń openssl. Pakiet ten pochodzi z podkatalogu easy-rsa
dystrybucji OpenVPN.

Instrukcje krok po kroku można znaleźć w HOWTO:
<http://www.openvpn.net/index.php/documentation/howto.html>.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%{?with_ipv6_payload:%patch3 -p1}

mv plugin/auth-pam/README README.auth-pam
mv plugin/down-root/README README.down-root

sed -e 's,/''usr/lib/openvpn,%{_libdir}/%{name},' %{SOURCE3} > contrib/update-resolv-conf

%build
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}

%configure \
	%{!?with_pkcs11:--disable-pkcs11} \
	--enable-password-save \
	--enable-iproute2 \
	--with-ifconfig-path=/sbin/ifconfig \
	--with-iproute-path=/sbin/ip \
	--with-route-path=/sbin/route \
	--with-netstat-path=/bin/netstat

%{__make} CFLAGS="%{rpmcflags} %{rpmcppflags} -D_GNU_SOURCE"

%{__make} -C plugin/auth-pam \
	OPTFLAGS="%{rpmcflags} %{rpmcppflags}"
%{__make} -C plugin/down-root \
	OPTFLAGS="%{rpmcflags} %{rpmcppflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/openvpn,%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},/var/run/openvpn,%{_includedir}} \
	$RPM_BUILD_ROOT{%{_libdir}/%{name}/plugins,/usr/lib/tmpfiles.d}

install openvpn $RPM_BUILD_ROOT%{_sbindir}
install *.8 $RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install openvpn-plugin.h $RPM_BUILD_ROOT%{_includedir}
install plugin/{auth-pam,down-root}/*.so $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins

install %{SOURCE4} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

# easy-rsa 2.0
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_datadir}}/easy-rsa
install -d $RPM_BUILD_ROOT%{_sysconfdir}/easy-rsa/keys
cp -a easy-rsa/2.0/vars $RPM_BUILD_ROOT%{_sysconfdir}/easy-rsa
cp -a easy-rsa/2.0/openssl-1.0.0.cnf $RPM_BUILD_ROOT%{_sysconfdir}/easy-rsa/openssl.cnf
cp -a easy-rsa/2.0/{build-*,clean-all,inherit-inter,list-crl,revoke-full,sign-req} $RPM_BUILD_ROOT%{_datadir}/easy-rsa
cp -a easy-rsa/2.0/pkitool $RPM_BUILD_ROOT%{_sbindir}

# we use cp -a, not to pull /bin/bash dependency
cp -a contrib/pull-resolv-conf/client.down $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a contrib/pull-resolv-conf/client.up $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a contrib/update-resolv-conf $RPM_BUILD_ROOT%{_libdir}/%{name}

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
%doc AUTHORS README* ChangeLog sample-config-files sample-keys sample-scripts management/management-notes.txt
%dir %{_sysconfdir}/openvpn
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,root,root) %{_sbindir}/openvpn
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/client.down
%attr(755,root,root) %{_libdir}/%{name}/client.up
%attr(755,root,root) %{_libdir}/%{name}/update-resolv-conf
%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins/*.so
%{_mandir}/man?/*
%dir /var/run/openvpn
/usr/lib/tmpfiles.d/%{name}.conf

%files devel
%defattr(644,root,root,755)
%doc plugin/{README,examples/}
%{_includedir}/*.h

%files -n easy-rsa
%defattr(644,root,root,755)
%doc easy-rsa/2.0/README
%dir %{_sysconfdir}/easy-rsa
%dir %attr(700,root,root) %{_sysconfdir}/easy-rsa/keys
%config(noreplace) %attr(640,root,root) %verify(not md5 mtime size) %{_sysconfdir}/easy-rsa/vars
%config(noreplace) %attr(640,root,root) %verify(not md5 mtime size) %{_sysconfdir}/easy-rsa/openssl.cnf
%attr(755,root,root) %{_sbindir}/pkitool
%dir %{_datadir}/easy-rsa
%attr(755,root,root) %{_datadir}/easy-rsa/*
