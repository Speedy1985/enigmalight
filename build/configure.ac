dnl Process this file with autoconf to produce a configure script.
dnl Created by Anjuta application wizard.

AC_INIT([EnigmaLight],[rc2])

AM_INIT_AUTOMAKE
AC_CONFIG_HEADERS([src/Include/Config.h])
AM_MAINTAINER_MODE

AC_SEARCH_LIBS([strerror],[cposix])

AC_PROG_CXX
AC_PROG_CC

AC_HEADER_STDC

dnl all use this
AC_CHECK_LIB(pthread,[main])
AC_CHECK_LIB(rt,[main])
AC_CHECK_LIB(m,[main])
AC_CHECK_LIB(dl,[main])

AS_IF([test "x$with_libusb" = xcheck], [
AC_CHECK_LIB([usb-1.0],[main],AC_DEFINE([HAVE_LIBUSB], [1], [ ]))
AC_CHECK_LIB([usb-1.0],[libusb_error_name],AC_DEFINE([HAVE_LIBUSB_ERROR_NAME], [1], [ ]))
AC_CHECK_HEADERS([libusb-1.0/libusb.h],[],[AC_MSG_ERROR([Missing a required header, please install it and try again...])])
])

AM_CONDITIONAL(HAVE_LIBUSB, [test "x$with_libusb" = xcheck])
AC_CHECK_DECL([clock_gettime], AC_DEFINE([HAVE_CLOCK_GETTIME], [1], [ ]), [], [[#include <time.h>]])

AC_CONFIG_FILES([
Makefile
src/Makefile
])
AC_OUTPUT