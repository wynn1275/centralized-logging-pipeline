provider "aws" {
  region = "us-east-1"
  access_key = "mockaccesskey"
  secret_key = "mocksecretkey"
  skip_credentials_validation = true
  skip_metadata_api_check = true
  skip_requesting_account_id = true
  s3_force_path_style = true
  endpoints {
    iam = "http://localhost:4593"
    s3 = "http://localhost:4572"
    kinesis = "http://localhost:4568"
    lambda = "http://localhost:4574"
    cloudwatch = "http://localhost:4582"
    cloudwatchlogs = "http://localhost:4586"
  }
}

resource "aws_kinesis_stream" "central_logging_stream" {
  name = "logging-stream"
  shard_count = 1
  retention_period = 48
}

resource "aws_s3_bucket" "log_storage" {
  bucket = "central-log"
  acl    = "private"
}

resource "aws_lambda_event_source_mapping" "kinesis_lambda_log_mapping" {
  event_source_arn = "${aws_kinesis_stream.central_logging_stream.arn}"
  function_name = "${aws_lambda_function.lambda.arn}"
  starting_position = "LATEST"
}

resource "aws_iam_role" "central-logging-role" {
  name = "lambda_kinesis_s3"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:DescribeStream",
        "kinesis:DescribeStreamSummary",
        "kinesis:GetRecords",
        "kinesis:GetShardIterator",
        "kinesis:ListShards",
        "kinesis:ListStreams",
        "kinesis:SubscribeToShard",
        "s3:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_lambda_function" "lambda" {
  filename = "${data.archive_file.access_log_parser_zip.output_path}"
  function_name = "accessLogParser"
  role = "${aws_iam_role.central-logging-role.arn}"
  handler = "access_log_parser.handler"
  runtime = "python3.8"

  source_code_hash = "${data.archive_file.access_log_parser_zip.output_base64sha256}"
  lifecycle {
    ignore_changes = ["filename", "last_modified"]
  }

}

data "archive_file" "access_log_parser_zip" {
  type = "zip"
  source_file = "${path.module}/../lambda/access_log_parser.py"
  output_path = "${path.module}/access_log_parser.zip"
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/accessLogParser"
  retention_in_days = 14
}

resource "aws_iam_policy" "lambda_logging_role" {
  name = "lambda_logging_role"
  path = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role = "${aws_iam_role.central-logging-role.name}"
  policy_arn = "${aws_iam_policy.lambda_logging_role.arn}"
}
