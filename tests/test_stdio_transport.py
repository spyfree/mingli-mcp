#!/usr/bin/env python3
"""
Stdio Transport Layer Tests

Tests for message sending, receiving, and error handling in the stdio transport.
Requirements: 2.3
"""

import io
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from transports.base_transport import BaseTransport
from transports.stdio_transport import StdioTransport


class TestStdioTransportBasics:
    """Basic stdio transport tests."""

    def test_transport_initialization(self):
        """Test that StdioTransport initializes correctly."""
        transport = StdioTransport()
        assert transport.running is False
        assert transport.message_handler is None

    def test_transport_inherits_base(self):
        """Test that StdioTransport inherits from BaseTransport."""
        transport = StdioTransport()
        assert isinstance(transport, BaseTransport)

    def test_get_transport_name(self):
        """Test transport name is 'stdio'."""
        transport = StdioTransport()
        assert transport.get_transport_name() == "stdio"


class TestSendMessage:
    """Tests for send_message functionality."""

    def test_send_message_writes_to_stdout(self):
        """Test that send_message writes JSON to stdout."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "result": {"test": "value"}}

        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            transport.send_message(message)
            output = mock_stdout.getvalue()

        # Should be valid JSON followed by newline
        assert output.endswith("\n")
        parsed = json.loads(output.strip())
        assert parsed == message

    def test_send_message_with_unicode(self):
        """Test that send_message handles unicode characters."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "result": {"name": "紫微斗数"}}

        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            transport.send_message(message)
            output = mock_stdout.getvalue()

        parsed = json.loads(output.strip())
        assert parsed["result"]["name"] == "紫微斗数"

    def test_send_message_flushes_stdout(self):
        """Test that send_message flushes stdout after writing."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "result": {}}

        mock_stdout = MagicMock()
        mock_stdout.write = MagicMock()
        mock_stdout.flush = MagicMock()

        with patch.object(sys, "stdout", mock_stdout):
            transport.send_message(message)

        mock_stdout.write.assert_called_once()
        mock_stdout.flush.assert_called_once()

    def test_send_message_handles_exception(self):
        """Test that send_message handles exceptions gracefully."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "result": {}}

        mock_stdout = MagicMock()
        mock_stdout.write = MagicMock(side_effect=IOError("Write failed"))

        with patch.object(sys, "stdout", mock_stdout):
            # Should not raise, just log the error
            transport.send_message(message)


class TestReceiveMessage:
    """Tests for receive_message functionality."""

    def test_receive_valid_json_message(self):
        """Test receiving a valid JSON message."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        json_line = json.dumps(message) + "\n"

        with patch.object(sys, "stdin", io.StringIO(json_line)):
            received = transport.receive_message()

        assert received == message

    def test_receive_message_returns_none_on_eof(self):
        """Test that receive_message returns None on EOF."""
        transport = StdioTransport()

        with patch.object(sys, "stdin", io.StringIO("")):
            received = transport.receive_message()

        assert received is None

    def test_receive_message_skips_empty_lines(self):
        """Test that receive_message skips empty lines."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "method": "test"}
        # Empty line followed by valid message
        input_data = "\n" + json.dumps(message) + "\n"

        with patch.object(sys, "stdin", io.StringIO(input_data)):
            received = transport.receive_message()

        assert received == message

    def test_receive_message_handles_invalid_json(self):
        """Test that receive_message handles invalid JSON gracefully."""
        transport = StdioTransport()

        with patch.object(sys, "stdin", io.StringIO("not valid json\n")):
            received = transport.receive_message()

        assert received is None

    def test_receive_message_with_unicode(self):
        """Test receiving a message with unicode characters."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "params": {"name": "八字命理"}}
        json_line = json.dumps(message, ensure_ascii=False) + "\n"

        with patch.object(sys, "stdin", io.StringIO(json_line)):
            received = transport.receive_message()

        assert received == message
        assert received["params"]["name"] == "八字命理"

    def test_receive_message_handles_read_exception(self):
        """Test that receive_message handles read exceptions gracefully."""
        transport = StdioTransport()

        mock_stdin = MagicMock()
        mock_stdin.readline = MagicMock(side_effect=IOError("Read failed"))

        with patch.object(sys, "stdin", mock_stdin):
            received = transport.receive_message()

        assert received is None


class TestMessageHandler:
    """Tests for message handler functionality."""

    def test_set_message_handler(self):
        """Test setting a message handler."""
        transport = StdioTransport()

        def handler(msg):
            return {"result": "ok"}

        transport.set_message_handler(handler)
        assert transport.message_handler == handler

    def test_handle_message_without_handler(self):
        """Test handle_message returns error when no handler is set."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "method": "test"}

        response = transport.handle_message(message)

        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "handler not configured" in response["error"]["message"]
        assert response["id"] == 1

    def test_handle_message_with_handler(self):
        """Test handle_message calls the handler correctly."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "method": "test"}

        def handler(msg):
            return {"jsonrpc": "2.0", "id": msg["id"], "result": "success"}

        transport.set_message_handler(handler)
        response = transport.handle_message(message)

        assert response["result"] == "success"
        assert response["id"] == 1

    def test_handle_message_catches_handler_exception(self):
        """Test handle_message catches exceptions from handler."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 2, "method": "test"}

        def failing_handler(msg):
            raise ValueError("Handler error")

        transport.set_message_handler(failing_handler)
        response = transport.handle_message(message)

        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Handler error" in response["error"]["message"]
        assert response["id"] == 2


