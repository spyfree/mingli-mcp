"""Date-level fortune boundaries and explicit calendar-year queries.

The public tools accept dates (not instants). BaZi retains its existing
Li-Chun-day convention; Ziwei follows the lunar new year in iztro-py 0.5.
"""

from datetime import datetime
from typing import Any, Callable, Dict

from lunar_python import Lunar, Solar

from mingli_mcp.core.exceptions import ValidationError
from mingli_mcp.utils.validators import MAX_YEAR, MIN_YEAR


def year_boundary(year: int, system: str) -> datetime:
    if system == "bazi":
        solar = Solar.fromYmd(year, 6, 1).getLunar().getJieQiTable()["立春"]
    else:
        solar = Lunar.fromYmd(year, 1, 1).getSolar()
    return datetime(solar.getYear(), solar.getMonth(), solar.getDay())


def fortune_time_basis(query_date: datetime, system: str) -> Dict[str, Any]:
    date = query_date.replace(hour=0, minute=0, second=0, microsecond=0)
    year = date.year if date >= year_boundary(date.year, system) else date.year - 1
    return {
        "query_scope": "date",
        "calendar_year": date.year,
        "effective_year": year,
        "year_boundary": "li_chun_day" if system == "bazi" else "lunar_new_year",
        "precision": "date",
        "valid_from": year_boundary(year, system).strftime("%Y-%m-%d"),
        "valid_until_exclusive": year_boundary(year + 1, system).strftime("%Y-%m-%d"),
        "note": "有效区间仅描述流年干支，不代表月、日运势或整个公历年；八字按立春日换年，紫微按农历正月初一换年。",
    }


def calendar_year_fortune(
    year: Any, system: str, get_fortune: Callable[[datetime], Dict[str, Any]]
) -> Dict[str, Any]:
    if type(year) is not int or not MIN_YEAR <= year <= MAX_YEAR:
        raise ValidationError(f"query_year 必须是 {MIN_YEAR}–{MAX_YEAR} 的整数")
    boundaries = [datetime(year, 1, 1), year_boundary(year, system), datetime(year + 1, 1, 1)]
    periods = []
    for start, end in zip(boundaries, boundaries[1:]):
        result = get_fortune(start)
        # A yearly query intentionally provides no day/month evidence. Avoid
        # duplicating natal charts and making a representative day look annual.
        keys = (
            ("liu_nian", "da_yun", "relations_with_natal")
            if system == "bazi"
            else ("yearly", "decadal")
        )
        periods.append(
            {
                "valid_from": start.strftime("%Y-%m-%d"),
                "valid_until_exclusive": end.strftime("%Y-%m-%d"),
                "time_basis": result["time_basis"],
                **{key: result[key] for key in keys if key in result},
            }
        )
    return {
        "query_scope": "calendar_year",
        "query_year": year,
        "periods": periods,
        "note": "公历全年按换年边界分段。各段流年分别解释，不得用年初干支代表全年；大运为各段起始日期的背景，不提供日月运势。",
    }


def annual_markdown(result: Dict[str, Any]) -> str:
    import json

    return (
        f"# {result['query_year']} 公历全年运势（分段）\n\n{result['note']}\n\n```json\n"
        + json.dumps(result, ensure_ascii=False, indent=2)
        + "\n```"
    )
