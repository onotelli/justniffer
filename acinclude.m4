AC_DEFUN([AX_BOOST_BASE],
[
AC_ARG_WITH([boost],
        AS_HELP_STRING([--with-boost@<:@=DIR@:>@], [use boost (default is yes) - it is possible to specify the root directory for boost (optional)]),
        [
    if test "$withval" = "no"; then
                want_boost="no"
    elif test "$withval" = "yes"; then
        want_boost="yes"
        ac_boost_path=""
    else
            want_boost="yes"
        ac_boost_path="$withval"
        fi
    ],
    [want_boost="yes"])


AC_ARG_WITH([boost-libdir],
        AS_HELP_STRING([--with-boost-libdir=LIB_DIR],
        [Force given directory for boost libraries. Note that this will overwrite library path detection, so use this parameter only if default library detection fails and you know exactly where your boost libraries are located.]),
        [
        if test -d $withval
        then
                ac_boost_lib_path="$withval"
        else
                AC_MSG_ERROR(--with-boost-libdir expected directory name)
        fi
        ],
        [ac_boost_lib_path=""]
)

if test "x$want_boost" = "xyes"; then
        boost_lib_version_req=ifelse([$1], ,1.20.0,$1)
        boost_lib_version_req_shorten=`expr $boost_lib_version_req : '\([[0-9]]*\.[[0-9]]*\)'`
        boost_lib_version_req_major=`expr $boost_lib_version_req : '\([[0-9]]*\)'`
        boost_lib_version_req_minor=`expr $boost_lib_version_req : '[[0-9]]*\.\([[0-9]]*\)'`
        boost_lib_version_req_sub_minor=`expr $boost_lib_version_req : '[[0-9]]*\.[[0-9]]*\.\([[0-9]]*\)'`
        if test "x$boost_lib_version_req_sub_minor" = "x" ; then
                boost_lib_version_req_sub_minor="0"
        fi
        WANT_BOOST_VERSION=`expr $boost_lib_version_req_major \* 100000 \+  $boost_lib_version_req_minor \* 100 \+ $boost_lib_version_req_sub_minor`
        AC_MSG_CHECKING(for boostlib >= $boost_lib_version_req)
        succeeded=no

        dnl first we check the system location for boost libraries
        dnl this location ist chosen if boost libraries are installed with the --layout=system option
        dnl or if you install boost with RPM
        if test "$ac_boost_path" != ""; then
                BOOST_LDFLAGS="-L$ac_boost_path/lib"
                BOOST_CPPFLAGS="-I$ac_boost_path/include"
        else
                for ac_boost_path_tmp in /usr /usr/local /opt /opt/local ; do
                        if test -d "$ac_boost_path_tmp/include/boost" && test -r "$ac_boost_path_tmp/include/boost"; then
                                BOOST_LDFLAGS="-L$ac_boost_path_tmp/lib"
                                BOOST_CPPFLAGS="-I$ac_boost_path_tmp/include"
                                break;
                        fi
                done
        fi

    dnl overwrite ld flags if we have required special directory with
    dnl --with-boost-libdir parameter
    if test "$ac_boost_lib_path" != ""; then
       BOOST_LDFLAGS="-L$ac_boost_lib_path"
    fi

        CPPFLAGS_SAVED="$CPPFLAGS"
        CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
        export CPPFLAGS

        LDFLAGS_SAVED="$LDFLAGS"
        LDFLAGS="$LDFLAGS $BOOST_LDFLAGS"
        export LDFLAGS

        AC_LANG_PUSH(C++)
        AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
        @%:@include <boost/version.hpp>
        ]], [[
        #if BOOST_VERSION >= $WANT_BOOST_VERSION
        // Everything is okay
        #else
        #  error Boost version is too old
        #endif
        ]])],[
        AC_MSG_RESULT(yes)
        succeeded=yes
        found_system=yes
        ],[
        ])
        AC_LANG_POP([C++])



        dnl if we found no boost with system layout we search for boost libraries
        dnl built and installed without the --layout=system option or for a staged(not installed) version
        if test "x$succeeded" != "xyes"; then
                _version=0
                if test "$ac_boost_path" != ""; then
                        if test -d "$ac_boost_path" && test -r "$ac_boost_path"; then
                                for i in `ls -d $ac_boost_path/include/boost-* 2>/dev/null`; do
                                        _version_tmp=`echo $i | sed "s#$ac_boost_path##" | sed 's/\/include\/boost-//' | sed 's/_/./'`
                                        V_CHECK=`expr $_version_tmp \> $_version`
                                        if test "$V_CHECK" = "1" ; then
                                                _version=$_version_tmp
                                        fi
                                        VERSION_UNDERSCORE=`echo $_version | sed 's/\./_/'`
                                        BOOST_CPPFLAGS="-I$ac_boost_path/include/boost-$VERSION_UNDERSCORE"
                                done
                        fi
                else
                        for ac_boost_path in /usr /usr/local /opt /opt/local ; do
                                if test -d "$ac_boost_path" && test -r "$ac_boost_path"; then
                                        for i in `ls -d $ac_boost_path/include/boost-* 2>/dev/null`; do
                                                _version_tmp=`echo $i | sed "s#$ac_boost_path##" | sed 's/\/include\/boost-//' | sed 's/_/./'`
                                                V_CHECK=`expr $_version_tmp \> $_version`
                                                if test "$V_CHECK" = "1" ; then
                                                        _version=$_version_tmp
                                                        best_path=$ac_boost_path
                                                fi
                                        done
                                fi
                        done

                        VERSION_UNDERSCORE=`echo $_version | sed 's/\./_/'`
                        BOOST_CPPFLAGS="-I$best_path/include/boost-$VERSION_UNDERSCORE"
            if test "$ac_boost_lib_path" = ""
            then
               BOOST_LDFLAGS="-L$best_path/lib"
            fi

                        if test "x$BOOST_ROOT" != "x"; then
                                if test -d "$BOOST_ROOT" && test -r "$BOOST_ROOT" && test -d "$BOOST_ROOT/stage/lib" && test -r "$BOOST_ROOT/stage/lib"; then
                                        version_dir=`expr //$BOOST_ROOT : '.*/\(.*\)'`
                                        stage_version=`echo $version_dir | sed 's/boost_//' | sed 's/_/./g'`
                                        stage_version_shorten=`expr $stage_version : '\([[0-9]]*\.[[0-9]]*\)'`
                                        V_CHECK=`expr $stage_version_shorten \>\= $_version`
                    if test "$V_CHECK" = "1" -a "$ac_boost_lib_path" = "" ; then
                                                AC_MSG_NOTICE(We will use a staged boost library from $BOOST_ROOT)
                                                BOOST_CPPFLAGS="-I$BOOST_ROOT"
                                                BOOST_LDFLAGS="-L$BOOST_ROOT/stage/lib"
                                        fi
                                fi
                        fi
                fi

                CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
                export CPPFLAGS
                LDFLAGS="$LDFLAGS $BOOST_LDFLAGS"
                export LDFLAGS

                AC_LANG_PUSH(C++)
                AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
                @%:@include <boost/version.hpp>
                ]], [[
                #if BOOST_VERSION >= $WANT_BOOST_VERSION
                // Everything is okay
                #else
                #  error Boost version is too old
                #endif
                ]])],[
                AC_MSG_RESULT(yes)
                succeeded=yes
                found_system=yes
                ],[
                ])
                AC_LANG_POP([C++])
        fi

        if test "$succeeded" != "yes" ; then
                if test "$_version" = "0" ; then
                        AC_MSG_ERROR([[We could not detect the boost libraries (version $boost_lib_version_req_shorten or higher). If you have a staged boost library (still not installed) please specify \$BOOST_ROOT in your environment and do not give a PATH to --with-boost option.  If you are sure you have boost installed, then check your version number looking in <boost/version.hpp>. See http://randspringer.de/boost for more documentation.]])
                else
                        AC_MSG_NOTICE([Your boost libraries seems to old (version $_version).])
                fi
        else
                AC_SUBST(BOOST_CPPFLAGS)
                AC_SUBST(BOOST_LDFLAGS)
                AC_DEFINE(HAVE_BOOST,,[define if the Boost library is available])
        fi

        CPPFLAGS="$CPPFLAGS_SAVED"
        LDFLAGS="$LDFLAGS_SAVED"
fi

])

AC_DEFUN([AX_BOOST_REGEX],
[
        AC_ARG_WITH([boost-regex],
        AS_HELP_STRING([--with-boost-regex@<:@=special-lib@:>@],
                   [use the Regex library from boost - it is possible to specify a certain library for the linker
                        e.g. --with-boost-regex=boost_regex-gcc-mt-d-1_33_1 ]),
        [
        if test "$withval" = "no"; then
                        want_boost="no"
        elif test "$withval" = "yes"; then
            want_boost="yes"
            ax_boost_user_regex_lib=""
        else
                    want_boost="yes"
                ax_boost_user_regex_lib="$withval"
                fi
        ],
        [want_boost="yes"]
        )

        if test "x$want_boost" = "xyes"; then
        AC_REQUIRE([AC_PROG_CC])
                CPPFLAGS_SAVED="$CPPFLAGS"
                CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
                export CPPFLAGS

                LDFLAGS_SAVED="$LDFLAGS"
                LDFLAGS="$LDFLAGS $BOOST_LDFLAGS"
                export LDFLAGS

        AC_CACHE_CHECK(whether the Boost::Regex library is available,
                                           ax_cv_boost_regex,
        [AC_LANG_PUSH([C++])
                         AC_COMPILE_IFELSE(AC_LANG_PROGRAM([[@%:@include <boost/regex.hpp>
                                                                                                ]],
                                   [[boost::regex r(); return 0;]]),
                   ax_cv_boost_regex=yes, ax_cv_boost_regex=no)
         AC_LANG_POP([C++])
                ])
                if test "x$ax_cv_boost_regex" = "xyes"; then
                        AC_DEFINE(HAVE_BOOST_REGEX,,[define if the Boost::Regex library is available])
            BOOSTLIBDIR=`echo $BOOST_LDFLAGS | sed -e 's/@<:@^\/@:>@*//'`
            if test "x$ax_boost_user_regex_lib" = "x"; then
                for libextension in `ls $BOOSTLIBDIR/libboost_regex*.{so,a}* 2>/dev/null | sed 's,.*/,,' | sed -e 's;^lib\(boost_regex.*\)\.so.*$;\1;' -e 's;^lib\(boost_regex.*\)\.a*$;\1;'` ; do
                     ax_lib=${libextension}
                                    AC_CHECK_LIB($ax_lib, exit,
                                 [BOOST_REGEX_LIB="-l$ax_lib"; AC_SUBST(BOOST_REGEX_LIB) link_regex="yes"; break],
                                    echo "ax_lib=$ax_lib"
				    [link_regex="no"])
                                done
                if test "x$link_regex" != "xyes"; then
                for libextension in `ls $BOOSTLIBDIR/boost_regex*.{dll,a}* 2>/dev/null | sed 's,.*/,,' | sed -e 's;^\(boost_regex.*\)\.dll.*$;\1;' -e 's;^\(boost_regex.*\)\.a*$;\1;'` ; do
                     ax_lib=${libextension}
                                    AC_CHECK_LIB($ax_lib, exit,
                                 [BOOST_REGEX_LIB="-l$ax_lib"; AC_SUBST(BOOST_REGEX_LIB) link_regex="yes"; break],
                                 [link_regex="no"])
                                done
                fi

            else
               for ax_lib in $ax_boost_user_regex_lib boost_regex-$ax_boost_user_regex_lib; do
                                      AC_CHECK_LIB($ax_lib, main,
                                   [BOOST_REGEX_LIB="-l$ax_lib"; AC_SUBST(BOOST_REGEX_LIB) link_regex="yes"; break],
                                   [link_regex="no"])
               done
            fi
                        if test "x$link_regex" != "xyes"; then
                                AC_MSG_ERROR(Could not link against $ax_lib !)
                        fi
                fi

                CPPFLAGS="$CPPFLAGS_SAVED"
        LDFLAGS="$LDFLAGS_SAVED"
        fi
])

AC_DEFUN([AX_BOOST_PROGRAM_OPTIONS],
[
        AC_ARG_WITH([boost-program-options],
                AS_HELP_STRING([--with-boost-program-options@<:@=special-lib@:>@],
                       [use the program options library from boost - it is possible to specify a certain library for the linker
                        e.g. --with-boost-program-options=boost_program_options-gcc-mt-1_33_1 ]),
        [
        if test "$withval" = "no"; then
                        want_boost="no"
        elif test "$withval" = "yes"; then
            want_boost="yes"
            ax_boost_user_program_options_lib=""
        else
                    want_boost="yes"
                ax_boost_user_program_options_lib="$withval"
                fi
        ],
        [want_boost="yes"]
        )

        if test "x$want_boost" = "xyes"; then
        AC_REQUIRE([AC_PROG_CC])
            export want_boost
                CPPFLAGS_SAVED="$CPPFLAGS"
                CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
                export CPPFLAGS
                LDFLAGS_SAVED="$LDFLAGS"
                LDFLAGS="$LDFLAGS $BOOST_LDFLAGS"
                export LDFLAGS
                AC_CACHE_CHECK([whether the Boost::Program_Options library is available],
                                           ax_cv_boost_program_options,
                                           [AC_LANG_PUSH(C++)
                                AC_COMPILE_IFELSE(AC_LANG_PROGRAM([[@%:@include <boost/program_options.hpp>
                                                          ]],
                                  [[boost::program_options::options_description generic("Generic options");
                                   return 0;]]),
                           ax_cv_boost_program_options=yes, ax_cv_boost_program_options=no)
                                        AC_LANG_POP([C++])
                ])
                if test "$ax_cv_boost_program_options" = yes; then
                                AC_DEFINE(HAVE_BOOST_PROGRAM_OPTIONS,,[define if the Boost::PROGRAM_OPTIONS library is available])
                  BOOSTLIBDIR=`echo $BOOST_LDFLAGS | sed -e 's/@<:@^\/@:>@*//'`
                if test "x$ax_boost_user_program_options_lib" = "x"; then
                for libextension in `ls $BOOSTLIBDIR/libboost_program_options*.{so,a}* 2>/dev/null | sed 's,.*/,,' | sed -e 's;^lib\(boost_program_options.*\)\.so.*$;\1;' -e 's;^lib\(boost_program_options.*\)\.a*$;\1;'` ; do
                     ax_lib=${libextension}
                                    AC_CHECK_LIB($ax_lib, exit,
                                 [BOOST_PROGRAM_OPTIONS_LIB="-l$ax_lib"; AC_SUBST(BOOST_PROGRAM_OPTIONS_LIB) link_program_options="yes"; break],
                                 [link_program_options="no"])
                                done
                if test "x$link_program_options" != "xyes"; then
                for libextension in `ls $BOOSTLIBDIR/boost_program_options*.{dll,a}* 2>/dev/null | sed 's,.*/,,' | sed -e 's;^\(boost_program_options.*\)\.dll.*$;\1;' -e 's;^\(boost_program_options.*\)\.a*$;\1;'` ; do
                     ax_lib=${libextension}
                                    AC_CHECK_LIB($ax_lib, exit,
                                 [BOOST_PROGRAM_OPTIONS_LIB="-l$ax_lib"; AC_SUBST(BOOST_PROGRAM_OPTIONS_LIB) link_program_options="yes"; break],
                                 [link_program_options="no"])
                                done
                fi
                else
                  for ax_lib in $ax_boost_user_program_options_lib boost_program_options-$ax_boost_user_program_options_lib; do
                                      AC_CHECK_LIB($ax_lib, main,
                                   [BOOST_PROGRAM_OPTIONS_LIB="-l$ax_lib"; AC_SUBST(BOOST_PROGRAM_OPTIONS_LIB) link_program_options="yes"; break],
                                   [link_program_options="no"])
                  done
                fi
                                if test "x$link_program_options" != "xyes"; then
                                        AC_MSG_ERROR([Could not link against [$ax_lib] !])
                                fi
                fi
                CPPFLAGS="$CPPFLAGS_SAVED"
        LDFLAGS="$LDFLAGS_SAVED"
        fi
])

AC_DEFUN([AX_BOOST_IOSTREAMS],
[
        AC_ARG_WITH([boost-iostreams],
        AS_HELP_STRING([--with-boost-iostreams@<:@=special-lib@:>@],
                   [use the IOStreams library from boost - it is possible to specify a certain library for the linker
                        e.g. --with-boost-iostreams=boost_iostreams-gcc-mt-d-1_33_1 ]),
        [
        if test "$withval" = "no"; then
                        want_boost="no"
        elif test "$withval" = "yes"; then
            want_boost="yes"
            ax_boost_user_iostreams_lib=""
        else
                    want_boost="yes"
                ax_boost_user_iostreams_lib="$withval"
                fi
        ],
        [want_boost="yes"]
        )

        if test "x$want_boost" = "xyes"; then
        AC_REQUIRE([AC_PROG_CC])
                CPPFLAGS_SAVED="$CPPFLAGS"
                CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
                export CPPFLAGS

                LDFLAGS_SAVED="$LDFLAGS"
                LDFLAGS="$LDFLAGS $BOOST_LDFLAGS"
                export LDFLAGS

        AC_CACHE_CHECK(whether the Boost::IOStreams library is available,
                                           ax_cv_boost_iostreams,
        [AC_LANG_PUSH([C++])
                 AC_COMPILE_IFELSE(AC_LANG_PROGRAM([[@%:@include <boost/iostreams/filtering_stream.hpp>
                                                                                         @%:@include <boost/range/iterator_range.hpp>
                                                                                        ]],
                                  [[std::string  input = "Hello World!";
                                                                 namespace io = boost::iostreams;
                                                                         io::filtering_istream  in(boost::make_iterator_range(input));
                                                                         return 0;
                                   ]]),
                             ax_cv_boost_iostreams=yes, ax_cv_boost_iostreams=no)
         AC_LANG_POP([C++])
                ])
                if test "x$ax_cv_boost_iostreams" = "xyes"; then
                        AC_DEFINE(HAVE_BOOST_IOSTREAMS,,[define if the Boost::IOStreams library is available])
            BOOSTLIBDIR=`echo $BOOST_LDFLAGS | sed -e 's/@<:@^\/@:>@*//'`
            if test "x$ax_boost_user_iostreams_lib" = "x"; then
                for libextension in `ls $BOOSTLIBDIR/libboost_iostreams*.{so,a}* 2>/dev/null | sed 's,.*/,,' | sed -e 's;^lib\(boost_iostreams.*\)\.so.*$;\1;' -e 's;^lib\(boost_iostreams.*\)\.a*$;\1;'` ; do
                     ax_lib=${libextension}
                                    AC_CHECK_LIB($ax_lib, exit,
                                 [BOOST_IOSTREAMS_LIB="-l$ax_lib"; AC_SUBST(BOOST_IOSTREAMS_LIB) link_iostreams="yes"; break],
                                 [link_iostreams="no"])
                                done
                if test "x$link_iostreams" != "xyes"; then
                for libextension in `ls $BOOSTLIBDIR/boost_iostreams*.{dll,a}* 2>/dev/null | sed 's,.*/,,' | sed -e 's;^\(boost_iostreams.*\)\.dll.*$;\1;' -e 's;^\(boost_iostreams.*\)\.a*$;\1;'` ; do
                     ax_lib=${libextension}
                                    AC_CHECK_LIB($ax_lib, exit,
                                 [BOOST_IOSTREAMS_LIB="-l$ax_lib"; AC_SUBST(BOOST_IOSTREAMS_LIB) link_iostreams="yes"; break],
                                 [link_iostreams="no"])
                                done
                fi

            else
               for ax_lib in $ax_boost_user_iostreams_lib boost_iostreams-$ax_boost_user_iostreams_lib; do
                                      AC_CHECK_LIB($ax_lib, main,
                                   [BOOST_IOSTREAMS_LIB="-l$ax_lib"; AC_SUBST(BOOST_IOSTREAMS_LIB) link_iostreams="yes"; break],
                                   [link_iostreams="no"])
                  done

            fi
                        if test "x$link_iostreams" != "xyes"; then
                                AC_MSG_ERROR(Could not link against $ax_lib !)
                        fi
                fi

                CPPFLAGS="$CPPFLAGS_SAVED"
        LDFLAGS="$LDFLAGS_SAVED"
        fi
])

AC_DEFUN([AX_PYTHON],
[
        AC_ARG_ENABLE(python, AS_HELP_STRING([--enable-python],[install python-scripts (default is yes)]) ,
        [
	 if test "$enableval" == "yes"; then
	    AX_PYTHON_ENABLED="enabled"
	 else
	    AX_PYTHON_ENABLED="disabled"
	 fi
	],
	[
	  AX_PYTHON_ENABLED="enabled"	
	])
	if test "$AX_PYTHON_ENABLED" == "enabled";then
	  AM_PATH_PYTHON(2.6, , [AC_MSG_NOTICE([your need python >=2.6, disabling python feature]) ; AX_PYTHON_ENABLED="disabled"])
	fi
])
