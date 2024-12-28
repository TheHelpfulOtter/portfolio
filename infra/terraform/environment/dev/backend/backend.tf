terraform {
  backend "s3" {
    bucket = "portfolio-dev-terraform-state"
    key    = "global/s3/terraform.tfstate"
    region = "eu-west-1"
    dynamodb_table = "portfolio-dev-terraform-state-lock"
    encrypt = true
  }
}
