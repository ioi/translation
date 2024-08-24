#!/bin/sh
# A script for printing on the server
# When a worker has server-side printing enabled, it calls this
# script as "./print.sh <worker> <file>"

set -e
if [ $# != 2 ] ; then
	echo >&2 "Usage: $0 <worker> <file>"
	exit 1
fi

# XXX: You need to customize this

# Stderr is connected to gunicorn error log
echo >&2 "PRINT: Called with $@"

exit 1
