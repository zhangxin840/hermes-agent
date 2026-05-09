import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch


def test_gateway_lifecycle_notifications_can_be_disabled_by_env():
    from gateway.run import GatewayRunner

    with patch.dict(os.environ, {"HERMES_GATEWAY_LIFECYCLE_NOTIFICATIONS": "false"}, clear=False):
        assert GatewayRunner._load_gateway_lifecycle_notifications() is False


def test_shutdown_notifications_skip_active_and_home_channels_when_disabled():
    from gateway.config import Platform
    from gateway.run import GatewayRunner

    runner = object.__new__(GatewayRunner)
    runner._gateway_lifecycle_notifications = False
    runner._snapshot_running_agents = Mock(return_value={"agent:main:feishu:group:oc_group"})
    runner.config = SimpleNamespace(
        get_home_channel=Mock(return_value=SimpleNamespace(chat_id="oc_home", thread_id=None))
    )
    adapter = SimpleNamespace(send=AsyncMock())
    runner.adapters = {Platform.FEISHU: adapter}

    asyncio.run(GatewayRunner._notify_active_sessions_of_shutdown(runner))

    adapter.send.assert_not_awaited()
