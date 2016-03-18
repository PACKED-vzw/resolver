#!/bin/bash

# Get the configuration options
source supervisor/resolver.cfg

if [ "$(id -un)" != "$RESOLVER_USER" ]; then
        echo "This script must be run as the $RESOLVER_USER user."
        exit 1
fi
exec supervisor/run_server.sh "$RESOLVER_NAME" "$RESOLVER_DIR"
exit 0
