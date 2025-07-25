import os
import logging
import time
from flask import Flask, abort, request, jsonify
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, ContainerAuthenticator
from ibm_secrets_manager_sdk.secrets_manager_v2 import SecretsManagerV2
from ibm_code_engine_sdk.code_engine_v2 import CodeEngineV2
from ibm_code_engine_sdk.code_engine_v2 import SecretDataTLSSecretData

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class Service:
    def __init__(self):
        
        trusted_profile_name = os.getenv("TRUSTED_PROFILE_NAME")
        self.authenticator = ContainerAuthenticator(iam_profile_name=trusted_profile_name)
        logging.info("ContainerAuthenticator created successfully")
        
        # ===================== other Authenticatio Option (not recommended) =====================
        # Uncomment the following line to use IAMAuthenticator (with API KEY) instead and comment out the 3 lines above

        # self.authenticator = IAMAuthenticator(os.getenv("IAM_API_KEY"))
        
        self.sm_client = self._init_sm_client()
        self.ce_client = self._init_ce_client()

    def _init_sm_client(self):
        sm_endpoint = os.getenv("SM_ENDPOINT")
        client = SecretsManagerV2(authenticator=self.authenticator)
        client.set_service_url(sm_endpoint)
        logging.info("Secrets Manager client initialized")
        return client

    def _init_ce_client(self):
        ce_url = os.getenv("CE_API_BASE_URL") + "/v2"
        client = CodeEngineV2(authenticator=self.authenticator)
        client.set_service_url(ce_url)
        logging.info("Code Engine client initialized")
        return client

    def get_secret(self, secret_id):
        response = self.sm_client.get_secret(id=secret_id).get_result()
        
        # ===================== Debug Logs =====================
        #WARNING: This exposes sensitive data. For testing only!

        #logging.info("Complete response from Secrets Manager:")   
        #logging.info(json.dumps(response, indent=2))              
        
        if response.get("secret_type") == "public_cert":
            cert_data = response
            logging.info("Fetched secret from Secrets Manager")
            return cert_data
        else:
            raise Exception("Unsupported secret type or empty response")

            # ===================== Debug Logs =====================
            #WARNING: This exposes sensitive data. For testing only!

            #logging.error(f"Unsupported secret type: {response.get('secret_type', 'unknown')}") #DebugLog

    def update_secret_in_cluster(self, secret):
        project_id = os.getenv("CE_PROJECT_ID")
        ce_secret_name = os.getenv("CE_SECRET")
        
        # Log the structure of the secret
        logging.info(f"Keys in secret object: {list(secret.keys())}")
        
        # Extract certificate components directly from the secret object
        certificate = secret.get("certificate", "")
        private_key = secret.get("private_key", "")
        intermediate = secret.get("intermediate", "")
        
        # Check if we found the data
        logging.info(f"Certificate found: {bool(certificate)}")
        logging.info(f"Private key found: {bool(private_key)}")
        logging.info(f"Intermediate found: {bool(intermediate)}")
        
        if not certificate:
            logging.error("Certificate not found in the response")
            raise ValueError("Certificate not found in the response")
        
        if not private_key:
            logging.error("Private key not found in the response")
            raise ValueError("Private key not found in the response")
        
        # Combine certificate with intermediate certificate chain if available
        full_certificate = certificate
        if intermediate:
            full_certificate = f"{certificate}\n{intermediate}"
            logging.info("Combined certificate with intermediate certificate")
        
        logging.info("Preparing certificate with chain for Code Engine")
        
        tls_data = SecretDataTLSSecretData(
            tls_cert=full_certificate,
            tls_key=private_key
        )

        self.ce_client.replace_secret(
            project_id=project_id,
            name=ce_secret_name,
            if_match="*",
            format="tls",
            data=tls_data
        )
        logging.info("Secret updated in Code Engine")
        
        # Add delay after successful update to prevent race conditions with subsequent requests
        time.sleep(2)


@app.route("/", methods=["POST"])
def handle_notification():
    
    # Check for the required authentication header
    expected_header_name = "Auth-SM-TLS-Sync"
    expected_header_value = "SM-TLS-Sync-Header-Verify"
    
    received_value = request.headers.get(expected_header_name)
    
    if received_value != expected_header_value:
        abort(403, "Forbidden: Invalid or missing authentication head   er")

    logging.info("Received notification")
    payload = request.get_json()

    # ===================== Debug Logs =====================
    #WARNING: This exposes sensitive data. For testing only!
    #logging.info("Payload: %s", json.dumps(payload, indent=2)) #DebugLog

    try:
        secret_id = payload["data"]["secrets"][0]["secret_id"]
    except (KeyError, IndexError) as e:
        logging.error("Invalid payload format")
        return jsonify({"error": "Invalid payload"}), 400

    service = Service()

    try:
        secret = service.get_secret(secret_id)
        service.update_secret_in_cluster(secret)
        return jsonify({"message": "Secret updated in cluster"}), 201
    except Exception as e:
        logging.error(str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
