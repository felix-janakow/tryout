import os
import json
import logging
from flask import Flask, request, jsonify
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_secrets_manager_sdk.secrets_manager_v2 import SecretsManagerV2
from ibm_code_engine_sdk.code_engine_v2 import CodeEngineV2
from ibm_code_engine_sdk.code_engine_v2 import ReplaceSecretOptions
from ibm_code_engine_sdk.code_engine_v2 import SecretDataTLSSecretData

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class Service:
    def __init__(self):
        self.authenticator = IAMAuthenticator(os.getenv("IAM_API_KEY"))
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
        if response.get("resources") and response["resources"][0]["secret_type"] == "imported_cert":
            cert_data = response["resources"][0]
            logging.info("Fetched secret from Secrets Manager")
            return cert_data
        else:
            raise Exception("Unsupported secret type or empty response")

    def update_secret_in_cluster(self, secret):
        project_id = os.getenv("CE_PROJECT_ID")
        ce_secret_name = os.getenv("CE_SECRET")

        tls_data = SecretDataTLSSecretData(
            tls_cert=secret["certificate"],
            tls_key=secret["private_key"]
        )

        options = ReplaceSecretOptions(
            project_id=project_id,
            name=ce_secret_name,
            if_match="*",
            format="tls",
            data=tls_data
        )

        self.ce_client.replace_secret(options)
        logging.info("Secret updated in Code Engine")


@app.route("/", methods=["POST"])
def handle_notification():
    logging.info("Received notification")
    payload = request.get_json()

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
