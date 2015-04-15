#!/bin/bash

##
# Configuration settings (EDIT THESE)
##
RESOLVER_USER="user"
RESOLVER_NAME="resolver_name"
PROXY_NAME="proxy_name"
PROXY_PORT="proxy_port"
RESOLVER_DIR="resolver_dir"

##
# Application
# DO NOT EDIT ANYTHING BELOW THIS LINE
##############################################################################

if [ "$(id -un)" != "$RESOLVER_USER" ]; then
        echo "This script must be run as the $RESOLVER_USER user."
        exit 1
fi
exec supervisor/run_server.sh "$RESOLVER_NAME" "$PROXY_NAME" "$PROXY_PORT" "$RESOLVER_DIR"
exit 0
