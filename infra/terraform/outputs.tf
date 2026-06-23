output "api_url" {
  value       = "https://${cloudflare_record.api.hostname}"
  description = "Public URL of the FastAPI service"
}

output "web_url" {
  value       = "https://${cloudflare_record.web.hostname}"
  description = "Public URL of the dashboard"
}

output "grafana_url" {
  value       = grafana_cloud_stack.main.url
  description = "Grafana Cloud dashboard URL"
}
