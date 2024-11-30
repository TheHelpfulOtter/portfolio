locals {
  tags = {
    "operations:owner"        = "devops"
    "cost-allocation:project" = "portfolio"
    "automation:environment"  = "dev"
    "automation:iac"          = "terraform"
    "cost-allocation:owner"   = "devops"
  }
}

resource "aws_s3_bucket" "s3_terraform_state" {
  bucket        = var.bucket_name
  force_destroy = false
  tags          = local.tags
}

resource "aws_s3_bucket_versioning" "s3_terraform_state_versioning" {
  bucket = aws_s3_bucket.s3_terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_terraform_state_encryption" {
  bucket = aws_s3_bucket.s3_terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "s3_terraform_state_public_access" {
  bucket = aws_s3_bucket.s3_terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "dynamodb_terraform_state_lock" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = local.tags
}
