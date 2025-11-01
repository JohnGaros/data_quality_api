#!/bin/bash
# =============================================================================
# Extend Data Quality Assessment API structure with enterprise security & Azure
# deployment components.
# =============================================================================

set -e

echo "🔧 Extending project with security and Azure infrastructure modules..."

# --- 1. Security module inside src/ ------------------------------------------
mkdir -p src/dq_security

touch src/dq_security/{auth_provider.py,rbac_middleware.py,keyvault_client.py,encryption_utils.py,audit_logger.py}

# --- 2. Azure infrastructure manifests ---------------------------------------
mkdir -p infra/azure

touch infra/azure/{keyvault-config.yaml,api_management.yaml,app_gateway_waf.yaml,monitor_diagnostics.yaml,network_rules.yaml}

# --- 3. Documentation updates ------------------------------------------------
touch docs/{SECURITY_GUIDE.md,RBAC_MODEL.md}

# --- 4. Optional: Add __init__.py for Python package discovery ----------------
touch src/dq_security/__init__.py

# --- 5. Confirmation ----------------------------------------------------------
echo "✅ Security and Azure infrastructure folders and files created successfully."
echo
echo "Created structure:"
tree -L 3 src/dq_security infra/azure docs 2>/dev/null || \
  find src/dq_security infra/azure docs -maxdepth 2 -type f