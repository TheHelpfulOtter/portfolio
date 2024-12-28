variable "region" {
  description = "The AWS region to deploy to."
  type        = string
  default     = "eu-west-1"
}

variable "environment" {
  description = "The environment to deploy to."
  type        = string
  default     = "dev"
}

variable "backend_bucket_name" {
  description = "The name of the S3 bucket to store the Terraform state."
  type        = string
  default     = "portfolio-dev-terraform-state"
}

variable "backend_dynamodb_table_name" {
  description = "The name of the DynamoDB table to store the Terraform state lock."
  type        = string
  default     = "portfolio-dev-terraform-state-lock"
}

variable "purpose" {
  description = "The purpose of this resource."
  type        = string
  default     = "Resources for storing the Terraform backend state."
}

