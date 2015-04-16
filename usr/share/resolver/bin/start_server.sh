#!/bin/bash

##
# Configuration settings (EDIT THESE)
##
source /etc/resolver/resolver_server.cfg

##
# Application
# DO NOT EDIT ANYTHING BELOW THIS LINE
##############################################################################

if [ "$(id -un)" != "$RESOLVER_USER" ]; then
        echo "This script must be run as the $RESOLVER_USER user."
        exit 1
fi
exec bin/run_server.sh "$RESOLVER_NAME" "$PROXY_NAME" "$PROXY_PORT" "$RESOLVER_DIR"
exit 0
