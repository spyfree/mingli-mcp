"""
工具参数归一化

出生日期历史上有两个参数名：get_ziwei_chart / get_bazi_chart 用 date，
其余工具用 birth_date。两者现在互为别名，所有工具都接受；schema 以
birth_date 为规范名公布，date 标注为已弃用但仍接受（现有调用方仍在用）。
"""

from typing import Any, Dict

from mingli_mcp.core.exceptions import ValidationError

BIRTH_DATE_KEY = "birth_date"
DEPRECATED_BIRTH_DATE_KEY = "date"


def normalize_birth_date(args: Dict[str, Any]) -> Dict[str, Any]:
    """返回把 date 别名并入 birth_date 的参数副本；两者都给且不同则报错。"""
    normalized = dict(args)
    alias = normalized.pop(DEPRECATED_BIRTH_DATE_KEY, None)
    canonical = normalized.get(BIRTH_DATE_KEY)

    if alias is not None and canonical is not None and alias != canonical:
        raise ValidationError(
            f"birth_date 与 date 是同一参数的两个名字，但取值不同："
            f"birth_date='{canonical}'，date='{alias}'。请只传 birth_date"
        )
    if canonical is None and alias is not None:
        normalized[BIRTH_DATE_KEY] = alias
    return normalized
