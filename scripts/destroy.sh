#!/bin/bash
set -e

echo "=== Django Azure Security Template — DESTROY ==="
echo "WARNING: This will delete ALL resources!"
echo "Environment: ${1:-staging}"
echo ""
echo "Type 'destroy' to confirm:"
read -r confirm

if [ "$confirm" != "destroy" ]; then
  echo "Aborted."
  exit 0
fi

cd "$(dirname "$0")/../terraform"

terraform destroy -var="environment=${1:-staging}"
echo ""
echo "=== All resources destroyed ==="
echo "State preserved in terraform.tfstate"#!/bin/bash
set -e

echo "=== Django Azure Security Template — DESTROY ==="
echo "WARNING: This will delete ALL resources!"
echo "Environment: ${1:-staging}"
echo ""
echo "Type 'destroy' to confirm:"
read -r confirm

if [ "$confirm" != "destroy" ]; then
  echo "Aborted."
  exit 0
fi

cd "$(dirname "$0")/../terraform"

terraform destroy -var="environment=${1:-staging}"
echo ""
echo "=== All resources destroyed ==="
echo "State preserved in terraform.tfstate"
