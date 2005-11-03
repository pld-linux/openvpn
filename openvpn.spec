# TODO
# - RFC: currently plugins were installed to /usr/%{_lib}/openvpn/plugins,
#   perhaps just /usr/%{_lib} as they're prefixed with openvpn-? pros from
#   this is that then you don't need to specify full path to plugins
#   in openvpn.conf
Summary:	VPN Daemon
Summary(pl):	Serwer VPN
Name:		openvpn
Version:	2.0.5
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://openvpn.net/release/%{name}-%{version}.tar.gz
# Source0-md5:	4bd7a42991c93db23842a0992debe53b
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-2.0_rc16MH.patch
Patch1:		%{name}-optflags.patch
URL:		http://openvpn.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	lzo-devel
BuildRequires:	openssl-devel >= 0.9.7d
Conflicts:	kernel < 2.4
Requires:	rc-scripts >= 0.4.0.19
Requires(post,preun):	/sbin/chkconfig
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

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}

%configure \
	--enable-pthread \
	--enable-iproute2
%{__make}

%{__make} -C plugin/auth-pam OPTFLAGS="%{rpmcflags}"
%{__make} -C plugin/down-root OPTFLAGS="%{rpmcflags}"

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

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add openvpn
if [ -f /var/lock/subsys/openvpn ]; then
	/etc/rc.d/init.d/openvpn restart 1>&2
else
	echo "Type \"/etc/rc.d/init.d/openvpn start\" to start OpenVPN" 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/openvpn ]; then
		/etc/rc.d/init.d/openvpn stop 1>&2
	fi
	/sbin/chkconfig --del openvpn
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README ChangeLog sample-config-files sample-keys easy-rsa sample-scripts
%dir %{_sysconfdir}/openvpn
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(755,root,root) %{_sbindir}/*
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
