# PostgreSQL management

## Create a backup

When Benefits was hosted as an Application service, we downloaded a copy of the `django.db` SQLite file to backup the database prior to deploying new migrations. Now we generate a .json export from PostgreSQL.

The command (and all other commands in this guide) are run from the `-web` suffixed Container app console. It is accessible via Azure > Container App > Monitoring > Console > /bin/bash.

```bash
# writes the file to /calitp/app
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 --output db_data.json
```

!!! info

    `--natural-foreign` and `--natural-primary` are used to avoid serialization issues with the permission and authentication Django objects.

## Copy a backup

To manage backups, use the app container's `web-storage` mounted volume.

```bash
# copy a backup into the mounted volume
cp db_data.json /home/calitp/app/data/db_data_YYY_MM_DD.json

# copy a backup from the mounted volume
cp /home/calitp/app/data/db_data_YYY_MM_DD.json db_data.json
```

You can view the files in the mounted volume (and upload new ones) by navigating to Azure > Storage account > Data storage > Classic file shares > `web-storage` > Browse.

## Restore from a backup

In order to restore from a .json backup, run the commands below from the Container app console.

```bash
# nuke existing data and rerun migrations
python manage.py ensure_db --reset

# seed data using the .json backup
python manage.py loaddata db_data.json
```

## Monitor server health

The Overview page for the "Azure Database for PostgreSQL flexible server" database service contains a variety of helpful charts to visualize the health of the hosted DB.

![PostgreSQL health](img/postgresql-health.png)

## Restart the server

The same Overview page can also be used to <kbd>↻ Restart</kbd> the database service.

## Provision

Provisioning for the database service is codified via [terraform][]. We currently use the Burstable compute tier with 32 GiB storage capacity, 1 vCore, and 2 GiB RAM. See the [azurerm documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/postgresql_flexible_server) for more information on configuring this service.

## Upgrade

When the time comes for a major version upgrade, the Overview page for the database service also offers helpful utilities for [validating and upgrading the database](https://learn.microsoft.com/en-us/azure/postgresql/configure-maintain/how-to-perform-major-version-upgrade?tabs=portal-major-version-upgrade).

Generally we expect that the steps to be:

1. Perform a dry-run upgrade in azure to confirm that the db passes "Pre-upgrade validation"
1. Test locally with the same version of PostgreSQL to verify appropriate behavior in the application
1. Trigger the upgrade in Azure
1. Update `azurerm_postgresql_flexible_server` in [terraform][] and `terraform apply` to avoid reversion

[terraform]: https://github.com/cal-itp/benefits/blob/3a930abe827601a8b541a0d464648f6d8979eb3a/terraform/database.tf#L11-L36
