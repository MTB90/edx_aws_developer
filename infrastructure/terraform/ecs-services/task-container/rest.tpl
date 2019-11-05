[
  {
    "name": "${name}",
    "image": "${docker_image_uri}",
    "cpu": ${cpu_unit},
    "memory": ${memory},
    "memoryReservation": ${memory},
    "entryPoint": [
      "python"
    ],
    "command": [
      "run.py"
    ],
    "environment": [
      {
        "name": "REGION",
        "value": "${region}"
      },
      {
        "name": "DATABASE",
        "value": "${database}"
      },
      {
        "name": "STORAGE",
        "value": "${file_storage}"
      }
    ],
    "portMappings": [
      {
        "hostPort": 0,
        "protocol": "tcp",
        "containerPort": 8080
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${log_group}",
        "awslogs-region": "${region}"
      }
    },
    "workingDirectory": "${workdir}",
    "healthCheck": {
      "retries": ${var.retries},
      "command": [
        "CMD-SHELL",
        "curl -f http://localhost:8080/health || exit 1"
      ],
      "timeout": ${var.timeout},
      "interval": ${var.interval},
      "startPeriod": ${var.start_period}
    }
  }
]