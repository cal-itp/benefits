# Azure

[dev-benefits.calitp.org](https://dev-benefits.calitp.org) is currently deployed into a Microsoft Azure account provided by [California Department of Technology (CDT)'s Office of Enterprise Technology (OET)](https://techblog.cdt.ca.gov/2020/06/cdt-taking-the-lead-in-digital-transformation/), a.k.a. the "DevSecOps" team. More specifically, it uses [custom containers](https://docs.microsoft.com/en-us/azure/app-service/configure-custom-container) on [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/overview).

## Architecture

### System interconnections

```mermaid
flowchart LR
    dmv[DMV Eligibility Verification API]
    benefits[Benefits application]
    style benefits stroke-width:5px
    recaptcha[Google reCAPTCHA]
    rider((User))

    rider --> benefits
    rider --> Login.gov
    rider --> recaptcha
    rider --> Littlepay

    benefits <--> Login.gov
    benefits <--> recaptcha
    benefits --> dmv
    benefits --> Amplitude
    benefits <--> Littlepay
```

### Benefits application

```mermaid
flowchart LR
    internet[Public internet]
    WAF
    django[Django application]
    interconnections[Other system interconnections]

    internet --> Cloudflare
    Cloudflare --> WAF
    django <--> interconnections

    subgraph Azure
        WAF --> NGINX

        subgraph App Service
            subgraph Custom container
                direction TB
                NGINX --> django
            end
        end
    end
```

WAF: [Web Application Firewall](https://azure.microsoft.com/en-us/services/web-application-firewall/)
