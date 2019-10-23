# Resources
resource "aws_lambda_function" "thumbnail_lambda" {
  filename      = var.lambda_source
  function_name = var.tags["Name"]
  role          = aws_iam_role.lambda_role.arn
  handler       = var.lambda_handler

  source_code_hash = filebase64sha256(var.lambda_source)
  runtime          = "python3.7"

}

resource "aws_iam_role" "lambda_role" {
  name               = format("%s-iam-role", var.tags["Name"])
  tags               = merge(var.tags, map("Name", format("%s-iam-role", var.tags["Name"])))
  assume_role_policy = file("${path.module}/../lambda-assume-role.json")
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_policy" "lambda_policy" {
  name        = format("%s-iam-policy", var.tags["Name"])
  path        = "/"
  description = "Policy for the Lambda Role."

  policy = data.template_file.template_instance_role.rendered
}

data "template_file" "template_instance_role" {
  template = file("${path.module}/lambda-role.json.tpl")

  vars = {
    storage = var.file_storage
  }
}