#!/usr/bin/env bash
source supervisor/REDIS.cfg
source supervisor/resolver.cfg


if [ ! -d "$RESOLVER_DIR" ]; then
	echo "Error: resolver directory $RESOLVER_DIR does not exist!"
	exit 2
fi

cd "$RESOLVER_DIR"

if [ ! -d "${RESOLVER_DIR}/${RESOLVER_NAME}/bin" ]; then
        virtualenv "$RESOLVER_NAME"
        . "${RESOLVER_NAME}/bin/activate"
else
        . "${RESOLVER_NAME}/bin/activate"
fi

rq_path="${RESOLVER_DIR}/${RESOLVER_NAME}/bin/rq"
url="redis://${REDIS_HOST}:${REDIS_PORT}/1"
queue="default" # Depends on application (Resolver); use "default" by euhm, default

exec "$rq_path" worker --url "$url" "$queue"

exit 0