Summary:	VPN Daemon
Summary(pl):	Serwer VPN
Name:		openvpn
Version:	1.0
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
aclocal
autoheader
autoconf
%configure \
	%{!?debug:--disable-debug} \
	--disable-opto
%{__make} CFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man8}

install %{name} $RPM_BUILD_ROOT%{_sbindir}
install *.8 $RPM_BUILD_ROOT%{_mandir}/man8

gzip -9nf CHANGES README

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc *.gz
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man?/*
