#!/bin/bash
set -e

echo "=== Django Azure Security Template — Deploy ==="
echo "Environment: ${1:-staging}"

cd "$(dirname "$0")/../terraform"

if [ ! -f terraform.tfvars ]; then
  echo "ERROR: terraform/terraform.tfvars not found"
  echo "Copy terraform.tfvars.example to terraform.tfvars and fill in values"
  exit 1
fi

terraform init
terraform plan -var="environment=${1:-staging}" -out=tfplan
echo ""
echo "Review the plan above. Proceed? (yes/no)"
read -r confirm
if [ "$confirm" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

terraform apply tfplan
echo ""
echo "=== Deploy complete ==="
terraform output
