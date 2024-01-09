#!/usr/bin/env bash

# Check for existing migrations, excluding "Initial Migration"
if alembic current | grep -q -v "Initial Migration"; then
    echo "Existing Initial migration found. Skipping initial migration."
else
    # Generate initial migration if no migration has been done
    alembic revision --autogenerate -m "Initial Migration"
    sleep 10  # Optional delay for database operations
    alembic upgrade head
fi

# Start the app
exec "$@"
