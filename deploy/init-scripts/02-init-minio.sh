#!/bin/bash
set -e

echo "Waiting for MinIO to be ready..."
until curl -s http://minio:9000/minio/health/live > /dev/null; do
  echo "Waiting for MinIO..."
  sleep 5
done

echo "Installing MinIO client..."
wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
chmod +x /usr/local/bin/mc

echo "Configuring MinIO client..."
mc alias set minio http://minio:9000 minioadmin minioadmin

echo "Creating MinIO buckets..."

# Create contracts bucket
mc mb minio/contracts --ignore-existing
mc policy set public minio/contracts

# Create evidence bucket
mc mb minio/evidence --ignore-existing
mc policy set private minio/evidence

# Create temp bucket for AI processing
mc mb minio/temp --ignore-existing
mc policy set private minio/temp

# Create backups bucket
mc mb minio/backups --ignore-existing
mc policy set private minio/backups

echo "Setting up bucket lifecycle policies..."

# Set lifecycle policy for temp bucket (auto-delete after 24 hours)
cat > /tmp/temp-lifecycle.json << EOF
{
    "Rules": [
        {
            "ID": "DeleteTempFiles",
            "Status": "Enabled",
            "Expiration": {
                "Days": 1
            }
        }
    ]
}
EOF

mc ilm import minio/temp < /tmp/temp-lifecycle.json

# Set lifecycle policy for backups (keep for 30 days)
cat > /tmp/backup-lifecycle.json << EOF
{
    "Rules": [
        {
            "ID": "DeleteOldBackups",
            "Status": "Enabled",
            "Expiration": {
                "Days": 30
            }
        }
    ]
}
EOF

mc ilm import minio/backups < /tmp/backup-lifecycle.json

echo "MinIO buckets and policies configured successfully!"

# Verify buckets
echo "Created buckets:"
mc ls minio/