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
AC_COPYRIGHT([2007-2025 (c) Plecno s.r.l]) # Use [] for strings with special chars like ()
AC_INIT([justniffer],[0.6.1],[info@plecno.com])
AC_DEFINE([JUSTNIFFER_VERSION], ["0.6.1"], [justniffer version])
AC_DEFINE([JUSTNIFFER_YEAR], ["2025"], [justniffer year])
#AC_CONFIG_MACRO_DIR([included])
AM_INIT_AUTOMAKE([-Wall -Werror foreign]) # Added foreign, -Wall -Werror are good practice
AM_MAINTAINER_MODE([disable])
# Removed redundant AC_DEFINE([HAVE_LIB_PCAP], [], [has not libcap]) - AC_CHECK_LIB handles this better
AM_CONFIG_HEADER([include/config.h]) # Use []
AC_SUBST([BASH_COMPLETION_DIR])


LIBNIDS="libnids-1.21_patched"
NIDS2_INCLUDE="-I ../lib/$LIBNIDS/src"
NIDS2_LIB="-L../lib/$LIBNIDS/src -lnids2"
PCAP_LIB="-lpcap"
AC_SUBST([NIDS2_INCLUDE])
AC_SUBST([NIDS2_LIB])
AC_SUBST([PCAP_LIB])

AC_CHECK_PROG([BASH_F], [bash], [yes]) # Use [] for prog names/values
AC_MSG_CHECKING([for bash])
AC_MSG_RESULT([$BASH_F])
if test "x$BASH_F" != "xyes"; # Safer comparison
then
  AC_MSG_ERROR([cannot find bash shell, download and build it: see www.gnu.org/software/bash/])
fi
AC_CONFIG_MACRO_DIR([m4])
AC_PROG_CXX # Use standard macro, detects g++ etc.
AC_PROG_CPP
AC_PROG_INSTALL
AC_CHECK_HEADERS([sys/time.h time.h]) # Check both
AC_C_CONST
AC_C_INLINE
AC_FUNC_STRFTIME
AC_HEADER_STDBOOL

# Check for time.h/sys/time.h combination (Modern Autoconf handles this mostly)
AC_CHECK_HEADERS([sys/time.h], [], [], [#include <time.h>])
if test "$ac_cv_header_sys_time_h" = yes; then
  AC_DEFINE([HAVE_SYS_TIME_H], [1], [Define to 1 if you have <sys/time.h>.])
fi

AC_STRUCT_TM
AC_CHECK_HEADER([netinet/ip.h], [],
  AC_MSG_ERROR([cannot find netinet/ip.h]))

LT_INIT

# Check for libpcap *before* libnids subdir configure
# AC_CHECK_LIB modifies LIBS, ensure it's done correctly
# The third argument is action-if-found, fourth is action-if-not-found
AC_CHECK_LIB([pcap], [pcap_open_live],
             [AC_DEFINE([HAVE_LIB_PCAP], [1], [Define if libpcap is present])],
             [AC_MSG_ERROR([libpcap not found. Please install libpcap-dev or equivalent.])],
             [$PCAP_LIB]) # Add required library for the check itself

# Boost checks (Keep these before optional Python/Boost.Python)
AX_BOOST_BASE([1.74]) # Specify minimum required version

AX_BOOST_REGEX
AX_BOOST_PROGRAM_OPTIONS
AX_BOOST_IOSTREAMS
AX_BOOST_ASIO
AX_BOOST_THREAD

AC_ARG_WITH([boost-python],
    [AS_HELP_STRING([--with-boost-python], [Enable or disable Boost.Python support])],
    [], [with_boost_python=yes])

have_python_devel=no

if test "x$with_boost_python" = "xno"; then
    AC_MSG_WARN([Boost.Python support disabled])
else
    AX_PYTHON_DEVEL([],[
      have_python_devel=yes;
    ],[
    ])
fi
if test "x$have_python_devel" = "xyes"; then
  AX_BOOST_PYTHON([],[],[
          AC_MSG_WARN([cazzo cazzo])      
  ])
fi

BASH_COMPLETION_DIR="`pkg-config --variable=completionsdir bash-completion 2>/dev/null || echo ""`"
AS_IF([test -z "$BASH_COMPLETION_DIR"], [
  AC_MSG_WARN([Could not determine bash-completion directory from pkg-config.])
  AC_MSG_WARN([Bash completion files will not be installed automatically.])
  AC_MSG_WARN([You might need to install the 'bash-completion' package.])
  BASH_COMPLETION_DIR='${datadir}/bash-completion/completions' # Provide a sensible default fallback
])
AC_SUBST([BASH_COMPLETION_DIR]) # Ensure this is SUBSTed *after* potential modification

AC_CONFIG_SUBDIRS([lib/libnids-1.21_patched])

# --- Summary ---
AC_MSG_NOTICE([Configuration Summary:])
AC_MSG_CHECKING([whether to build Python bindings])
AS_IF([test "x$enable_python" = "xyes"], [
  AC_MSG_RESULT([yes])
],[
  AC_MSG_RESULT([no])
])
# Add more summary messages here if needed

AC_CONFIG_FILES([Makefile src/Makefile]) # Add other Makefiles that need configuration (e.g., python/Makefile)
AC_OUTPUT