# Rollback record Wed Nov  4 18:28:53 PST 2026
- previous production deployment: 463df52a-3e9f-4fc7-8ce1-02da8f1e52e4
- new commit: 2f8b8959a5063fb8a908fab668050f6860956911
- preview tested: https://preview.pnw-weather-site.pages.dev
- rollback: POST https://api.cloudflare.com/client/v4/accounts/b6dc205037fd8e8c37d5267ee61dc302/pages/projects/pnw-weather-site/deployments/463df52a-3e9f-4fc7-8ce1-02da8f1e52e4/rollback (Bearer PNW_CLOUDFLARE_API_TOKEN), or Pages dashboard > Deployments > Rollback
- production guard OK Wed Nov  4 18:33:15 PST 2026
