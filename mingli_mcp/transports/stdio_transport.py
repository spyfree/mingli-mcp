"""
标准输入输出传输层

用于Cursor等IDE的MCP集成
"""

import json
import logging
import sys
from typing import Any, Dict, Optional

from .base_transport import BaseTransport

logger = logging.getLogger(__name__)

PARSE_ERROR_RESPONSE = {
    "jsonrpc": "2.0",
    "error": {"code": -32700, "message": "Parse error"},
    "id": None,
}


class StdioTransport(BaseTransport):
    """标准输入输出传输层"""

    def __init__(self):
        super().__init__()
        self.running = False

    def start(self) -> None:
        """启动stdio传输层，开始处理消息循环

        解析失败的行会返回-32700 Parse error并继续处理后续消息，
        只有stdin EOF才会结束循环。
        """
        self.running = True
        logger.info("Stdio transport started")

        try:
            while self.running:
                line = sys.stdin.readline()
                if not line:
                    logger.info("Received EOF on stdin")
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    message = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    self.send_message(dict(PARSE_ERROR_RESPONSE))
                    continue

                logger.debug(f"Received message: {line[:200]}...")
                response = self.handle_message(message)
                if response is not None:
                    self.send_message(response)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception:
            logger.exception("Error in message loop")
        finally:
            self.stop()

    def stop(self) -> None:
        """停止stdio传输层"""
        self.running = False
        logger.info("Stdio transport stopped")

    def send_message(self, message: Dict[str, Any]) -> None:
        """
        通过stdout发送JSON-RPC消息

        Args:
            message: 要发送的消息字典
        """
        try:
            json_str = json.dumps(message, ensure_ascii=False)
            sys.stdout.write(json_str + "\n")
            sys.stdout.flush()
            logger.debug(f"Sent message: {json_str[:200]}...")
        except Exception:
            logger.exception("Error sending message")

    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        从stdin接收JSON-RPC消息

        Returns:
            接收到的消息字典，如果到达EOF或解析失败返回None
        """
        try:
            line = sys.stdin.readline()
            if not line:
                logger.info("Received EOF on stdin")
                return None

            line = line.strip()
            if not line:
                return self.receive_message()  # 跳过空行

            message = json.loads(line)
            logger.debug(f"Received message: {line[:200]}...")
            return message
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception:
            logger.exception("Error receiving message")
            return None
