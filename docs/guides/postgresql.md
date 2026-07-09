# Postgresql management

## Create a backup

When benefits was hosted as an application service, we downloaded a copy of the django.db sqlite file to backup the db prior to deploying new migrations.

Now we generate a .json export from Postgres by running the command below from the container app console (accessible via Azure > Container App > Monitoring > Console).

```bash
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 --output db_data.json
```

!!! info

    `--natural-foreign` and `--natural-primary` are used to avoid serialization issues with the permission and authentication Django objects.

## Restore from a backup

In order to restore from a .json backup, the commands below need to be run from the container app console (accessible via Azure > Container App > Monitoring > Console).

```bash
# blows away the existing db and runs migrations
python manage.py ensure_db --reset

# seeds data from the json backup
python manage.py loaddata db_data.json
```

## Monitor server health

## Restart the server

## Provision

## Upgrade
