variable "prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "data_subnet_id" {
  type = string
}

variable "pg_dns_zone_id" {
  type = string
}

variable "tags" {
  type = map(string)
}
