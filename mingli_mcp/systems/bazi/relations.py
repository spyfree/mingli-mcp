"""
八字干支关系

列出若干柱之间【实际构成】的干支组合：天干五合 / 相冲，地支六合、三合（全局 / 半合 /
拱合）、三会、六冲、三刑（含无礼之刑、自刑）、六害、六破。

只陈述"构成了这个组合"，不判断合化成败——合化要看月令、透干等，流派分歧大，
由解读方自行判断。type 为稳定的英文枚举、干支为简体汉字，均不随 language 变化，
供调用方做机器校验。

六合、三合、六冲、六害、天干五合与官网 src/lib/comparison/comparison-rules.ts
口径一致（见 tests/test_bazi_relations.py 的对照测试）。
"""

from itertools import combinations
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# (柱名, 字) —— 柱名 year / month / day / hour，运势里另有 da_yun / liu_nian
Member = Tuple[str, str]

COMBINE_NOTE = "只表示构成此组合；是否合化需看月令、透干等条件，此处不作判断"

# 天干五合（合化五行）
STEM_COMBINES: Dict[frozenset, str] = {
    frozenset("甲己"): "土",
    frozenset("乙庚"): "金",
    frozenset("丙辛"): "水",
    frozenset("丁壬"): "木",
    frozenset("戊癸"): "火",
}

# 天干相冲（戊己居中，不入冲）
STEM_CLASHES = [frozenset(pair) for pair in ("甲庚", "乙辛", "丙壬", "丁癸")]

# 地支六合（合化五行）
BRANCH_SIX_COMBINES: Dict[frozenset, str] = {
    frozenset("子丑"): "土",
    frozenset("寅亥"): "木",
    frozenset("卯戌"): "火",
    frozenset("辰酉"): "金",
    frozenset("巳申"): "水",
    frozenset("午未"): "土",
}
SIX_COMBINE_NOTES = {frozenset("午未"): "午未合化五行说法不一（土 / 火）"}

# 地支三合局：(生, 旺, 墓) → 五行。旺支在中间，半合必须含旺支，缺旺支为拱合
BRANCH_THREE_COMBINES: Dict[str, str] = {
    "申子辰": "水",
    "亥卯未": "木",
    "寅午戌": "火",
    "巳酉丑": "金",
}

# 地支三会方
BRANCH_THREE_MEETINGS: Dict[str, str] = {
    "寅卯辰": "木",
    "巳午未": "火",
    "申酉戌": "金",
    "亥子丑": "水",
}

