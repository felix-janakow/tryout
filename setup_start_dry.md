# Setting up the SM-TLS-Sync Tool

## Step 1: Building the image
<details> <summary> click to extend</summary>
</details>

## Step 2: Setting up a trusted profile 
<details> <summary> click to extend</summary>
</details>

## Step 3: Creating the configmap 
<details> <summary> click to extend</summary>

## 3.1 Required environment variables
The following environment variables must be configured for the configmap in the CE-Project:

### Service Endpoints
- `SM_ENDPOINT` - IBM Secrets Manager **private** service endpoint URL
- `CE_API_BASE_URL` - IBM Code Engine API base URL

### Resource Identifiers
- `CE_PROJECT_ID` - IBM Code Engine project ID
- `CE_SECRET` - Name of the TLS secret in Code Engine to update

### Authentication
- `TRUSTED_PROFILE_NAME` - Name of the IBM Cloud trusted profile (recommended)
- `IAM_API_KEY` - IBM Cloud API key (not recommended, alternative to trusted profile)


> The environment variables `CE_API_BASE_URL` and `TRUSTED_PROFILE_NAME` are predefined (if you are not changing the trusted profile name during creation) with the following values: 
> 
> |Variable|Value|
> |---|---|
> |`CE_API_BASE_URL`|https://eu-de.codeengine.cloud.ibm.com/api|
> |`TRUSTED_PROFILE_NAME`|ce-secrets-rotation|

## 3.2 Creating the configmap within the CE-Project

</details>

## Step 4: Deploying the app
<details> <summary> click to extend</summary>
</details>

## Step 5: Setting up the event notification service
<details> <summary> click to extend</summary>
</details>