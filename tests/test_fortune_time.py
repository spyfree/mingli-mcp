import json

import pytest

from mingli_mcp.core.exceptions import ValidationError
from mingli_mcp.mcp_server.tools.bazi_handlers import handle_get_bazi_fortune
from mingli_mcp.mcp_server.tools.ziwei_handlers import (
    handle_get_ziwei_chart,
    handle_get_ziwei_fortune,
)

ARGS = dict(birth_date="1990-06-15", time_index=6, gender="男", format="json")
HANDLERS = [handle_get_bazi_fortune, handle_get_ziwei_fortune]


def ganzhi(result):
    if "liu_nian" in result:
        return result["liu_nian"]["gan_zhi"]
    return result["yearly"]["heavenly_stem"] + result["yearly"]["earthly_branch"]


@pytest.mark.parametrize("handler", HANDLERS)
@pytest.mark.parametrize(
    "year,before,after",
    [
        (2027, "丙午", "丁未"),
        (2030, "己酉", "庚戌"),
        (2033, "壬子", "癸丑"),
        (2036, "乙卯", "丙辰"),
    ],
)
def test_whole_year_covers_both_years_without_daily_evidence(handler, year, before, after):
    result = json.loads(handler(dict(ARGS, query_year=year)))
    first, second = result["periods"]
    assert first["valid_from"] == f"{year}-01-01"
    assert first["valid_until_exclusive"] == second["valid_from"]
    assert second["valid_until_exclusive"] == f"{year + 1}-01-01"
    assert [ganzhi(first), ganzhi(second)] == [before, after]
    assert first["time_basis"]["effective_year"] == year - 1
    assert second["time_basis"]["effective_year"] == year
    assert all("daily" not in p and "monthly" not in p for p in result["periods"])


def test_date_query_preserves_distinct_boundaries():
    bazi, ziwei = [json.loads(h(dict(ARGS, query_date="2027-02-05"))) for h in HANDLERS]
    assert ganzhi(bazi) == "丁未"
    assert ganzhi(ziwei) == "丙午"
    assert bazi["time_basis"]["year_boundary"] == "li_chun_day"
    assert ziwei["time_basis"]["year_boundary"] == "lunar_new_year"
    assert bazi["time_basis"]["effective_year"] == 2027
    assert ziwei["time_basis"]["effective_year"] == 2026


@pytest.mark.parametrize("handler", HANDLERS)
@pytest.mark.parametrize(
    "extra",
    [
        dict(query_year=2033, query_date="2033-01-01"),
        dict(query_year=True),
        dict(query_year="2033"),
        dict(query_year=2101),
        dict(query_date=""),
        dict(query_date="2033"),
    ],
)
def test_invalid_query_is_not_replaced_with_today(handler, extra):
    with pytest.raises((ValidationError, ValueError)):
        handler(dict(ARGS, **extra))


def test_json_chart_explains_lunar_ganzhi():
    chart = json.loads(
        handle_get_ziwei_chart(dict(date="1990-06-15", time_index=6, gender="男", format="json"))
    )
    assert "农历干支" in chart["basic_info"]
    assert "四柱" not in chart["basic_info"]
    assert "节令" in chart["basic_info"]["干支口径"]
