# Rollback record Wed Nov  4 20:43:58 PST 2026
- previous production deployment: b51db3eb-9156-4af6-b62c-3e241483c869
- new commit: bb01bc8e7e0396c990c6e35ae94e313e6756c06a
- preview tested: https://preview.pnw-weather-site.pages.dev
- rollback: POST https://api.cloudflare.com/client/v4/accounts/b6dc205037fd8e8c37d5267ee61dc302/pages/projects/pnw-weather-site/deployments/b51db3eb-9156-4af6-b62c-3e241483c869/rollback (Bearer PNW_CLOUDFLARE_API_TOKEN), or Pages dashboard > Deployments > Rollback
