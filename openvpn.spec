
# tun devices are handled in different way in 2.2. and 2.4 kernels.

%define         _kernel_ver     %(grep UTS_RELEASE %{_kernelsrcdir}/include/linux/version.h 2>/dev/null | cut -d'"' -f2)
%define         _kernel24       %(echo %{_kernel_ver} | grep -qv '2\.4\.' ; echo $?)
%if %{_kernel24}
%define         _kernel_series  2.4
%else
%define         _kernel_series  2.2
%endif

Summary:	VPN Daemon
Summary(pl):	Serwer VPN
Name:		openvpn
Version:	1.6
Release:	0.5.0@%{_kernel_series}
License:	GPL
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/openvpn/%{name}-%{version}_beta5.tar.gz
# Source0-md5:	009d0b140af92b0598079a003abaf381
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://openvpn.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	lzo-devel
BuildRequires:	openssl-devel >= 0.9.7c
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
%if %{_kernel24}
%{!?_without_dist_kernel:Requires: kernel > 2.4}
%else
%{!?_without_dist_kernel:Requires: kernel < 2.3}
%endif
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
%setup -q -n %{name}-%{version}_beta5

%build
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}

%configure \
	--enable-pthread
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/openvpn,%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},/var/run/openvpn}

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
