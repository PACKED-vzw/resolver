#
# Regular cron jobs for the resolver package
#
0 4	* * *	root	[ -x /usr/bin/resolver_maintenance ] && /usr/bin/resolver_maintenance
