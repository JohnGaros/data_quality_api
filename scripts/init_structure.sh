#!/bin/bash
# ============================================================================
# Data Quality Assessment API – Project Skeleton Initialization Script
# ============================================================================
# Creates the directory tree and placeholder files for the DQ API project.
# ============================================================================

set -e

# # --- Root folder -------------------------------------------------------------
# mkdir -p data_quality_api
# cd data_quality_api

# --- Core directories --------------------------------------------------------
mkdir -p src/{dq_core/{models,engine,report},dq_api/{routes,services},dq_config,dq_admin,dq_integration/{azure_blob,power_platform,notifications},dq_dsl/{examples},dq_tests,test_data}
mkdir -p configs/dq_rules
mkdir -p scripts
mkdir -p infra/{k8s,ci_cd}
mkdir -p docs
mkdir -p tests/{unit,integration,regression}

# --- Core engine files -------------------------------------------------------
touch src/dq_core/models/{logical_field.py,field_mapping.py,data_quality_rule.py,customer_profile.py,dq_config.py}
touch src/dq_core/engine/{rule_engine.py,evaluator.py,helpers.py}
touch src/dq_core/report/{validation_report.py,exporters.py}

# --- API layer ---------------------------------------------------------------
touch src/dq_api/routes/{uploads.py,validation.py,rules.py,tenants.py,auth.py,health.py}
touch src/dq_api/services/{job_manager.py,report_service.py,notification_service.py}
touch src/dq_api/{dependencies.py,schemas.py,middlewares.py,settings.py,app_factory.py}

# --- Configuration management ------------------------------------------------
touch src/dq_config/{loader.py,registry.py,serializers.py,validators.py}

# --- Administrative layer ----------------------------------------------------
touch src/dq_admin/{rbac.py,tenant_manager.py,audit_log.py,user_manager.py}

# --- Integrations ------------------------------------------------------------
touch src/dq_integration/azure_blob/{blob_client.py,blob_storage_config.py,blob_job_adapter.py}
touch src/dq_integration/power_platform/{powerapps_connector.py,powerbi_exporter.py,msflow_hooks.py}
touch src/dq_integration/notifications/{email_notifier.py,webhook_notifier.py,ms_teams_notifier.py}

# --- Rule DSL (future) -------------------------------------------------------
touch src/dq_dsl/{grammar.lark,parser.py,compiler.py}
touch src/dq_dsl/examples/{simple_rules.dsl,parsed_ast_example.json}

# --- Testing framework (future) ---------------------------------------------
touch src/dq_tests/{generator.py,runner.py}
touch src/dq_tests/test_cases/{rule_regression.yaml,integration_tests.yaml}
mkdir -p src/dq_tests/reports

# --- API entrypoint ----------------------------------------------------------
touch src/main.py

# --- Configuration files -----------------------------------------------------
touch configs/{example_dq_config.json,logging.yaml,settings.env}
touch configs/dq_rules/.gitkeep

# --- Scripts -----------------------------------------------------------------
touch scripts/{run_local.sh,seed_demo_data.py,migrate_db.py}
chmod +x scripts/run_local.sh

# --- Infrastructure ----------------------------------------------------------
touch infra/{Dockerfile,docker-compose.yaml}
touch infra/k8s/{api-deployment.yaml,api-service.yaml,postgres-deployment.yaml,storage-secrets.yaml}
touch infra/ci_cd/{github-actions.yaml,tests.yml,build_and_push.yaml}

# --- Documentation -----------------------------------------------------------
touch docs/{API_SPEC.md,ARCHITECTURE.md,CONFIG_GUIDE.md,INTEGRATION_GUIDE.md,ROADMAP.md}

# --- Tests -------------------------------------------------------------------
touch tests/unit/{test_rule_engine.py,test_loader.py,test_api_endpoints.py}
touch tests/integration/{test_end_to_end_upload.py,test_blob_integration.py,test_rbac.py}
touch tests/regression/.gitkeep
touch tests/conftest.py

# --- Root-level project files ------------------------------------------------
touch requirements.txt
touch pyproject.toml
touch .env.example
touch .gitignore
touch README.md

echo "✅ Data Quality Assessment API project structure created successfully."
