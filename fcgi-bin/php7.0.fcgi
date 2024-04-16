#!/bin/bash
PHPRC=$PWD/../etc/php7.0
export PHPRC
umask 022
export PHP_FCGI_CHILDREN
PHP_FCGI_MAX_REQUESTS=99999
export PHP_FCGI_MAX_REQUESTS
SCRIPT_FILENAME=$PATH_TRANSLATED
export SCRIPT_FILENAME
exec /opt/rh/rh-php70/root/usr/bin/php-cgi
