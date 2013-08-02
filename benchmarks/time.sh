#! /bin/bash
output=$1
shift
echo Running $@
echo output to $output
exec 3>&1 4>&2
var=$( { time $@ 1>&3 2>&4; } 2>&1 )  # Captures time only.
exec 3>&- 4>&-
echo $var > $output

