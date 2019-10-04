# Local variables
locals {
  module = "igw"
  name   = format("%s-%s", var.tags["Project"], var.tags["Envarioment"])
  tags   = merge(var.tags, map("Module", local.module, "Name", local.name))
}

# Resources
resource "aws_internet_gateway" "igw" {
  tags   = var.tags
  vpc_id = var.vpc_id
}

resource "aws_route" "igw_route" {
  route_table_id         = var.route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}
