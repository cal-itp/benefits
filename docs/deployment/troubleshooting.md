# Troubleshooting

## Tools

### Monitoring

We have [ping tests](https://docs.microsoft.com/en-us/azure/azure-monitor/app/monitor-web-app-availability) set up to notify about availability of each [environment](../infrastructure/#environments). Alerts go to [#benefits-notify](https://cal-itp.slack.com/archives/C022HHSEE3F).

### Logs

Logs can be found a couple of places:

#### Azure App Service Logs

[Open the `Logs` for the environment you are interested in.](https://docs.google.com/document/d/11EPDIROBvg7cRtU2V42c6VBxcW_o8HhcyORALNtL_XY/edit#heading=h.6pxjhslhxwvj) The following tables are likely of interest:

- `AppServiceConsoleLogs`: `stdout` and `stderr` coming from the container
- `AppServiceHTTPLogs`: requests coming through App Service
- `AppServicePlatformLogs`: deployment information

For some pre-defined queries, click `Queries`, then `Group by: Query type`, and look under `Query pack queries`.

#### [Azure Monitor Logs](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-platform-logs)

[Open the `Logs` for the environment you are interested in.](https://docs.google.com/document/d/11EPDIROBvg7cRtU2V42c6VBxcW_o8HhcyORALNtL_XY/edit#heading=h.n0oq4r1jo7zs)

The following [tables](https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python#telemetry-type-mappings) are likely of interest:

- `requests`
- `traces`

In the latter two, you should see recent log output. Note [there is some latency](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time).

See [`Failures`](https://docs.microsoft.com/en-us/azure/azure-monitor/app/asp-net-exceptions#diagnose-failures-using-the-azure-portal) in the sidebar (or `exceptions` under `Logs`) for application errors/exceptions.

#### Live tail

After [setting up the Azure CLI](#making-changes), you can use the following command to [stream live logs](https://docs.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs#in-local-terminal):

```sh
az webapp log tail --resource-group RG-CDT-PUB-VIP-CALITP-P-001 --name AS-CDT-PUB-VIP-CALITP-P-001 2>&1 | grep -v /healthcheck
```

#### SCM

<https://as-cdt-pub-vip-calitp-p-001-dev.scm.azurewebsites.net/api/logs/docker>

## Specific issues

This section serves the [runbook](https://www.pagerduty.com/resources/learn/what-is-a-runbook/) for Benefits.

### Terraform lock

[General info](https://developer.hashicorp.com/terraform/language/state/locking)

If Terraform commands fail (locally or in the Pipeline) due to an `Error acquiring the state lock`:

1. Check the `Lock Info` for the `Created` timestamp. If it's **in the past ten minutes** or so, that probably means Terraform is still running elsewhere, and you should wait (stop here).
1. **Are any [Pipeline runs](https://calenterprise.visualstudio.com/CDT.OET.CAL-ITP/_build?definitionId=828) stuck?** If so, cancel that build, and try re-running the Terraform command.
1. **Do any engineers have a Terrafrom command running locally?** You'll need to ask them. For example: They may have started an `apply` and it's sitting waiting for them to [approve](https://developer.hashicorp.com/terraform/cli/commands/apply#automatic-plan-mode) it. They will need to (gracefully) exit for the lock to be released.
1. **If none of the steps above identified the source of the lock**, and especially if the `Created` time is more than ten minutes ago, that probably means the last Terraform command didn't release the lock. You'll need to grab the `ID` from the `Lock Info` output and [force unlock](https://developer.hashicorp.com/terraform/language/state/locking#force-unlock).

### App fails to start

If the container fails to start, you should see a [downtime alert](#monitoring). Assuming this app version was working in another [environment](../infrastructure/#environments), the issue is likely due to misconfiguration. Some things you can do:

- Check the [logs](#logs)
- Ensure the [environment variables](../../configuration/environment-variables/) and [configuration data](../../configuration/data/) are set properly.
- [Turn on debugging](../../configuration/environment-variables/#django_debug)
- Force-push/revert the [environment](../infrastructure/#environments) branch back to the old version to roll back

### Littlepay API issue

Littlepay API issues may show up as:

- The [monitor](https://github.com/cal-itp/benefits/actions/workflows/check-api.yml) failing
- The `Connect your card` button doesn't work

A common problem that causes Littlepay API failures is that the certificate expired. To resolve:

1. Reach out to <support@littlepay.com>
1. Receive a new certificate
1. Put that certificate into the [configuration data](../../configuration/data/) and/or the [GitHub Actions secrets](https://github.com/cal-itp/benefits/settings/secrets/actions)

### Eligibility Server

If the Benefits application gets a 403 error when trying to make API calls to the [Eligibility Server](https://docs.calitp.org/eligibility-server/), it may be because the outbound IP addresses changed, and the Eligibility Server firewall is still restricting access to the old IP ranges.

1. Grab the `outbound_ip_ranges` `output` values from the most recent Benefit [deployment](https://calenterprise.visualstudio.com/CDT.OET.CAL-ITP/_build?definitionId=828) to the relevant environment.
1. Update the IP ranges
   1. Go to the [Eligibility Server Pipeline](https://dev.azure.com/mstransit/courtesy-cards/_build?definitionId=1&_a=summary)
   1. Click `Edit`
   1. Click `Variables`
   1. Update the relevant variable with the new list of CIDRs

Note there is nightly downtime as the Eligibility Server restarts and loads new data.
