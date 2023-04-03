#!/bin/sh
major=`cut -d. -f1 VERSION`
minor=`cut -d. -f2 VERSION`
patch=`cut -d. -f3 VERSION`

if [[ -z $1 ]]; then
	echo -n ${major}.${minor}.${patch}
else
	case $1 in
		major|maj|ma|a|1)
			echo -n $[${major}+1].${minor}.${patch} > VERSION
		;;
		minor|min|mi|i|2)
			echo -n ${major}.$[${minor}+1].${patch} > VERSION
		;;
		p|patch|3)
			echo -n ${major}.${minor}.$[${patch}+1] > VERSION
		;;
	esac
fi