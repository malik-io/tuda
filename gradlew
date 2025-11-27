#!/usr/bin/env bash

#
# Copyright 2015 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS=""

APP_NAME="Gradle"
APP_BASE_NAME=`basename "$0"`

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD="maximum"

warn () {
    echo "$*"
}

die () {
    echo
    echo "ERROR: $*"
    echo
    exit 1
}

# OS specific support (must be 'true' or 'false').
cygwin=false
msys=false
darwin=false
nonstop=false
case "`uname`" in
  CYGWIN* )
    cygwin=true
    ;;
  Darwin* )
    darwin=true
    ;;
  MINGW* )
    msys=true
    ;;
  NONSTOP* )
    nonstop=true
    ;;
esac

# Attempt to set APP_HOME
# Resolve links: $0 may be a link
PRG="$0"
# Need this for relative symlinks.
while [ -h "$PRG" ] ; do
    ls=`ls -ld "$PRG"`
    link=`expr "$ls" : '.*-> \(.*\)$'`
    if expr "$link" : '/.*' > /dev/null; then
        PRG="$link"
    else
        PRG=`dirname "$PRG"`"/$link"
    fi
done
SAVED="`pwd`"
cd "`dirname \"$PRG\"`/" >/dev/null
APP_HOME="`pwd -P`"
cd "$SAVED" >/dev/null

# Add localization support.
#
# Source the UTF-8 initialization sequence.
if [ -f "$APP_HOME/bin/i18n.sh" ]; then
    . "$APP_HOME/bin/i18n.sh"
fi
# ~

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar


# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD="java"
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Increase the maximum file descriptors if we can.
if [ "$cygwin" = "false" -a "$darwin" = "false" -a "$nonstop" = "false" ] ; then
    MAX_FD_LIMIT=`ulimit -H -n`
    if [ $? -eq 0 ] ; then
        if [ "$MAX_FD" = "maximum" -o "$MAX_FD" = "max" ] ; then
            # Use the system limit
            MAX_FD="$MAX_FD_LIMIT"
        fi
        ulimit -n $MAX_FD
        if [ $? -ne 0 ] ; then
            warn "Could not set maximum file descriptor limit: $MAX_FD"
        fi
    else
        warn "Could not query maximum file descriptor limit: $MAX_FD_LIMIT"
    fi
fi

# For Darwin, add options to specify how the application appears in the dock
if $darwin; then
    GRADLE_OPTS="$GRADLE_OPTS \"-Xdock:name=$APP_NAME\" \"-Xdock:icon=$APP_HOME/media/gradle.icns\""
fi

# For Cygwin, switch paths to Windows format before running java
if $cygwin ; then
    APP_HOME=`cygpath --path --mixed "$APP_HOME"`
    CLASSPATH=`cygpath --path --mixed "$CLASSPATH"`
    JAVACMD=`cygpath --unix "$JAVACMD"`

    # We build the pattern for arguments to be converted to Windows paths
    ROOTDIRSRAW=`find -L / -maxdepth 1 -mindepth 1 -type d 2>/dev/null`
    SEP=""
    for dir in $ROOTDIRSRAW ; do
        ROOTDIRS="$ROOTDIRS$SEP$dir"
        SEP="|"
    done
    OURCYGPID=`$$`
    ACCEPTABLE_FINDS=`find / -maxdepth 1 -mindepth 1 -type d 2>/dev/null | egrep -v '^(/(cygdrive|dev|proc|var|usr|tmp))$'`
    if [ -n "$ACCEPTABLE_FINDS" ] ; then
        CYGHOME=`cygpath -w "$HOME"`
    fi
    convert_path_pattern="^(($ROOTDIRS|.)?/(cygdrive|dev|proc|var|usr|tmp)/|($CYGHOME)?)"
    # A list of arguments that should not be converted
    do_not_convert_list=("-classpath" "-cp" "-jar" "-agentlib" "-agentpath" "-javaagent" "-splash")
    convert_arg_flag=true
    for arg in "$@" ; do
        if [ "$convert_arg_flag" = true ] ; then
            for i in "${do_not_convert_list[@]}" ; do
                if [ "$arg" = "$i" ] ; then
                    convert_arg_flag=false
                    break
                fi
            done
            if [ "$convert_arg_flag" = true ] ; then
                if echo "$arg" | egrep -q "$convert_path_pattern" ; then
                    if echo "$arg" | egrep -q '^(/(cygdrive|dev|proc|var|usr|tmp))' ; then
                        echo "The argument '$arg' has absolute path using canonical Cygwin path prefix, which is not supported."
                        echo "This might lead to incorrect behavior of the build."
                        echo "Please use Windows path or full path without Cygwin canonical path prefix."
                        echo "For example, use 'C:/Users/user' instead of '/cygdrive/c/Users/user'."
                    fi
                    if [ "$OURCYGPID" = "1" ] ; then
                        # This is a workaround for invoking cpptasks with faulty arguments from MSYS
                        # This can be removed if cpptasks is fixed
                        if echo "$arg" | egrep -q "^(/tmp/cc)" ; then
                            arg=`cygpath --path --mixed "$arg"`
                        fi
                    fi
                fi
                # TODO: We are unable to handle arguments in form of '-Dfoo=/path/to/bar'
                # So we are ignoring them for now
                if ! echo "$arg" | egrep -q "^-D" ; then
                    if [ "$arg" = "-d" ] || [ "$arg" = "-p" ] ; then
                        # Argument of -d or -p should not be converted
                        convert_arg_flag=false
                    fi
                fi
            fi
        else
            convert_arg_flag=true
        fi
        new_args="$new_args \"$arg\""
    done
    set -- $new_args
fi

# Split up the JVM options only if the JDK version is JDK 9 or higher
if [ -n "$JAVA_VERSION" ] && [ "$JAVA_VERSION" -ge 9 ]; then
    DEFAULT_JVM_OPTS_ARRAY=(${DEFAULT_JVM_OPTS})
else
    DEFAULT_JVM_OPTS_ARRAY=("$DEFAULT_JVM_OPTS")
fi

# Collect all arguments for the java command, following the shell quoting and substitution rules
eval set -- "\"$JAVACMD\"" \
    "${DEFAULT_JVM_OPTS_ARRAY[@]}" \
    "-classpath" "\"$CLASSPATH\"" \
    "org.gradle.wrapper.GradleWrapperMain" \
    "\"\$@\""

# Some environments may export GRADLE_OPTS with the leading "-D" separate from the rest of the option.
#
#   e.g. GRADLE_OPTS='-Dorg.gradle.daemon=true' \
#     or GRADLE_OPTS='-D org.gradle.daemon=true'
#
# After "eval set -- ... ", the command line arguments become:
#
#   "java" "-D" "org.gradle.daemon=true" ...
#
# Using "java -D org.gradle.daemon=true ..." is not valid. The following logic is to fix this case.
new_args=""
is_pending_leading_D=false
for arg in "$@" ; do
    if $is_pending_leading_D; then
        new_args="$new_args \"-D$arg\""
    else
        if [ "$arg" = "-D" ] ; then
            is_pending_leading_D=true
        else
            new_args="$new_args \"$arg\""
        fi
    fi
done
eval set -- $new_args

"$@"
