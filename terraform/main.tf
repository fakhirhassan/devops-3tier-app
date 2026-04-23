# S3 bucket - created first
resource "aws_s3_bucket" "my_bucket" {
  bucket = "${var.s3_bucket_name}-${terraform.workspace}"

  tags = {
    Name        = "${var.s3_bucket_name}-${terraform.workspace}"
    Environment = terraform.workspace
  }
}

# EC2 instance - created after S3 bucket
resource "aws_instance" "my_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type

  depends_on = [aws_s3_bucket.my_bucket]

  tags = {
    Name        = "${var.project_name}-ec2-${terraform.workspace}"
    Environment = terraform.workspace
  }
}
