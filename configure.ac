dnl
dnl	Copyright (c) 2007-2025 Plecno s.r.l. All Rights Reserved 
dnl	info@plecno.com
dnl	via Giovio 8, 20144 Milano, Italy
dnl
dnl	Released under the terms of the GPLv3 or later
dnl
dnl	Author: Oreste Notelli <oreste.notelli@plecno.com>	
dnl

AC_PREREQ([2.71])
AC_COPYRIGHT(2007-2025 (c) Plecno s.r.l)
AC_INIT([justniffer],[0.5.22],[info@plecno.com])
AC_DEFINE(JUSTNIFFER_VERSION, ["0.5.22"], [justniffer version])
AC_DEFINE(JUSTNIFFER_YEAR, ["2025"], [justniffer year])
#AC_CONFIG_MACRO_DIR([included])
AM_INIT_AUTOMAKE
AM_MAINTAINER_MODE([disable])
AC_DEFINE([HAVE_LIB_PCAP], [], [has not libcap])
AM_CONFIG_HEADER(include/config.h)
AC_SUBST([BASH_COMPLETION_DIR])

#AM_INIT_AUTOMAKE([-Wall -Werror])

dnl if test "$CXXFLAGS" = ""; then
dnl CXXFLAGS="-Os -Wall"
dnl fi

LIBNIDS="libnids-1.21_patched"
NIDS2_INCLUDE="-I ../lib/$LIBNIDS/src"
NIDS2_LIB="-L../lib/$LIBNIDS/src -lnids2"
PCAP_LIB="-lpcap"
AC_SUBST(NIDS2_INCLUDE)
AC_SUBST(NIDS2_LIB)
AC_SUBST(PCAP_LIB)

AC_CHECK_PROG(BASH_F, bash, "yes") 
echo "BASH_F= $BASH_F"
if test "$BASH_F" != "yes";
then
  AC_MSG_ERROR(["cannot find bash shell, download and build it: see www.gnu.org/software/bash/"])
fi
AC_CONFIG_MACRO_DIR([m4])
AC_PROG_CXX (gcc)
AC_PROG_CPP
AC_PROG_INSTALL
AC_CHECK_HEADERS([sys/time.h])
AC_C_CONST
AC_C_INLINE
AC_FUNC_STRFTIME
AC_HEADER_STDBOOL
m4_warn([obsolete],
[Update your code to rely only on HAVE_SYS_TIME_H,
then remove this warning and the obsolete code below it.
All current systems provide time.h; it need not be checked for.
Not all systems provide sys/time.h, but those that do, all allow
you to include it and time.h simultaneously.])dnl
AC_CHECK_HEADERS_ONCE([sys/time.h])
# Obsolete code to be removed.
if test $ac_cv_header_sys_time_h = yes; then
  AC_DEFINE([TIME_WITH_SYS_TIME],[1],[Define to 1 if you can safely include both <sys/time.h>
	     and <time.h>.  This macro is obsolete.])
fi
# End of obsolete code.

AC_STRUCT_TM
AC_CHECK_HEADER(netinet/ip.h, , 
  AC_MSG_ERROR(["cannot find netinet/ip.h"]))
LT_INIT  
AC_CHECK_LIB(pcap, pcap_open_live, AC_DEFINE(HAVE_LIB_PCAP))

AX_BOOST_BASE([1.74])
 
AX_BOOST_REGEX
AX_BOOST_PROGRAM_OPTIONS
AX_BOOST_IOSTREAMS
AX_BOOST_PYTHON
AX_BOOST_ASIO
AX_BOOST_THREAD

AC_CHECK_FILE(lib/$LIBNIDS/README.original, ,
[ AC_CHECK_PROG(PATCH, patch, yes, no) 
  if test "$PATCH" != yes;
  then
    AC_MSG_ERROR(["cannot find patch, download and build it: see http://www.gnu.org/software/patch/"])
  fi
  TAR_FOUND=""
  AC_CHECK_PROG(TAR, tar, yes) 
  if test "$TAR" != yes;
  then
    AC_MSG_ERROR(["cannot find tar"])
  fi
  AC_CHECK_FILE(lib/$LIBNIDS/src/nids2.h, , AC_MSG_ERROR(["cannot find patched libnids"]))
  ]
)

BASH_COMPLETION_DIR="`pkg-config --variable=completionsdir bash-completion`"

AC_CONFIG_SUBDIRS([lib/libnids-1.21_patched])
	
AX_PYTHON_DEVEL



	
AC_CONFIG_FILES([Makefile src/Makefile ])
AC_OUTPUT




