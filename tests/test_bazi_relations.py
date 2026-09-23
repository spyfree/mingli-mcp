"""
八字干支关系（relations / relations_with_natal）

09-22 一条线上越南语答复把「酉午」说成六合化火（午的六合是未）、把「酉酉」说成
合金（实为自刑）。关系表由代码算好提供，这里钉住口径。
"""

from itertools import combinations

import pytest

from mingli_mcp.systems import get_system
from mingli_mcp.systems.bazi.relations import find_relations, find_relations_with_natal

ZHI = "子丑寅卯辰巳午未申酉戌亥"
GAN = "甲乙丙丁戊己庚辛壬癸"


def natal(*pillars):
    return [(name, p[0], p[1]) for name, p in zip(("year", "month", "day", "hour"), pillars)]


def summarize(relations):
    return {(r["type"], "".join(m["char"] for m in r["members"])) for r in relations}


def test_reported_case_has_self_punishment_and_no_you_wu_combine():
    relations = find_relations(natal("乙酉", "丙戌", "癸酉", "戊午"))
    found = summarize(relations)

    assert ("branch_self_punishment", "酉酉") in found
    assert not any(
        r["type"] == "branch_six_combine" and {m["char"] for m in r["members"]} == {"酉", "午"}
        for r in relations
    )
    assert ("stem_five_combine", "癸戊") in found
    assert ("branch_half_combine", "午戌") in found
    assert ("branch_harm", "酉戌") in found and ("branch_harm", "戌酉") in found


def test_members_name_the_pillars():
    relations = find_relations(natal("乙酉", "丙戌", "癸酉", "戊午"))
    self_punishment = next(r for r in relations if r["type"] == "branch_self_punishment")
    assert self_punishment["members"] == [
        {"pillar": "year", "char": "酉"},
        {"pillar": "day", "char": "酉"},
    ]
    assert self_punishment["name_zh"] == "地支自刑"


def test_combines_state_element_but_never_judge_transformation():
    relations = find_relations(natal("甲子", "己丑", "丙申", "辛卯"))
    combines = [r for r in relations if "combine" in r["type"]]
    assert {r["element"] for r in combines if r["type"] == "stem_five_combine"} == {"土", "水"}
    for relation in combines:
        assert "不作判断" in relation["note"]


def test_three_combine_full_half_and_arch():
    full = summarize(find_relations(natal("甲申", "丙子", "戊辰", "庚午")))
    assert ("branch_three_combine", "申子辰") in full
    # 全局已成，不再把其中两两组合重复列为半合 / 拱合
    assert not any(t in ("branch_half_combine", "branch_arch_combine") for t, _ in full)

    arch = find_relations(natal("甲申", "丙寅", "戊辰", "庚午"))
    arch_rel = next(r for r in arch if r["type"] == "branch_arch_combine")
    assert arch_rel["missing"] == "子"
    assert arch_rel["element"] == "水"
    assert "缺子" in arch_rel["note"]

    half = next(
        r
        for r in find_relations(natal("甲子", "丙寅", "戊辰", "庚午"))
        if r["type"] == "branch_half_combine"
    )
    assert half["missing"] == "申"


def test_three_meeting_and_punishments():
    found = summarize(find_relations(natal("甲寅", "丁卯", "戊辰", "庚午")))
    assert ("branch_three_meeting", "寅卯辰") in found
    assert ("branch_harm", "卯辰") in found

    found = summarize(find_relations(natal("甲寅", "己巳", "庚申", "丙子")))
    assert ("branch_punishment", "寅巳申") in found
    found = summarize(find_relations(natal("甲子", "丁卯", "庚戌", "丙戌")))
    assert ("branch_rude_punishment", "子卯") in found
    # 戌不在自刑之列
    assert not any(t == "branch_self_punishment" for t, _ in found)


def test_relations_with_natal_only_lists_new_relations():
    base = natal("乙酉", "丙戌", "癸酉", "戊午")
    relations = find_relations_with_natal(base, [("da_yun", "庚", "子"), ("liu_nian", "丙", "午")])
    for relation in relations:
        assert {"da_yun", "liu_nian"} & {m["pillar"] for m in relation["members"]}
    found = summarize(relations)
    assert ("branch_clash", "子午") in found  # 大运子 冲 时支午 / 流年午
    assert ("branch_self_punishment", "午午") in found  # 流年午 见 时支午


# ----------------------------------------------------------------------------
# 与官网口径对照：mingli src/lib/comparison/comparison-rules.ts
# 官网表按生肖写，这里原样抄录后换算成地支比对
# ----------------------------------------------------------------------------

