import os
from google.cloud import secretmanager
from google.auth import default as auth_default
from dotenv import load_dotenv

load_dotenv()


secrets = secretmanager.SecretManagerServiceClient()
creds, project_id = auth_default()
print(f"\n****\nproject_id: {project_id}\n\n")


def set_secret_to_env():
    print(f"projects/{project_id}/secrets/{os.getenv('AUTH_KEY_SALT_NAME')}/versions/latest")
    if os.getenv('AUTH_KEY_SALT_NAME'):
        auth_key_salt = secrets.access_secret_version(
            request={"name": f"projects/{project_id}/secrets/{os.getenv('AUTH_KEY_SALT_NAME')}/versions/latest"},
            timeout=10
        ).payload.data.decode("utf-8")
        print(f"AUTH_KEY_SALT: {auth_key_salt}\n")
        os.environ['AUTH_KEY_SALT'] = auth_key_salt

    if os.getenv('JWT_SECRET_KEY_NAME'):
        auth_jwt_secret = secrets.access_secret_version(
            request={"name": f"projects/{project_id}/secrets/{os.getenv('JWT_SECRET_KEY_NAME')}/versions/latest"},
            timeout=10
        ).payload.data.decode("utf-8")
        print(f"AUTH_JWT_SECRET: {auth_jwt_secret}\n")
        os.environ['JWT_SECRET_KEY'] = auth_jwt_secret
