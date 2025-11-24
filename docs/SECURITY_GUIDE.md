# Security Guide — Data Quality Assessment API

## 1. Purpose
- Summarise the security posture for supervisors, PMs, and engineering teams.
- Provide actionable guidance for protecting data, secrets, and access.
- Support audits by documenting controls and planned evidence.

## 2. Security principles
- **Zero trust:** authenticate and authorise every request (human or service).
- **Least privilege:** grant only the access a role or service needs.
- **Defense in depth:** layer controls (network, application, metadata logging).
- **Auditability:** capture traceable records for all sensitive actions.
- **Secure by default:** encryption, secure storage, and hardened infrastructure baked in.

## 3. Identity and access management
- OAuth2 / OpenID Connect via Azure Active Directory; tokens carry RBAC roles (`Uploader`, `Configurator`, `Admin`).
- App roles mapped to scopes that the API enforces per endpoint (see `docs/RBAC_MODEL.md`).
- Service principals for automation follow least-privilege scopes (e.g., upload-only, reporting-only).
- Just-in-time access for production Admin tasks; all break-glass use logged and reviewed.

## 4. Secrets and key management
- Azure Key Vault stores API keys, database credentials, signing keys.
- Managed Identity or short-lived credentials for services retrieving secrets.
- No secrets committed to source control; configuration files reference Key Vault identifiers.
- Periodic rotation of secrets aligned with corporate policy (e.g., every 90 days).

## 5. Data protection
- TLS 1.2+ enforced for all API and storage traffic; HTTP is redirected or rejected.
- Data at rest encrypted using Azure Storage encryption and database-native encryption.
- Uploaded files stored in isolated containers per tenant with SAS tokens or Managed Identity access.
- Metadata layer tags sensitive assets (PII/PCI/PHI) and enforces additional controls before access.

## 6. Application security controls
- Input validation and schema checks via Pydantic models and configuration validators.
- Idempotency keys on uploads prevent replay attacks.
- Rate limiting and threat protection handled by Azure API Management or equivalent gateway.
- Audit logging hooks in `dq_security.audit_logger` and `dq_metadata` capture every privileged action.
- Static code analysis and dependency scanning part of CI/CD pipeline (to be defined in `infra/ci_cd`).

## 7. Infrastructure and network
- Deployments inside Azure virtual networks with subnet isolation for API, data, and admin services.
- Web Application Firewall (WAF) in front of API endpoints to block OWASP Top 10 threats.
- Private endpoints or service endpoints for databases and storage, avoiding public exposure.
- Logging and monitoring forwarded to Azure Monitor / Log Analytics with retention aligned to compliance.

## 8. Operational security
- Runbooks include incident response steps, escalation contacts, and communication templates.
- Security alerts integrated with on-call rotations; anomalies trigger immediate review (see NFR alerts).
- Regular access reviews to confirm active users and service accounts are still required.
- Backup integrity tests and disaster recovery drills executed at least annually.

## 9. Compliance considerations
- Metadata layer produces evidence packs (audit reports, lineage, approvals) on demand, including GDPR-relevant information (lawful basis, classification tags, audit events tied to data subject requests and breach response).
- Retention policies configurable per tenant; deletion workflows logged with justification and aligned to GDPR storage limitation and erasure requirements.
- Aligns with corporate baselines (SOC 2, GDPR) — gaps tracked in `docs/STAKEHOLDER_DECISIONS.md`.
- Document data processing agreements and privacy impact assessments where applicable; ensure GDPR Article 30 records of processing activities can be derived from contracts and metadata.

## 10. Open items
- Finalise security runbook details (incident response contacts, SLA for breach notifications).
- Define vulnerability management cadence (patch schedule, penetration testing).
- Confirm logging format requirements with corporate SIEM team.
- Decide on customer-facing security communication (trust center, status page).
