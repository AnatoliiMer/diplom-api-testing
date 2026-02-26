#!/bin/sh
echo "Waiting for app to be ready..."
while ! nc -z app 5000; do
  sleep 1
done
echo "App is ready!"
exec "$@"