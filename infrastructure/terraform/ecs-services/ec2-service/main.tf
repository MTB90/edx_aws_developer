# Resources
resource "aws_ecs_service" "ecs_service" {
  name = var.tags["Name"]

  launch_type         = "EC2"
  cluster             = var.cluster_id
  task_definition     = var.task_definition_arn
  scheduling_strategy = "REPLICA"

  desired_count = var.capacity_limits["desired"]

  ordered_placement_strategy {
    type  = "spread"
    field = "instanceId"
  }

  dynamic "load_balancer" {
    for_each = var.tg_arn != null ? [{}] : []
    content {
      target_group_arn = var.tg_arn
      container_name   = var.container_name
      container_port   = 8080
    }
  }

  dynamic "service_registries" {
    for_each = var.service_discovery_arn != null ? [{}] : []
    content {
      registry_arn = var.service_discovery_arn
      container_name = var.container_name
      container_port = 8080
    }
  }
}