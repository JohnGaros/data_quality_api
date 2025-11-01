# Azure Resources

## Purpose
- Provides reference templates for deploying the platform on Microsoft Azure.
- Captures security, networking, and monitoring settings agreed with cloud governance.

## Typical files
- `keyvault-config.yaml`: secrets management setup.
- `api_management.yaml`: API gateway and throttling policies.
- `app_gateway_waf.yaml`: web application firewall configuration.
- `monitor_diagnostics.yaml`: logging and telemetry collection.
- `network_rules.yaml`: virtual network and firewall rules.

## Notes for PMs and platform teams
- Treat these files as the baseline for compliance reviews.
- Any change should go through infrastructure change control and be reflected in deployment runbooks.

