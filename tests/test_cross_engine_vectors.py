"""跨引擎金标向量：本服务与官网 (spyfree/mingli) 必须排出同一张四柱盘。

同一批用户既会在官网排盘，也会用插件连这个 MCP 服务。两端盘不一致就是产品事故——
用户看到两个日主、两套十神，只会认为产品算错了。

向量表 docs/cross-engine-vectors.json 在两个仓库各存一份（内容必须逐字一致），
它同时也是口径的书面记录：时辰中点映射、交节换柱、晚子时换日各走哪一派。
任何一端要改口径，先改那张表、两边同步，再改代码。
"""

import json
from pathlib import Path

import pytest

from mingli_mcp.systems.bazi.bazi_system import (
    DAY_BOUNDARY_SECT,
    HOUR_BY_TIME_INDEX,
    BaziSystem,
)

VECTOR_FILE = Path(__file__).resolve().parents[1] / "docs" / "cross-engine-vectors.json"
VECTORS = json.loads(VECTOR_FILE.read_text(encoding="utf-8"))


def _birth_info(vector):
    payload = vector["input"]
    info = {
        "date": payload["date"],
        "time_index": payload["timeIndex"],
        "gender": payload["gender"],
        "calendar": payload["calendar"],
    }
    if payload.get("isLeapMonth"):
        info["is_leap_month"] = True
    return info


@pytest.fixture(scope="module")
def system():
    return BaziSystem()


@pytest.mark.parametrize("vector", VECTORS["vectors"], ids=lambda v: v["id"])
def test_matches_shared_vector(system, vector):
    """四柱与官网逐柱相同"""
    chart = system.get_chart(_birth_info(vector))
    pillars = chart["pillars"]
    actual = {
        "year": pillars["year"]["pillar"],
        "month": pillars["month"]["pillar"],
        "day": pillars["day"]["pillar"],
        "hour": pillars["hour"]["pillar"],
    }
    assert actual == vector["expect"], vector["note"]


def test_hour_mapping_matches_contract():
    """时辰中点映射与向量表声明一致（取起点会在交节当天排出不同月柱）"""
    declared = {
        int(k): v
        for k, v in VECTORS["conventions"]["hourFromTimeIndex"].items()
        if not k.startswith("$")
    }
    assert HOUR_BY_TIME_INDEX == declared


def test_day_boundary_sect_matches_contract():
    """晚子时走子初换日：lunar_python 的 sect=1，其默认 sect=2 是夜子时派"""
    assert VECTORS["conventions"]["dayBoundary"]["school"] == "子初换日"
    assert DAY_BOUNDARY_SECT == 1


def test_late_zi_advances_the_day_pillar(system):
    """23:00 与前一个时辰跨日：亥时留当日、晚子时进次日，且与次日早子时同柱"""
    base = {"date": "2024-01-15", "gender": "男", "calendar": "solar"}
    hai = system.get_chart({**base, "time_index": 11})
    late_zi = system.get_chart({**base, "time_index": 12})
    early_zi = system.get_chart(
        {"date": "2024-01-16", "gender": "男", "calendar": "solar", "time_index": 0}
    )

    assert hai["pillars"]["day"]["pillar"] == "戊寅"
    assert late_zi["pillars"]["day"]["pillar"] == "己卯"
    assert late_zi["pillars"]["day"]["pillar"] == early_zi["pillars"]["day"]["pillar"]