SITE_ZODIAC = dict(zip("鼠牛虎兔龙蛇马羊猴鸡狗猪", ZHI))
SITE_RULES = {
    "liuhe": [["鼠", "牛"], ["虎", "猪"], ["兔", "狗"], ["龙", "鸡"], ["蛇", "猴"], ["马", "羊"]],
    "sanhe": [["猴", "鼠", "龙"], ["虎", "马", "狗"], ["蛇", "鸡", "牛"], ["猪", "兔", "羊"]],
    "liuchong": [
        ["鼠", "马"],
        ["牛", "羊"],
        ["虎", "猴"],
        ["兔", "鸡"],
        ["龙", "狗"],
        ["蛇", "猪"],
    ],
    "liuhai": [["鼠", "羊"], ["牛", "马"], ["虎", "蛇"], ["兔", "龙"], ["猴", "猪"], ["鸡", "狗"]],
}
SITE_TIANGAN_HE = {
    "甲": "己",
    "己": "甲",
    "乙": "庚",
    "庚": "乙",
    "丙": "辛",
    "辛": "丙",
    "丁": "壬",
    "壬": "丁",
    "戊": "癸",
    "癸": "戊",
}
SITE_DIZHI_HE = {
    "子": "丑",
    "丑": "子",
    "寅": "亥",
    "亥": "寅",
    "卯": "戌",
    "戌": "卯",
    "辰": "酉",
    "酉": "辰",
    "巳": "申",
    "申": "巳",
    "午": "未",
    "未": "午",
}


def _site_pairs(rule):
    return {frozenset(SITE_ZODIAC[a] for a in pair) for pair in SITE_RULES[rule]}


def _pair_types(a, b):
    """两支各占一柱时成立的关系类型"""
    return {r["type"] for r in find_relations([("year", "甲", a), ("day", "甲", b)])}


@pytest.mark.parametrize(
    "rule,rel_type",
    [("liuhe", "branch_six_combine"), ("liuchong", "branch_clash"), ("liuhai", "branch_harm")],
)
def test_branch_pairs_match_site(rule, rel_type):
    ours = {frozenset((a, b)) for a, b in combinations(ZHI, 2) if rel_type in _pair_types(a, b)}
    assert ours == _site_pairs(rule)


def test_six_combine_matches_site_dizhi_he():
    ours = {a: b for a in ZHI for b in ZHI if a != b and "branch_six_combine" in _pair_types(a, b)}
    assert ours == SITE_DIZHI_HE


def test_three_combine_groups_match_site():
    ours = set()
    for trio in combinations(ZHI, 3):
        relations = find_relations([(p, "甲", z) for p, z in zip(("year", "month", "day"), trio)])
        if any(r["type"] == "branch_three_combine" for r in relations):
            ours.add(frozenset(trio))
    assert ours == {frozenset(SITE_ZODIAC[a] for a in group) for group in SITE_RULES["sanhe"]}
    # 站点 isSanhe 判的是"同属一局的两支"：我方必须把每一对都认成半合或拱合
    for group in SITE_RULES["sanhe"]:
        for a, b in combinations([SITE_ZODIAC[x] for x in group], 2):
            assert _pair_types(a, b) & {"branch_half_combine", "branch_arch_combine"}


def test_stem_five_combine_matches_site_tiangan_he():
    ours = {}
    for a in GAN:
        for b in GAN:
            if a == b:
                continue
            relations = find_relations([("year", a, "子"), ("day", b, "午")])
            if any(r["type"] == "stem_five_combine" for r in relations):
                ours[a] = b
    assert ours == SITE_TIANGAN_HE


# ----------------------------------------------------------------------------
# 接入 get_bazi_chart / get_bazi_fortune
# ----------------------------------------------------------------------------


def test_chart_and_fortune_expose_relations():
    from datetime import datetime

    bazi = get_system("bazi")
    birth = {"date": "2000-08-16", "time_index": 2, "gender": "女"}
    chart = bazi.get_chart(birth)
    pillars = [chart["pillars"][p]["pillar"] for p in ("year", "month", "day", "hour")]
    assert chart["relations"] == find_relations(natal(*pillars))

    fortune = bazi.get_fortune(birth, datetime(2026, 9, 23))
    extra = [
        ("da_yun", *fortune["da_yun"]["gan_zhi"]),
        ("liu_nian", *fortune["liu_nian"]["gan_zhi"]),
    ]
    assert fortune["relations_with_natal"] == find_relations_with_natal(natal(*pillars), extra)
