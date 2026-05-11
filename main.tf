# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "marketing_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.large" # Hedefimiz burası
  
  tags = {
    Name        = "Marketing-Campaign-Test"
    Environment = "Staging"
    Owner       = "Marketing-Dept"
  }
}
