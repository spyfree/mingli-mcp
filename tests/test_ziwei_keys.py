"""
紫微规范键（P1-3）与飞星四化（P1-2）

本地化的 name 不能用来按名字定位宫位或星曜（7a24079 修的就是这个 bug），
调用方改用与语言无关的 key / *_zh 字段。
"""

import pytest
from iztro_py.data.heavenly_stems import get_mutagen

from mingli_mcp.systems import get_system
from mingli_mcp.systems.ziwei.formatter import ZiweiFormatter

BIRTH = {"date": "2000-08-16", "time_index": 2, "gender": "女"}

# 官网 src/lib/ziwei-advanced.ts 的 SIHUA_MAP（生年四化，按天干）原样抄录
SITE_SIHUA_MAP = {
    "甲": {"lu": "廉贞", "quan": "破军", "ke": "武曲", "ji": "太阳"},
    "乙": {"lu": "天机", "quan": "天梁", "ke": "紫微", "ji": "太阴"},
    "丙": {"lu": "天同", "quan": "天机", "ke": "文昌", "ji": "廉贞"},
    "丁": {"lu": "太阴", "quan": "天同", "ke": "天机", "ji": "巨门"},
    "戊": {"lu": "贪狼", "quan": "太阴", "ke": "右弼", "ji": "天机"},
    "己": {"lu": "武曲", "quan": "贪狼", "ke": "天梁", "ji": "文曲"},
    "庚": {"lu": "太阳", "quan": "武曲", "ke": "太阴", "ji": "天同"},
    "辛": {"lu": "巨门", "quan": "太阳", "ke": "文曲", "ji": "文昌"},
    "壬": {"lu": "天梁", "quan": "紫微", "ke": "左辅", "ji": "武曲"},
    "癸": {"lu": "破军", "quan": "巨门", "ke": "太阴", "ji": "贪狼"},
}


@pytest.mark.parametrize("stem_key,stem", ZiweiFormatter.HEAVENLY_STEMS.items())
def test_sihua_table_matches_site(stem_key, stem):
    stars = [ZiweiFormatter._star_name_zh(key) for key in get_mutagen(stem_key)]
    assert dict(zip(ZiweiFormatter.MUTAGEN_KEYS, stars)) == SITE_SIHUA_MAP[stem]


@pytest.fixture(scope="module")
def charts():
    ziwei = get_system("ziwei")
    return {lang: ziwei.get_chart(BIRTH, lang) for lang in ("zh-CN", "vi-VN")}


def test_palaces_and_stars_carry_canonical_keys(charts):
    chart = charts["vi-VN"]
    palace = next(p for p in chart["palaces"] if p["key"] == "surfacePalace")
    assert palace["name"] == "Thiên Di"
    assert palace["name_zh"] == "迁移宫"
    assert palace["heavenly_stem_zh"] in ZiweiFormatter.HEAVENLY_STEMS.values()
    assert palace["earthly_branch_zh"] in ZiweiFormatter.EARTHLY_BRANCHES.values()

    star = palace["major_stars"][0]
    assert star["key"].endswith("Maj")
    assert star["name"] != star["name_zh"]
    assert star["brightness_zh"] in ("庙", "旺", "得", "利", "平", "不", "陷", "")


def test_existing_localized_fields_are_unchanged(charts):
    """只增不改：name 等字段仍按 language 本地化"""
    zh = charts["zh-CN"]["palaces"]
    vi = charts["vi-VN"]["palaces"]
    assert [p["name"] for p in zh] == [p["name_zh"] for p in zh]
    assert vi[0]["name"] == "Tài Bạch" and vi[0]["heavenly_stem"] == "Mậu"


def test_birth_year_mutagen_on_stars(charts):
    """2000 庚辰年：太阳禄、武曲权、太阴科、天同忌"""
    marked = {
        star["key"]: star["mutagen_key"]
        for palace in charts["vi-VN"]["palaces"]
        for star in palace["major_stars"] + palace["minor_stars"]
        if "mutagen_key" in star
    }
    assert marked == {"taiyangMaj": "lu", "wuquMaj": "quan", "taiyinMaj": "ke", "tiantongMaj": "ji"}


def test_flying_sihua_lands_where_the_star_sits(charts):
    for chart in charts.values():
        star_palace = {
            star["key"]: palace["key"]
            for palace in chart["palaces"]
            for star in palace["major_stars"] + palace["minor_stars"]
        }
        stems = {p["key"]: p["heavenly_stem_zh"] for p in chart["palaces"]}
        assert [f["palace_key"] for f in chart["flying_sihua"]] == [
            p["key"] for p in chart["palaces"]
        ]
        for item in chart["flying_sihua"]:
            assert item["stem"] == stems[item["palace_key"]]
            site = SITE_SIHUA_MAP[item["stem"]]
            for transform in item["transforms"]:
                assert transform["star_name_zh"] == site[transform["mutagen"]]
                assert transform["to_palace_key"] == star_palace[transform["star_key"]]
                assert transform["self"] == (transform["to_palace_key"] == item["palace_key"])


def test_flying_sihua_wu_stem(charts):
    """戊干：贪狼化禄、太阴化权、右弼化科、天机化忌"""
    item = next(f for f in charts["zh-CN"]["flying_sihua"] if f["stem"] == "戊")
    assert [(t["mutagen"], t["star_key"]) for t in item["transforms"]] == [
        ("lu", "tanlangMaj"),
        ("quan", "taiyinMaj"),
        ("ke", "youbiMin"),
        ("ji", "tianjiMaj"),
    ]


def test_fortune_limits_carry_canonical_keys():
    from datetime import datetime

    fortune = get_system("ziwei").get_fortune(BIRTH, datetime(2026, 9, 23), "vi-VN")
    yearly = fortune["yearly"]
    assert yearly["heavenly_stem_zh"] == "丙" and yearly["earthly_branch_zh"] == "午"
    assert len(yearly["palace_keys"]) == 12 and yearly["palace_keys"][0].endswith("Palace")
    assert yearly["mutagen_zh"] == ["天同", "天机", "文昌", "廉贞"]
    assert yearly["mutagen_keys"] == ["tiantongMaj", "tianjiMaj", "wenchangMin", "lianzhenMaj"]
