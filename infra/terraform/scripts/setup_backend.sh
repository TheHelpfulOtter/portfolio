#!/bin/bash
# Run this script from `infra/terraform` directory

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425?permalink_comment_id=3935570
set -euo pipefail

TERRAFORM_DIR="$(pwd)" 

# =============================================
# Validation
# =============================================
if [ $# -ne 2 ]; then
    echo "Usage: $0 <action> <environment>"
    echo "Available actions: plan, apply"
    echo "Available environments: dev, uat, prod"
    exit 1
fi

ACTION=$1
ENVIRONMENT=$2

case "$ACTION" in
    plan|apply)
        echo "Valid action: $ACTION"
        ;;
    *)
        echo "Invalid action: $ACTION"
        echo "Available actions: plan, apply"
        exit 1
        ;;
esac

case $ENVIRONMENT in
    dev|uat|prod)
        echo "Valid environment: $ENVIRONMENT"
        ;;
    *) 
        echo "Invalid environment: $ENVIRONMENT"
        echo "Available environments: dev, uat, prod"
        exit 1
        ;;
esac

BACKEND_DIR="$TERRAFORM_DIR/environment/${ENVIRONMENT}/backend"

if [ ! -f "$BACKEND_DIR/backend.tf" ]; then
    echo "Error: backend.tf not found"
    exit 1
fi

# # =============================================
# # Restore backend.tf from previous run 
# # =============================================
restore_backend_tf() {
    if [ -f "$BACKEND_DIR/backend.tf.bak" ]; then
        echo "📝 Restoring backend.tf from backup..."
        mv "$BACKEND_DIR/backend.tf.bak" "$BACKEND_DIR/backend.tf"
    fi
}
trap restore_backend_tf EXIT

# # =============================================
# # Run the terraform command
# # =============================================
if [ "$ACTION" == "plan" ]; then
    echo "📝 Planning resources for backend..."
    mv "$BACKEND_DIR/backend.tf" "$BACKEND_DIR/backend.tf.bak"
    terraform -chdir=$BACKEND_DIR init
    terraform -chdir=$BACKEND_DIR plan
    mv "$BACKEND_DIR/backend.tf.bak" "$BACKEND_DIR/backend.tf"
    exit 0
else
    echo "🛠️ Creating resources for backend..."
    mv "$BACKEND_DIR/backend.tf" "$BACKEND_DIR/backend.tf.bak"
    terraform -chdir=$BACKEND_DIR init
    terraform -chdir=$BACKEND_DIR apply --auto-approve

    echo "⚙️ Configuring remote backend..."
    mv "$BACKEND_DIR/backend.tf.bak" "$BACKEND_DIR/backend.tf"
    terraform -chdir=$BACKEND_DIR init -reconfigure
    terraform -chdir=$BACKEND_DIR apply --auto-approve
fi
