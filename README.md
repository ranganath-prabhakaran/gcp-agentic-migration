Agentic AI Framework for MySQL to Cloud SQL Migration
Overview
This project provides a production-ready, end-to-end solution for migrating legacy MySQL databases to Google Cloud SQL. It utilizes an innovative framework of autonomous AI agents, built with Microsoft AutoGen, to orchestrate the entire migration lifecycle.

Communication and tool execution are handled securely and modularly via the Model Context Protocol (MCP), where a custom server acts as a secure bridge between the AI agents and the underlying cloud infrastructure and migration utilities.

Features
Fully Automated: End-to-end automation from infrastructure provisioning to data validation.

Intelligent & Dynamic: Automatically selects the optimal migration strategy (GCS Import, DMS, or Mydumper/Myloader) based on database size.

Secure: Uses GCP Secret Manager for all credentials and a secure MCP server to sandbox agent actions.

Resilient: Includes an anomaly detection agent to monitor for and flag errors during the process.

Self-Optimizing: A performance optimization agent provides actionable cost and performance recommendations after each run.

Infrastructure as Code: All GCP resources are managed via Terraform for reproducibility and consistency.

Prerequisites
Google Cloud Account with billing enabled.

gcloud CLI

terraform CLI

python >= 3.10

git

Setup
Clone Repository: git clone <repo_url> && cd gcp-agentic-migration

Configure Project: Edit config.py to set your GCP_PROJECT_ID.

Prepare GCP: Follow the steps in the "Environment Preparation" section of the main documentation to enable APIs and create secrets.

Provision Infrastructure: Run terraform init and terraform apply from the terraform/ directory as detailed in the documentation.

Setup VM: SSH into the migration-orchestrator-vm created by Terraform, clone the repo, and set up the Python environment:bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Usage
Start MCP Server: In one SSH session on the VM, run:

Bash

uvicorn mcp_server.server:app --host 0.0.0.0 --port 8000

Execute Migration: In a second SSH session on the VM, run the main script:

Bash

# Example for a 250 GB database using GCP recommended encryption
python main.py --volume 250 --encryption gcp-recommended