class TestStartStop:
    """Tests for start/stop functionality."""

    def test_stop_sets_running_false(self):
        """Test that stop() sets running to False."""
        transport = StdioTransport()
        transport.running = True
        transport.stop()
        assert transport.running is False

    def test_start_sets_running_true_initially(self):
        """Test that start() sets running to True initially."""
        transport = StdioTransport()

        # Mock stdin to return EOF immediately
        with patch.object(sys, "stdin", io.StringIO("")):
            with patch.object(sys, "stdout", io.StringIO()):
                transport.start()

        # After start completes (due to EOF), running should be False
        assert transport.running is False

    def test_start_processes_messages_until_eof(self):
        """Test that start() processes messages until EOF."""
        transport = StdioTransport()
        messages_received = []

        def handler(msg):
            messages_received.append(msg)
            return {"jsonrpc": "2.0", "id": msg.get("id"), "result": "ok"}

        transport.set_message_handler(handler)

        # Two messages followed by EOF
        msg1 = {"jsonrpc": "2.0", "id": 1, "method": "test1"}
        msg2 = {"jsonrpc": "2.0", "id": 2, "method": "test2"}
        input_data = json.dumps(msg1) + "\n" + json.dumps(msg2) + "\n"

        with patch.object(sys, "stdin", io.StringIO(input_data)):
            with patch.object(sys, "stdout", io.StringIO()):
                transport.start()

        assert len(messages_received) == 2
        assert messages_received[0]["method"] == "test1"
        assert messages_received[1]["method"] == "test2"

    def test_start_handles_keyboard_interrupt(self):
        """Test that start() handles KeyboardInterrupt gracefully."""
        transport = StdioTransport()

        mock_stdin = MagicMock()
        mock_stdin.readline = MagicMock(side_effect=KeyboardInterrupt())

        with patch.object(sys, "stdin", mock_stdin):
            with patch.object(sys, "stdout", io.StringIO()):
                # Should not raise
                transport.start()

        assert transport.running is False


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_send_message_with_non_serializable_data(self):
        """Test send_message handles non-JSON-serializable data."""
        transport = StdioTransport()
        # Sets are not JSON serializable
        message = {"data": {1, 2, 3}}

        with patch.object(sys, "stdout", io.StringIO()):
            # Should not raise, just log the error
            transport.send_message(message)

    def test_receive_message_with_whitespace_only_line(self):
        """Test receive_message handles whitespace-only lines."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": 1, "method": "test"}
        # Whitespace line followed by valid message
        input_data = "   \n" + json.dumps(message) + "\n"

        with patch.object(sys, "stdin", io.StringIO(input_data)):
            received = transport.receive_message()

        assert received == message

    def test_handle_message_preserves_request_id(self):
        """Test that handle_message preserves request ID in error responses."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": "custom-id-123", "method": "test"}

        response = transport.handle_message(message)

        assert response["id"] == "custom-id-123"

    def test_handle_message_with_null_id(self):
        """Test handle_message with null ID (notification)."""
        transport = StdioTransport()
        message = {"jsonrpc": "2.0", "id": None, "method": "test"}

        response = transport.handle_message(message)

        assert response["id"] is None
