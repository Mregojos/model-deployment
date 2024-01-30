# Web Application

* Deployed Web App: https://www.mattcloudtech.com or https://app.mattcloudtech.com
* Generative AI (Multimodal Model) Chatbot: https://www.mattcloudtech.com/Agent or https://app.mattcloudtech.com/Agent
* AI-Powered Cloud Toolkit: https://www.mattcloudtech.com/Toolkit or https://app.mattcloudtech.com/Toolkit

---
## About
* Staging Repository for https://mattcloudtech.com

---
## Resources
* Git Repository: https://github.com/mregojos/model-deployment
* Generative AI (Multimodal Model) Deployment Repository: https://github.com/mregojos/GCP-LLM-Deployment
* Infrastructure Automation Repository: https://github.com/mregojos/infrastructure-automation-gcp
* CI/CD Repository: https://github.com/mregojos/ci-cd-gcp

---
## Setup 
* Google Cloud Account
* Google Cloud Project Owner Role

```sh
# Enviroment Variables
source environment-variables.sh
# For Google Cloud Deployment
sh app-deployment.sh 
# For Development
sh app-dev 

# Cleanup
source environment-variables.sh
sh cleanup.sh
```

---
## Disclaimer
* This project is for demonstration purposes only.
* The models in the project are works in progress and may have biases and errors.
* The author of the project is not responsible for any damages and losses resulting from the use of this project.
* This project is not endorsed or affiliated with Google Cloud Platform.