import os
from functools import lru_cache

import hvac


REQUIRED_DATABASE_SECRET_KEYS = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]


class VaultSecretError(RuntimeError):
    """
    Ошибка получения секретов из Hashicorp Vault.
    """


def get_required_env(name: str) -> str:
    """
    Получает обязательную переменную окружения.
    """
    value = os.getenv(name)

    if not value:
        raise VaultSecretError(f"Environment variable {name} is not set")

    return value


@lru_cache
def get_database_secrets() -> dict[str, str]:
    """
    Получает параметры подключения к PostgreSQL из Hashicorp Vault.

    В ЛР3 сервис модели не использует пароль БД напрямую из исходного кода.
    Секреты читаются из Vault по пути secret/data/database/postgres.
    """
    vault_addr = get_required_env("VAULT_ADDR")
    vault_token = get_required_env("VAULT_TOKEN")

    vault_kv_mount = os.getenv("VAULT_KV_MOUNT", "secret")
    vault_db_secret_path = os.getenv("VAULT_DB_SECRET_PATH", "database/postgres")

    client = hvac.Client(
        url=vault_addr,
        token=vault_token,
    )

    if not client.is_authenticated():
        raise VaultSecretError("Vault authentication failed")

    try:
        response = client.secrets.kv.v2.read_secret_version(
            mount_point=vault_kv_mount,
            path=vault_db_secret_path,
        )
    except Exception as error:
        raise VaultSecretError(
            f"Failed to read database secrets from Vault: {error}"
        ) from error

    secrets = response["data"]["data"]

    missing_keys = [
        key for key in REQUIRED_DATABASE_SECRET_KEYS
        if key not in secrets or secrets[key] in (None, "")
    ]

    if missing_keys:
        raise VaultSecretError(
            f"Missing database secrets in Vault: {missing_keys}"
        )

    return {
        key: str(secrets[key])
        for key in REQUIRED_DATABASE_SECRET_KEYS
    }