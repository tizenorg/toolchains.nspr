Summary:        Netscape Portable Runtime
Name:           nspr
Version:        4.8.7
Release:        1
License:        MPLv1.1 or GPLv2+ or LGPLv2+
URL:            http://www.mozilla.org/projects/nspr/
Group:          System/Libraries
BuildRoot:      %{_tmppath}/%{name}-%{version}-root
Source0:        https://ftp.mozilla.org/pub/mozilla.org/nspr/releases/v%{version}/src/%{name}-%{version}.tar.gz
Source1:        nspr.pc.in
Source2:        nspr-config-vars.in
Source1001: packaging/nspr.manifest 

Patch1:         nspr-config-pc.patch
Patch2:         pr-wait-cond-var-seconds.patch

%description
NSPR provides platform independence for non-GUI operating system 
facilities. These facilities include threads, thread synchronization, 
normal file and network I/O, interval timing and calendar time, basic 
memory management (malloc and free) and shared library linking.

%package devel
Summary:        Development libraries for the Netscape Portable Runtime
Group:          Development/Libraries
Requires:       nspr = %{version}-%{release}
Requires:       pkgconfig

%description devel
Header files for doing development with the Netscape Portable Runtime.

%prep

%setup -q

# Original nspr-config is not suitable for our distribution,
# because on different platforms it contains different dynamic content.
# Therefore we produce an adjusted copy of nspr-config that will be 
# identical on all platforms.
# However, we need to use original nspr-config to produce some variables
# that go into nspr.pc for pkg-config.

cp ./mozilla/nsprpub/config/nspr-config.in ./mozilla/nsprpub/config/nspr-config-pc.in
%patch1 -p0
%patch2 -p1

cp %{SOURCE2} ./mozilla/nsprpub/config/

%build
cp %{SOURCE1001} .

./mozilla/nsprpub/configure \
                 --prefix=%{_prefix} \
                 --libdir=%{_libdir} \
                 --includedir=%{_includedir}/nspr4 \
%ifarch x86_64 ppc64 ia64 s390x sparc64
                 --enable-64bit \
%endif
                 --enable-optimize="$RPM_OPT_FLAGS" \
                 --disable-debug

make

%install

%{__rm} -Rf $RPM_BUILD_ROOT

DESTDIR=$RPM_BUILD_ROOT \
  make install

NSPR_LIBS=`./config/nspr-config --libs`
NSPR_CFLAGS=`./config/nspr-config --cflags`
NSPR_VERSION=`./config/nspr-config --version`
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig

cat ./config/nspr-config-vars > \
                     $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nspr.pc

cat %{SOURCE1} | sed -e "s,%%libdir%%,%{_libdir},g" \
                     -e "s,%%prefix%%,%{_prefix},g" \
                     -e "s,%%exec_prefix%%,%{_prefix},g" \
                     -e "s,%%includedir%%,%{_includedir}/nspr4,g" \
                     -e "s,%%NSPR_VERSION%%,$NSPR_VERSION,g" \
                     -e "s,%%FULL_NSPR_LIBS%%,$NSPR_LIBS,g" \
                     -e "s,%%FULL_NSPR_CFLAGS%%,$NSPR_CFLAGS,g" >> \
                     $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/nspr.pc

%{__mkdir_p} $RPM_BUILD_ROOT/%{_bindir}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_lib}
%{__cp} ./config/nspr-config-pc $RPM_BUILD_ROOT/%{_bindir}/nspr-config

# Get rid of the things we don't want installed (per upstream)
%{__rm} -rf \
   $RPM_BUILD_ROOT/%{_bindir}/compile-et.pl \
   $RPM_BUILD_ROOT/%{_bindir}/prerr.properties \
   $RPM_BUILD_ROOT/%{_libdir}/libnspr4.a \
   $RPM_BUILD_ROOT/%{_libdir}/libplc4.a \
   $RPM_BUILD_ROOT/%{_libdir}/libplds4.a \
   $RPM_BUILD_ROOT/%{_datadir}/aclocal/nspr.m4 \
   $RPM_BUILD_ROOT/%{_includedir}/nspr4/md

for file in libnspr4.so libplc4.so libplds4.so
do
  mv -f $RPM_BUILD_ROOT/%{_libdir}/$file $RPM_BUILD_ROOT/%{_lib}/$file
  ln -sf ../../%{_lib}/$file $RPM_BUILD_ROOT/%{_libdir}/$file
done


%clean
%{__rm} -Rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%manifest nspr.manifest
%defattr(-,root,root)
/%{_lib}/libnspr4.so
/%{_lib}/libplc4.so
/%{_lib}/libplds4.so

%files devel
%manifest nspr.manifest
%defattr(-, root, root)
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_bindir}/nspr-config
