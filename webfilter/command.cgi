#!/bin/sh
#
# Various hard coded commands to switch fonctionalities and retrieve values
PWD="$PWD"

[ "$1" = "" ] && exit 1
ACTION="$1"

# Get variables and source config file
#WORKING_DIR=$(echo "$DOCUMENT_ROOT$SCRIPT_NAME" | sed s/\\command.cgi//g)
[ "$WORKING_DIR" = "" ] && WORKING_DIR="$(dirname $0)"
CONFIG="config"
cd $WORKING_DIR
. $CONFIG

case "$ACTION" in
	checklogformat)
		# Check log format allows us to generate stats
		# Fix log format and logfile
		# Stores and compresses old missformated logfile
		[ ! "$(./command.cgi e2config logfileformat)" = "3" ] && {
			/etc/init.d/e2guardian stop
			uci set e2guardian.e2guardian.logfileformat=3
			uci commit
			cd /www/cgi-bin/webfilter
			./convertlog.cgi
			LOGLOCATION="$(./command.cgi e2config loglocation)"
			LOGLOCATIONEXT="$(./command.cgi fileext $LOGLOCATION)"
			CONVERTEDLOG="$(echo $LOGLOCATION | sed 's/'$LOGLOCATIONEXT'$/_convert2ls/')$LOGLOCATIONEXT"
			cp -f $LOGLOCATION $LOGLOCATION.$(date "+%Y%m%d%H%M")
			chown nobody:nogroup $LOGLOCATION.$(date "+%Y%m%d%H%M")
			gzip $LOGLOCATION.$(date "+%Y%m%d%H%M")
			cp -f $CONVERTEDLOG $LOGLOCATION
			chown nobody:nogroup $LOGLOCATION
			rm -f $CONVERTEDLOG
			/etc/init.d/e2guardian start
		}
	;;
	e2config)
		# returns E2Guardian config file path if $2 is not set
		# returns E2Guardian config file value if $2 is set
		E2GCONFIG="$E2G_CONFDIR/e2guardian.conf"
		[ "$2" == "" ] && {
			echo "$E2GCONFIG"
		} || {
			echo "$(grep -i -e "$2 = " $E2GCONFIG | \
			awk -F= '{print $2}' |  sed "s/[' ]//g")"
		}
	;;
	e2fconfig)
		# returns E2Guardian group config file path
		# group 1 is default if $2 is not set
		GROUPNUM="$2"
		[ "$2" = "" ] && GROUPNUM="1"
		echo "$E2G_CONFDIR/e2guardianf$GROUPNUM.conf"
	;;
	fileext)
		# returns file extension of the filename given
		y=${2%.*}
		echo $(basename $2) | sed 's@'${y##*/}'@@'
	;;
	loglinetype)
		# returns detected e2guardian's logtype dependending of first field given
		# takes the value of the "first field" as a parameter
		[ "$2" = "" ] && exit 1
		shift
		# Seems to be a timestamp line = squid
		[ ! "$(echo $* | grep -Eo '^[0-9]{10}[.][0-9]{3}')" = "" ] \
		&& { echo "squid" ; exit 0 ; }
		# Seems to be a e2guardian csv
		[ ! "$(echo $* | grep -Eo '^\"[0-9]{4}[.][0-9]{1,2}[.][0-9]{1,2}')" = "" ] \
		&& { echo "csv" ; exit 0 ; }
		# Seems to be a dansguardian logfile
		[ ! "$(echo $* | grep -Eo '^[0-9]{4}[.][0-9]{1,2}[.][0-9]{1,2}')" = "" ] \
		&& { echo "dansguardian" ; exit 0 ; }
	;;
	logrotate)
		# Rotate and compress last current log
		# Includes time of action into filename
		# Provides a new empty logfile
		# Returns name of rotated logfile
		LOGFILE="$(./command.cgi e2config loglocation)"
		FILEEXT="$(./command.cgi fileext $(basename $LOGFILE))"
		RKVLOGFILE="$(echo $LOGFILE | sed 's/'$FILEEXT'$/_'$(date "+%Y%m%d%H%M")$FILEEXT'/')"
		echo $RKVLOGFILE
		# Copy logfile
		cp $LOGFILE $RKVLOGFILE
		chown nobody:nogroup $LOGFILE
		chown nobody:nogroup $RKVLOGFILE
		gzip $RKVLOGFILE
		> $LOGFILE
		echo "$RKVLOGFILE.gz"
	;;
	percent)
		# returns the percentage of a work in progress
		# takes total amount of work to process as parameter $2
		# takes current amount of work already processed as parameter $3
		PERCENT=`expr $3 \* 100 / $2`
		[ "$PERCENT" -le "9" ] && PERCENT="0$PERCENT"
		echo "$PERCENT%"
	;;
	version)
		# returns version of the program
		echo "$(opkg list-installed | grep DTB_WebFilter)"
	;;
	send_file)
		# returns hexdump of file a content
		# takes filename as first parameter
		echo "$(hexdump -v -e '"\\\x" 1/1 "%02x"' $(echo $2 | sed 's/=//g'))"
	;;
	*)
		echo "Unknown command"
	;;
esac

cd $PWD
