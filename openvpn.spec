
# Conditional build:
%bcond_without	pkcs11		# build without PKCS#11 support

Summary:	VPN Daemon
Summary(pl.UTF-8):	Serwer VPN
Name:		openvpn
Version:	2.3.6
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://swupdate.openvpn.net/community/releases/%{name}-%{version}.tar.gz
# Source0-md5:	6ca03fe0fd093e0d01601abee808835c
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.tmpfiles
Source4:	%{name}-service-generator
Source5:	%{name}.target
Source6:	%{name}@.service
Patch0:		%{name}-pam.patch
URL:		http://www.openvpn.net/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	libselinux-devel
BuildRequires:	lzo-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	pam-devel
%{?with_pkcs11:BuildRequires:	pkcs11-helper-devel}
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	systemd-devel
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	/sbin/ip
Requires:	rc-scripts >= 0.4.3.0
Requires:	systemd-units >= 38
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
	$RPM_BUILD_ROOT{%{_libdir}/%{name}/plugins,%{systemdtmpfilesdir},%{systemdunitdir}} \
	$RPM_BUILD_ROOT%{systemdunitdir}-generators

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

install -p %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}-generators/openvpn-service-generator
install -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdunitdir}/openvpn.target
install -p %{SOURCE6} $RPM_BUILD_ROOT%{systemdunitdir}/openvpn@.service
ln -s /dev/null $RPM_BUILD_ROOT%{systemdunitdir}/openvpn.service

%{__rm} $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/*.la
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add openvpn
%service openvpn restart "OpenVPN"
%systemd_post openvpn.target

%preun
if [ "$1" = "0" ]; then
	%service openvpn stop
	/sbin/chkconfig --del openvpn
fi
%systemd_preun openvpn.target

%postun
%systemd_reload

%triggerpostun -- openvpn < 2.3.2-2
[ -f /etc/sysconfig/rpm ] && . /etc/sysconfig/rpm
[ ${RPM_ENABLE_SYSTEMD_SERVICE:-yes} = no ] && exit 0
[ "$(echo /etc/rc.d/rc[0-6].d/S[0-9][0-9]openvpn)" = "/etc/rc.d/rc[0-6].d/S[0-9][0-9]openvpn" ] && exit 0
export SYSTEMD_LOG_LEVEL=warning SYSTEMD_LOG_TARGET=syslog
/bin/systemctl --quiet enable openvpn.target || :
exit 0

%files
%defattr(644,root,root,755)
%doc AUTHORS README* ChangeLog sample/sample-{config-files,keys,scripts} doc/management-notes.txt
%doc *.IPv6 src/plugins/*/README.*
%dir %{_sysconfdir}/openvpn
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,root,root) %{_sbindir}/openvpn
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{systemdunitdir}-generators/%{name}-service-generator
%{systemdunitdir}/%{name}.service
%{systemdunitdir}/%{name}.target
%{systemdunitdir}/%{name}@.service
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/plugins
%attr(755,root,root) %{_libdir}/%{name}/plugins/openvpn-plugin-auth-pam.so
%attr(755,root,root) %{_libdir}/%{name}/plugins/openvpn-plugin-down-root.so
%{_mandir}/man8/openvpn.8*
%dir /var/run/openvpn
%{systemdtmpfilesdir}/%{name}.conf

%files devel
%defattr(644,root,root,755)
%doc doc/README.plugins sample/sample-plugins
%{_includedir}/openvpn-plugin.h
