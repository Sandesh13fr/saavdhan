"""No-op tracing. Saavdhan sends no telemetry; call sites stay for a future local tracer."""
from contextlib import contextmanager


class _Span:
    def set_attribute(self, *_):
        pass

    def get_span_context(self):
        return type("Ctx", (), {"trace_id": 0})()


@contextmanager
def trace(*_, **__):
    yield _Span()


def span(**_):
    return lambda fn: fn


def record_usage(*_):
    pass
