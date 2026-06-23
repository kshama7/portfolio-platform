terraform {
  required_version = ">= 1.5"
  required_providers {
    fly = {
      source  = "fly-apps/fly"
      version = "~> 0.0.23"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40"
    }
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.10"
    }
  }
  backend "s3" {
    bucket         = "kshama-tfstate"
    key            = "portfolio-platform/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "kshama-tflock"
  }
}

provider "fly" {
  fly_api_token = var.fly_api_token
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "grafana" {
  url  = var.grafana_cloud_url
  auth = var.grafana_cloud_api_key
}

# ─── Fly apps ────────────────────────────────────────────────────────────
resource "fly_app" "api" {
  name = "portfolio-api"
  org  = var.fly_org
}

resource "fly_app" "web" {
  name = "portfolio-web"
  org  = var.fly_org
}

# ─── DNS (Cloudflare) ────────────────────────────────────────────────────
resource "cloudflare_record" "api" {
  zone_id = var.cloudflare_zone_id
  name    = "api.portfolio"
  type    = "CNAME"
  content = "portfolio-api.fly.dev"
  proxied = true
  comment = "Managed by Terraform — portfolio-platform"
}

resource "cloudflare_record" "web" {
  zone_id = var.cloudflare_zone_id
  name    = "portfolio"
  type    = "CNAME"
  content = "portfolio-web.fly.dev"
  proxied = true
  comment = "Managed by Terraform — portfolio-platform"
}

# ─── Grafana Cloud — Prometheus scrape job ──────────────────────────────
resource "grafana_cloud_stack" "main" {
  name        = "portfolio-platform"
  slug        = "portfolioplatform"
  region_slug = "us"
}

resource "grafana_dashboard" "service_overview" {
  config_json = file("${path.module}/../../observability/grafana/dashboards/portfolio-platform.json")
  folder      = grafana_folder.platform.id
}

resource "grafana_folder" "platform" {
  title = "Portfolio Platform"
}

resource "grafana_contact_point" "pagerduty" {
  name = "pagerduty"

  pagerduty {
    integration_key = var.pagerduty_integration_key
    severity        = "critical"
  }
}

resource "grafana_notification_policy" "default" {
  group_by      = ["alertname", "service"]
  contact_point = grafana_contact_point.pagerduty.name
  group_wait    = "30s"
  group_interval = "5m"
  repeat_interval = "4h"
}
