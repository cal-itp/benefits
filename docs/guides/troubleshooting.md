# Troubleshooting

## Tools

### Monitoring

We have [ping tests](https://docs.microsoft.com/en-us/azure/azure-monitor/app/monitor-web-app-availability) set up to notify about availability of each [environment](../explanation/infrastructure.md#environments). Alerts go to [#benefits-notify](https://cal-itp.slack.com/archives/C022HHSEE3F).

### Logs

#### Azure Container App Logs

In the Azure Portal, in the Container App, you can find real time logs under Monitoring > Log stream and historical logs under Monitoring > Logs

For some pre-defined queries, click `Queries`, then `Group by: Query type`, and look under `Query pack queries`.

#### Live tail

After [setting up the Azure CLI](../explanation/infrastructure.md#making-changes), you can use the following command to [stream live logs](https://learn.microsoft.com/en-us/azure/container-apps/log-streaming?tabs=bash):

```sh
az containerapp logs show --resource-group RG-CDT-PUB-VIP-CALITP-P-001 --name ca-cdt-pub-vip-calitp-p-web --tail 10 >&1 | grep -v /healthcheck
```

### Sentry

Cal-ITP's Sentry instance collects both [errors ("Issues")](https://sentry.calitp.org/organizations/sentry/issues/?project=3) and app [performance info](https://sentry.calitp.org/organizations/sentry/performance/?project=3).

[Alerts are sent to `#benefits-notify` in Slack.](https://sentry.calitp.org/organizations/sentry/alerts/rules/benefits/9/details/) [Others can be configured.](https://sentry.calitp.org/organizations/sentry/alerts/rules/)

You can troubleshoot Sentry itself by [turning on debug mode](../reference/environment-variables.md#django_debug) and visiting `/error/`.

## Specific issues

### Terraform lock

[General info](https://developer.hashicorp.com/terraform/language/state/locking)

If Terraform commands fail (locally or in the Pipeline) due to an `Error acquiring the state lock`:

1. Check the `Lock Info` for the `Created` timestamp. If it's **in the past ten minutes** or so, that probably means Terraform is still running elsewhere, and you should wait (stop here).
1. **Are any [GitHub action runs](https://github.com/cal-itp/benefits/actions/workflows/deploy.yml) stuck?** If so, cancel that build, and try re-running the Terraform command.
1. **Do any engineers have a Terrafrom command running locally?** You'll need to ask them. For example: They may have started an `apply` and it's sitting waiting for them to [approve](https://developer.hashicorp.com/terraform/cli/commands/apply#automatic-plan-mode) it. They will need to (gracefully) exit for the lock to be released.
1. **If none of the steps above identified the source of the lock**, and especially if the `Created` time is more than ten minutes ago, that probably means the last Terraform command didn't release the lock. You'll need to grab the `ID` from the `Lock Info` output and [force unlock](https://developer.hashicorp.com/terraform/language/state/locking#force-unlock).

### App fails to start

If the container fails to start, you should see a [downtime alert](#monitoring). Assuming this app version was working in another [environment](../explanation/infrastructure.md#environments), the issue is likely due to misconfiguration. Some things you can do:

- Check the [logs](#logs)
- Ensure the [environment variables](../reference/environment-variables.md) and [configuration data](../tutorials/load-sample-data.md) are set properly.
- [Turn on debugging](../reference/environment-variables.md#django_debug)
- Force-push/revert the [environment](../explanation/infrastructure.md#environments) branch back to the old version to roll back

### Littlepay API issue

Littlepay API issues may show up as:

- The [monitor](https://github.com/cal-itp/benefits/actions/workflows/check-api.yml) failing
- The `Connect your card` button doesn't work

A common problem that causes Littlepay API failures is that the certificate expired. To resolve:

1. Reach out to <support@littlepay.com>
1. Receive a new certificate
1. Put that certificate into the [configuration data](../tutorials/load-sample-data.md) and/or the [GitHub Actions secrets](https://github.com/cal-itp/benefits/settings/secrets/actions)

### Eligibility Server

It would be unexpected, but a <kbd>403</kbd> error calling the [Eligibility Server](https://docs.calitp.org/eligibility-server/) would indicate that the outbound IP address has changed, and that the new IP is not on the Eligibility Server firewall's allowlist.

1. Retrieve the _IP address_ value from the _Public IP address_ resource in the Azure Portal for the relevant environment.
1. Update the IP address:
   1. Go to the [Eligibility Server Pipeline](https://dev.azure.com/mstransit/courtesy-cards/_build?definitionId=2&_a=summary)
   1. Click `Edit`
   1. Click `Variables`
   1. Update the relevant variable with the new public IP address

Note there is nightly downtime as the [Eligibility Servers](https://docs.calitp.org/eligibility-server/) restart and load new data.
