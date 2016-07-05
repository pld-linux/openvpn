#
# Conditional build:
%bcond_without	pkcs11		# build without PKCS#11 support

Summary:	VPN Daemon
Summary(pl.UTF-8):	Serwer VPN
Name:		openvpn
Version:	2.3.11
Release:	1
License:	GPL v2
Group:		Networking/Daemons
# when updating, use .xz url:
#Source0:	http://build.openvpn.net/downloads/releases/%{name}-%{version}.tar.xz
#BuildRequires:	tar >= 1:1.22
#BuildRequires:	xz
Source0:	http://swupdate.openvpn.net/community/releases/%{name}-%{version}.tar.gz
# Source0-md5:	e075a11f9fd0a81dae1ed1760479e9d6
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.tmpfiles
Source4:	%{name}-service-generator
Source5:	%{name}.target
Source6:	%{name}@.service
Source7:	%{name}-update-resolv-conf
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
Suggests:	%{name}-plugin-auth-pam
Suggests:	%{name}-plugin-down-root
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

%package plugin-auth-pam
Summary:	Plugin for username/password authentication via PAM
Summary(pl.UTF-8):	Wtyczka do uwierzytelniania nazwą użytkownika i hasłem poprzez PAM
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-auth-pam
The openvpn-auth-pam module implements username/password
authentication via PAM, and essentially allows any authentication
method supported by PAM (such as LDAP, RADIUS, or Linux Shadow
passwords) to be used with OpenVPN. While PAM supports
username/password authentication, this can be combined with X509
certificates to provide two indepedent levels of authentication.

This module uses a split privilege execution model which will function
even if you drop openvpn daemon privileges using the user, group, or
chroot directives.

%description plugin-auth-pam -l pl.UTF-8
Moduł openvpn-auth-pam implementuje uwierzytelnianie nazwą użytkownika
i hasłem poprzez PAM, zasadniczo pozwalając na korzystanie z dowolnej
metody uwierzytelniania obsługiwanej przez PAM (np. LDAP, RADIUS,
hasła shadow) z OpenVPN. Jako że PAM obsługuje uwierzytelnianie nazwą
użytkownika i hasłem, to można je łączyć z certyfikatami X509 w celu
zapewniania dwóch różnych poziomów uwierzytelnienia.

Ten moduł wykorzystuje model wykonywania z podziałem uprawnień, co
działa nawet przy odrzuceniu uprawnień demona openvpn przy użyciu
dyrektyw user, group lub chroot.

%package plugin-down-root
Summary:	Plugin to allow root after privilege drop
Summary(pl.UTF-8):	Wtyczka pozwalająca na wykorzystanie uprawnień roota po odrzuceniu uprawnień
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description plugin-down-root
The down-root module allows an OpenVPN configuration to call a down
script with root privileges, even when privileges have been dropped
using --user/--group/--chroot.

This module uses a split privilege execution model which will fork()
before OpenVPN drops root privileges, at the point where the --up
script is usually called. The module will then remain in a wait state
until it receives a message from OpenVPN via pipe to execute the down
script. Thus, the down script will be run in the same execution
environment as the up script.

%description plugin-down-root -l pl.UTF-8
Moduł down-root pozwala na wywołanie skryptu down z uprawnieniami
roota z poziomu konfiguracji OpenVPN-a nawet w przypadku odrzucenia
uprawnień przy użyciu opcji --user/--group/--chroot.

Ten moduł wykorzystuje model wykonywania z podziałem uprawnień, który
wykonuje fork() przed odrzuceniem uprawnień roota, w miejscu, gdzie
zwykle jest wywoływany skrypt --up. Moduł pozostaje w stanie
oczekiwania do odebrania przez potok od OpenVPN-a komunikatu, aby
wykonać skrypt down. Dzięki temu skrypt down zostanie uruchomiony w
tym samym środowisku, co skrypt up.

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

sed -e 's,/''usr/lib/openvpn,%{_libdir}/%{name},' %{SOURCE7} > contrib/update-resolv-conf

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

# we use "cp", not "install", not to pull /bin/bash dependency
cp -p contrib/pull-resolv-conf/client.down $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -p contrib/pull-resolv-conf/client.up $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -p contrib/update-resolv-conf $RPM_BUILD_ROOT%{_libdir}/%{name}

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
%doc *.IPv6
%dir %{_sysconfdir}/openvpn
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,root,root) %{_sbindir}/openvpn
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{systemdunitdir}-generators/%{name}-service-generator
%{systemdunitdir}/%{name}.service
%{systemdunitdir}/%{name}.target
%{systemdunitdir}/%{name}@.service
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/client.down
%attr(755,root,root) %{_libdir}/%{name}/client.up
%attr(755,root,root) %{_libdir}/%{name}/update-resolv-conf
%dir %{_libdir}/%{name}/plugins
%{_mandir}/man8/openvpn.8*
%dir /var/run/openvpn
%{systemdtmpfilesdir}/%{name}.conf

%files plugin-auth-pam
%defattr(644,root,root,755)
%doc src/plugins/auth-pam/README.auth-pam
%attr(755,root,root) %{_libdir}/%{name}/plugins/openvpn-plugin-auth-pam.so

%files plugin-down-root
%defattr(644,root,root,755)
%doc src/plugins/down-root/README.down-root
%attr(755,root,root) %{_libdir}/%{name}/plugins/openvpn-plugin-down-root.so

%files devel
%defattr(644,root,root,755)
%doc doc/README.plugins sample/sample-plugins
%{_includedir}/openvpn-plugin.h
