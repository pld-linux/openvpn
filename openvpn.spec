Summary:	VPN Daemon
Summary(pl):	Serwer VPN
Name:		openvpn
Version:	1.3.1
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://prdownloads.sourceforge.net/openvpn/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://openvpn.sourceforge.net/
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	lzo-devel
BuildRequires:	openssl-devel >= 0.9.6
PreReq:		rc-scripts
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

%prep
%setup -q

%build
%{__aclocal}
autoheader
%{__autoconf}
%{__automake}
%configure 
%{__make} #CFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/openvpn,%{_sbindir},%{_mandir}/man8}
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig,/var/run/openvpn}

install %{name} $RPM_BUILD_ROOT%{_sbindir}
install *.8 $RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

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
%doc AUTHORS README ChangeLog sample-config-files sample-keys 
%attr(755,root,root) %{_sbindir}/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not size mtime md5) /etc/sysconfig/%{name}
%attr(754,root,root) %config(noreplace) /etc/rc.d/init.d/%{name}
%{_mandir}/man?/*
%dir /var/run/openvpn
