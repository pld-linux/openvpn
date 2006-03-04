# TODO
# - RFC: currently plugins were installed to /usr/%{_lib}/openvpn/plugins,
#   perhaps just /usr/%{_lib} as they're prefixed with openvpn-? pros from
#   this is that then you don't need to specify full path to plugins
#   in openvpn.conf
Summary:	VPN Daemon
Summary(pl):	Serwer VPN
Name:		openvpn
Version:	2.0.5
Release:	2.8
License:	GPL
Group:		Networking/Daemons
Source0:	http://openvpn.net/release/%{name}-%{version}.tar.gz
# Source0-md5:	4bd7a42991c93db23842a0992debe53b
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-2.0_rc16MH.patch
Patch1:		%{name}-optflags.patch
Patch2:		easy-rsa2.patch
URL:		http://openvpn.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	lzo-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.0.19
Conflicts:	kernel < 2.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var

%description
OpenVPN is a robust and highly configurable VPN (Virtual Private
Network) daemon which can be used to securely link two or more private
networks using an encrypted tunnel over the internet.

%description -l pl
OpenVPN jest mocnym i silnie konfigurowalnym serwerem VPN (Wirtualne
Sieci Prywatne), który mo¿e byæ u¿yty do bezpiecznego ³±czenia dwóch
lub wiêcej prywatnych sieci u¿ywaj±c zaszyfrowanego tunelu poprzez
internet.

%package devel
Summary:	Header files for OpenVPN plugins development
Summary(pl):	Pliki nag³ówkowe do tworzenia wtyczek OpenVPN
Group:		Development/Libraries

%description devel
This is the package containing the header files for OpenVPN plugins
development.

%description devel -l pl
Ten pakiet zawiera pliki nag³ówkowe do tworzenia wtyczek OpenVPN.

%package -n easy-rsa
Summary:	Small RSA key management package
Summary(pl):	Ma³y pakiet do zarz±dzania kluczami RSA
Version:	2.0
Group:		Applications/Communications
Requires:	grep
Requires:	openssl-tools
Requires:	/bin/bash

%description -n easy-rsa
This is a small RSA key management package, based on the openssl
command line tool, that can be found in the easy-rsa subdirectory of
the OpenVPN distribution.

For step-by-step instructions, see the HOWTO:
<http://openvpn.net/howto.html>.

%description -n easy-rsa -l pl
To jest ma³y pakiet do zarz±dzania kluczami RSA, oparty na narzêdziu
linii poleceñ openssl. Pakiet ten pochodzi z podkatalogu easy-rsa
dystrybucji OpenVPN.

Instrukcje krok po kroku mo¿na znale¼æ w HOWTO:
<http://openvpn.net/howto.html>.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}

%configure \
	--enable-pthread \
	--enable-iproute2
%{__make}

%{__make} -C plugin/auth-pam \
	OPTFLAGS="%{rpmcflags}"
%{__make} -C plugin/down-root \
	OPTFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/openvpn,%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},/var/run/openvpn,%{_includedir},%{_libdir}/%{name}/plugins}

install openvpn $RPM_BUILD_ROOT%{_sbindir}
install *.8 $RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install openvpn-plugin.h $RPM_BUILD_ROOT%{_includedir}
install plugin/{auth-pam,down-root}/*.so $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins

# easy-rsa 2.0
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_datadir}}/easy-rsa
install -d $RPM_BUILD_ROOT%{_sysconfdir}/easy-rsa/keys
cp -a easy-rsa/2.0/{vars,openssl.cnf} $RPM_BUILD_ROOT%{_sysconfdir}/easy-rsa
cp -a easy-rsa/2.0/{build-*,clean-all,inherit-inter,list-crl,revoke-full,sign-req} $RPM_BUILD_ROOT%{_datadir}/easy-rsa
cp -a easy-rsa/2.0/pkitool $RPM_BUILD_ROOT%{_sbindir}

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
%doc AUTHORS README ChangeLog sample-config-files sample-keys sample-scripts
%dir %{_sysconfdir}/openvpn
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,root,root) %{_sbindir}/openvpn
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins/*.so
%{_mandir}/man?/*
%dir /var/run/openvpn

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