BRANCH_CLASHES = [frozenset(pair) for pair in ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")]
BRANCH_HARMS = [frozenset(pair) for pair in ("子未", "丑午", "寅巳", "卯辰", "申亥", "酉戌")]
BRANCH_DESTRUCTIONS = [frozenset(pair) for pair in ("子酉", "卯午", "巳申", "寅亥", "丑辰", "戌未")]

# 三刑：寅巳申无恩之刑、丑戌未恃势之刑（三支全为三刑，两支为相刑）
BRANCH_PUNISHMENTS = {"寅巳申": "无恩之刑", "丑戌未": "恃势之刑"}
RUDE_PUNISHMENT = frozenset("子卯")  # 无礼之刑
SELF_PUNISHMENT_BRANCHES = "辰午酉亥"

NAME_ZH = {
    "stem_five_combine": "天干五合",
    "stem_clash": "天干相冲",
    "branch_six_combine": "地支六合",
    "branch_three_combine": "地支三合",
    "branch_half_combine": "地支半合",
    "branch_arch_combine": "地支拱合",
    "branch_three_meeting": "地支三会",
    "branch_clash": "地支六冲",
    "branch_punishment": "地支三刑",
    "branch_rude_punishment": "无礼之刑",
    "branch_self_punishment": "地支自刑",
    "branch_harm": "地支六害",
    "branch_destruction": "地支六破",
}


def _relation(
    rel_type: str,
    members: Sequence[Member],
    element: Optional[str] = None,
    note: Optional[str] = None,
    **extra: Any,
) -> Dict[str, Any]:
    relation: Dict[str, Any] = {
        "type": rel_type,
        "name_zh": NAME_ZH[rel_type],
        "members": [{"pillar": pillar, "char": char} for pillar, char in members],
    }
    if element:
        relation["element"] = element
    relation.update(extra)
    if note:
        relation["note"] = note
    return relation


def _chars(members: Iterable[Member]) -> str:
    return "".join(char for _, char in members)


def _stem_relations(stems: Sequence[Member]) -> List[Dict[str, Any]]:
    relations = []
    for pair in combinations(stems, 2):
        key = frozenset(_chars(pair))
        if key in STEM_COMBINES:
            relations.append(_relation("stem_five_combine", pair, STEM_COMBINES[key], COMBINE_NOTE))
        elif key in STEM_CLASHES:
            relations.append(_relation("stem_clash", pair))
    return relations


def _trio_relations(branches: Sequence[Member]) -> List[Dict[str, Any]]:
    """三合（全局 / 半合 / 拱合）与三会；三刑的三支全刑也在这里"""
    relations = []
    covered_pairs: Set[frozenset] = set()  # 已成全局的三合，其中的两两组合不再重复列为半合 / 拱合

    for trio in combinations(branches, 3):
        trio_chars = set(_chars(trio))
        for group, element in BRANCH_THREE_COMBINES.items():
            if trio_chars == set(group):
                ordered = sorted(trio, key=lambda m: group.index(m[1]))
                relations.append(_relation("branch_three_combine", ordered, element, COMBINE_NOTE))
                covered_pairs.update(frozenset(pair) for pair in combinations(trio, 2))
        for group, element in BRANCH_THREE_MEETINGS.items():
            if trio_chars == set(group):
                ordered = sorted(trio, key=lambda m: group.index(m[1]))
                relations.append(_relation("branch_three_meeting", ordered, element))
        for group, name in BRANCH_PUNISHMENTS.items():
            if trio_chars == set(group):
                ordered = sorted(trio, key=lambda m: group.index(m[1]))
                relations.append(_relation("branch_punishment", ordered, None, name))
                covered_pairs.update(frozenset(pair) for pair in combinations(trio, 2))

    for pair in combinations(branches, 2):
        chars = _chars(pair)
        if len(set(chars)) < 2:
            continue
        for group, element in BRANCH_THREE_COMBINES.items():
            if not set(chars) <= set(group):
                continue
            if frozenset(pair) in covered_pairs:
                continue
            ordered = sorted(pair, key=lambda m: group.index(m[1]))
            missing = next(c for c in group if c not in chars)
            rel_type = "branch_half_combine" if group[1] in chars else "branch_arch_combine"
            relations.append(
                _relation(
                    rel_type,
                    ordered,
                    element,
                    f"{group}三合局缺{missing}；{COMBINE_NOTE}",
                    missing=missing,
                )
            )
        for group, name in BRANCH_PUNISHMENTS.items():
            if set(chars) <= set(group) and frozenset(pair) not in covered_pairs:
                ordered = sorted(pair, key=lambda m: group.index(m[1]))
                missing = next(c for c in group if c not in chars)
                relations.append(
                    _relation(
                        "branch_punishment",
                        ordered,
                        None,
                        f"{name}（{group}缺{missing}，两支相刑）",
                        missing=missing,
                    )
                )
    return relations


def _pair_relations(branches: Sequence[Member]) -> List[Dict[str, Any]]:
    relations = []
    for pair in combinations(branches, 2):
        chars = _chars(pair)
        key = frozenset(chars)
        if len(key) == 1:
            if chars[0] in SELF_PUNISHMENT_BRANCHES:
                relations.append(_relation("branch_self_punishment", pair))
            continue
        if key in BRANCH_SIX_COMBINES:
            note = SIX_COMBINE_NOTES.get(key, "")
            note = f"{note}；{COMBINE_NOTE}" if note else COMBINE_NOTE
            relations.append(_relation("branch_six_combine", pair, BRANCH_SIX_COMBINES[key], note))
        if key in BRANCH_CLASHES:
            relations.append(_relation("branch_clash", pair))
        if key == RUDE_PUNISHMENT:
            relations.append(_relation("branch_rude_punishment", pair))
        if key in BRANCH_HARMS:
            relations.append(_relation("branch_harm", pair))
        if key in BRANCH_DESTRUCTIONS:
            relations.append(_relation("branch_destruction", pair))
    return relations


def find_relations(pillars: Sequence[Tuple[str, str, str]]) -> List[Dict[str, Any]]:
    """列出若干柱之间成立的全部干支关系

    Args:
        pillars: [(柱名, 天干, 地支), ...]，如 [("year", "乙", "酉"), ...]
    """
    stems = [(name, gan) for name, gan, _ in pillars]
    branches = [(name, zhi) for name, _, zhi in pillars]
    return _stem_relations(stems) + _trio_relations(branches) + _pair_relations(branches)


def find_relations_with_natal(
    natal: Sequence[Tuple[str, str, str]], extra: Sequence[Tuple[str, str, str]]
) -> List[Dict[str, Any]]:
    """运势干支（大运、流年）加入后新成立的关系：至少含一个运势成员

    本命四柱内部的关系已在 get_bazi_chart 的 relations 里，这里不重复；
    大运与流年之间的关系（如岁运相冲）也列出。
    """
    extra_names = {name for name, _, _ in extra}
    return [
        relation
        for relation in find_relations([*natal, *extra])
        if any(member["pillar"] in extra_names for member in relation["members"])
    ]
