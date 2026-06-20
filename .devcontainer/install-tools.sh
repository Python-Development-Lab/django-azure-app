#!/bin/bash
set -e

echo "=== Installing Terraform ==="
TERRAFORM_VERSION=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | python3 -c "import sys,json; print(json.load(sys.stdin)['current_version'])")
echo "Latest Terraform: $TERRAFORM_VERSION"

curl -fsSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
  -o /tmp/terraform.zip
sudo unzip -o /tmp/terraform.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/terraform
rm /tmp/terraform.zip

echo "=== Installing tflint ==="
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

echo "=== Installing Python deps ==="
pip install -r requirements.txt
pip install pytest pytest-django coverage flake8

echo "=== Versions ==="
terraform version
az version
python --version
echo "✅ All tools installed"