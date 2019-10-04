provider "aws" {
  region = var.region

  s3_force_path_style         = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  skip_credentials_validation = true

  access_key = "access_key"
  secret_key = "secret_key"

  endpoints {
    s3       = "http://127.0.0.1:4572"
    dynamodb = "http://127.0.0.1:4569"
  }
}
