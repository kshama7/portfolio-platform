variable "fly_api_token" {
  type      = string
  sensitive = true
}

variable "fly_org" {
  type    = string
  default = "personal"
}

variable "cloudflare_api_token" {
  type      = string
  sensitive = true
}

variable "cloudflare_zone_id" {
  type = string
}

variable "grafana_cloud_url" {
  type = string
}

variable "grafana_cloud_api_key" {
  type      = string
  sensitive = true
}

variable "pagerduty_integration_key" {
  type      = string
  sensitive = true
}
