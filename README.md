# Web App and Model Deployment

## Objective
* To develop a web app and deploy models using Google Cloud Services.

---
### Start the app
Prerequisite:
* Google Cloud Account
* Google Cloud Project Owner Role

```sh
# Start the app
sh environment-variables.sh
sh app-deployment.sh # For Google Cloud Deployment
sh app-dev # For Development

# Cleanup
sh environment-variables.sh
sh cleanup.sh
```

---
* This is a development and testing repository for https://site.mattcloudtech.com.
* Repository: https://github.com/mregojos/model-deployment
* Infrastructure Automation Repository: https://github.com/mregojos/infrastructure-automation-gcp
* CI/CD Repository: https://github.com/mregojos/ci-cd-gcp