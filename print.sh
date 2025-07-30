#!/bin/sh
# A script for printing on the server
# When a worker has server-side printing enabled, it calls this
# script as "./print.sh <worker> <file>"
# The file name is relative to MEDIA_ROOT.

set -e
if [ $# != 2 ] ; then
	echo >&2 "Usage: $0 <worker> <file>"
	exit 1
fi

# Stderr is connected to gunicorn error log
echo >&2 "PRINT: Called with $@"

F=media/$2

case "$1" in
	draft)
		lp -da -oDuplex=DuplexNoTumble "$F"
		;;
	final1)
		lp -da -oDuplex=DuplexNoTumble "$F"
		#lp -db -oKMDuplex=True "$F"
		;;
	final2)
		lp -da -oDuplex=DuplexNoTumble "$F"
		# lp -dc -oDuplex=DuplexNoTumble "$F"
		;;
	*)
		echo >&2 "PRINT: Unknown worker $1"
		exit 1
		;;
esac
