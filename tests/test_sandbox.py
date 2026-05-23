import pytest

import src.agent.sandbox as sandbox_module
from src.agent.sandbox import AgentSandbox, ResourceLimits


class FakeResource:
    RLIMIT_CPU = "cpu"
    RLIMIT_AS = "memory"

    def __init__(self):
        self.calls = []
        self.error = RuntimeError

    def setrlimit(self, limit, values):
        self.calls.append((limit, values))


def test_default_resource_limits_do_not_claim_disk_quota():
    limits = ResourceLimits()

    assert limits.disk_mb is None


def test_apply_limits_rejects_disk_limit(monkeypatch):
    fake_resource = FakeResource()
    monkeypatch.setattr(sandbox_module, "resource", fake_resource)

    with pytest.raises(NotImplementedError, match="disk_mb is not enforced"):
        AgentSandbox().apply_limits("agent-1", ResourceLimits(disk_mb=100))

    assert fake_resource.calls == []


def test_apply_limits_sets_cpu_and_memory_without_disk(monkeypatch):
    fake_resource = FakeResource()
    monkeypatch.setattr(sandbox_module, "resource", fake_resource)

    AgentSandbox().apply_limits("agent-1", ResourceLimits(cpu_time=30, memory_mb=128))

    assert fake_resource.calls == [
        ("cpu", (30, 30)),
        ("memory", (128 * 1024 * 1024, 128 * 1024 * 1024)),
    ]
