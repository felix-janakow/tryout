# Codeengine-SM-TLS-Sync
The rotator.py script is designed to run as a Code Engine application that automatically synchronizes public TLS certificates from IBM Cloud Secrets Manager. It operates by receiving rotation events from Secrets Manager through the Event Notifications service.

**Architecture**
-----
![Goals](https://github.ibm.com/Cloud-DACH/codeengine-sm-tls-sync/assets/481326/b9881807-ece5-4008-8d61-3eb0b892e806)

**Prerequisites**
-----
### 1. IBM Cloud Account Setup
- Active IBM Cloud 
- Appropriate IAM permissions for:
  - Creating and managing Secrets Manager instances
  - Creating and managing Code Engine projects
  - Creating trusted profiles and service IDs

### 2. Required IBM Cloud Services
#### IBM Secrets Manager
- Secrets Manager instance provisioned
- A public TLS-certificate secret stored in the instance with active roation in place

#### IBM Code Engine
- Code Engine project with the app the secret will be rotated for
- TLS certificate in `Secrets and configmaps` stored within the Code Engine project where the app resides

**Environment Variables**
-----
The following environment variables must be configured for the configmap in the CE-Project:

### Service Endpoints
- `SM_ENDPOINT` - IBM Secrets Manager **private** service endpoint URL
- `CE_API_BASE_URL` - IBM Code Engine API base URL

### Resource Identifiers
- `CE_PROJECT_ID` - IBM Code Engine project ID
- `CE_SECRET` - Name of the TLS secret in Code Engine to update

### Authentication (Alternative Options)
- `TRUSTED_PROFILE_NAME` - Name of the IBM Cloud trusted profile (recommended)
- `IAM_API_KEY` - IBM Cloud API key (not recommended, alternative to trusted profile)

> [!NOTE]
> The environment variables `CE_API_BASE_URL` and `TRUSTED_PROFILE_NAME` are predefined (if you are not changing the trusted profile name during creation) with the following values: 
>
> |Variable|Value|
> |---|---|
> |`CE_API_BASE_URL`|https://eu-de.codeengine.cloud.ibm.com/api|
> |`TRUSTED_PROFILE_NAME`|ce-secrets-rotation|

> [!IMPORTANT]
> If you have trouble finding the remaining values, refer to the [Environment Variables](docs/ENV/environment_variables.md) documentation for guidance

**Setup**
-----

To start with the Setup of the TLS certificate secret rotator, navigate to the [Setup starting page](docs/SETUP/setup_start.md)

