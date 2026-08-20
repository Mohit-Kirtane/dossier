from unittest.mock import MagicMock, patch

from app.core.config import get_settings
from app.graph.workflow import _finish_tracewell_handlers, _tracewell_callbacks


def test_tracewell_callbacks_empty_when_unconfigured():
    get_settings.cache_clear()
    with patch.dict("os.environ", {"TRACEWELL_API_KEY": ""}):
        assert _tracewell_callbacks() == []
    get_settings.cache_clear()


def test_tracewell_callbacks_never_raises_when_handler_construction_fails():
    # Tracing is best-effort: a broken SDK, unreachable server, or local
    # network/SSL issue must never take Dossier down.
    get_settings.cache_clear()
    with patch.dict("os.environ", {"TRACEWELL_API_KEY": "tw_fake_key_for_test"}):
        with patch("tracewell_sdk.TracewellCallbackHandler", side_effect=RuntimeError("boom")):
            assert _tracewell_callbacks() == []
    get_settings.cache_clear()


def test_finish_tracewell_handlers_marks_every_handler_complete():
    handlers = [MagicMock(), MagicMock()]
    _finish_tracewell_handlers(handlers, status="complete")
    for handler in handlers:
        handler.finish.assert_called_once_with(status="complete")


def test_finish_tracewell_handlers_swallows_a_failing_handler():
    ok_handler = MagicMock()
    broken_handler = MagicMock()
    broken_handler.finish.side_effect = RuntimeError("network down")

    # Must not raise, and must still finish every other handler.
    _finish_tracewell_handlers([broken_handler, ok_handler], status="error")

    ok_handler.finish.assert_called_once_with(status="error")
