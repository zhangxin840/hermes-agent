"""Gateway-level authorization behavior."""

from types import SimpleNamespace

from gateway.config import Platform
from gateway.run import GatewayRunner
from gateway.session import SessionSource


class _PairingStore:
    def is_approved(self, platform, user_id):
        return False


def _runner():
    runner = GatewayRunner.__new__(GatewayRunner)
    runner.pairing_store = _PairingStore()
    return runner


def _clear_auth_env(monkeypatch):
    for env_var in (
        "FEISHU_ALLOWED_USERS",
        "FEISHU_GROUP_ALLOWED_USERS",
        "FEISHU_ALLOW_ALL_USERS",
        "GATEWAY_ALLOWED_USERS",
        "GATEWAY_ALLOW_ALL_USERS",
    ):
        monkeypatch.delenv(env_var, raising=False)


def test_feishu_group_allowlist_authorizes_group_chat_id(monkeypatch):
    _clear_auth_env(monkeypatch)
    monkeypatch.setenv("FEISHU_GROUP_ALLOWED_USERS", "oc_allowed")

    source = SessionSource(
        platform=Platform.FEISHU,
        chat_id="oc_allowed",
        chat_type="group",
        user_id="ou_external",
    )

    assert _runner()._is_user_authorized(source) is True


def test_feishu_group_allowlist_does_not_authorize_other_groups(monkeypatch):
    _clear_auth_env(monkeypatch)
    monkeypatch.setenv("FEISHU_GROUP_ALLOWED_USERS", "oc_allowed")

    source = SessionSource(
        platform=Platform.FEISHU,
        chat_id="oc_other",
        chat_type="group",
        user_id="ou_external",
    )

    assert _runner()._is_user_authorized(source) is False


def test_feishu_config_group_rules_authorize_registered_group_chat(monkeypatch):
    _clear_auth_env(monkeypatch)
    runner = _runner()
    runner.config = SimpleNamespace(
        platforms={
            Platform.FEISHU: SimpleNamespace(
                extra={
                    "group_rules": [
                        {"chat_id": "oc_allowed", "policy": "open", "require_mention": True}
                    ]
                }
            )
        }
    )

    source = SessionSource(
        platform=Platform.FEISHU,
        chat_id="oc_allowed",
        chat_type="group",
        user_id="ou_external",
    )

    assert runner._is_user_authorized(source) is True
