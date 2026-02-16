if [ $(alembic heads | wc -l) -eq 1 ]; then
    echo "Only one head: OK"
else
    echo "Multiple heads are forbidden. Use 'alembic upgrade head' command before making a new revision."
    exit 1
fi
