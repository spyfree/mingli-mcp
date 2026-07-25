"""
八字系统实现

基于lunar_python库实现八字（四柱命理）排盘和分析
参考: https://github.com/china-testing/bazi
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from mingli_mcp.core.base_system import BaseFortuneSystem
from mingli_mcp.core.exceptions import DependencyError, SystemError, ValidationError

from .formatter import BaziFormatter

logger = logging.getLogger(__name__)

try:
    from lunar_python import Lunar, Solar

    LUNAR_AVAILABLE = True
except ImportError:
    logger.warning("lunar_python not installed, BaziSystem will not work")
    LUNAR_AVAILABLE = False
    if not TYPE_CHECKING:
        Lunar = None  # type: ignore
        Solar = None  # type: ignore


# 时辰序号 → 用于排盘的小时（取时辰中点，晚子时取 23）。
# 与官网 spyfree/mingli 的 getHourFromTimeIndex 逐项一致，
# 契约见 docs/cross-engine-vectors.json 的 conventions.hourFromTimeIndex。
HOUR_BY_TIME_INDEX = {
    0: 0,  # 早子时 00:00-00:59
    1: 2,  # 丑时   01:00-02:59
    2: 4,  # 寅时
    3: 6,  # 卯时
    4: 8,  # 辰时
    5: 10,  # 巳时
    6: 12,  # 午时
    7: 14,  # 未时
    8: 16,  # 申时
    9: 18,  # 酉时
    10: 20,  # 戌时
    11: 22,  # 亥时
    12: 23,  # 晚子时 23:00-23:59
}

# 晚子时的换日流派。lunar_python 的 EightChar 默认 sect=2（夜子时：日柱留在当日、
# 时柱取次日子时）；sect=1 是子初换日——23:00 起日柱即进位次日。
#
# 本服务取 sect=1，与官网保持一致：官网的紫微引擎 (iztro) 自身输出的日干支就是
# 子初换日，两个产品卖给的是同一批人，同一个生日必须排出同一个日主。
# 这是流派选择不是对错——改它等于改掉所有 23:00-23:59 出生用户的日主，
# 连带十神、格局、大运全变，所以要改先改 docs/cross-engine-vectors.json。
DAY_BOUNDARY_SECT = 1


class BaziSystem(BaseFortuneSystem):
    """八字系统实现"""

    # 十天干
    GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    # 十二地支
    ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 十二生肖（与 ZHI 同序：子鼠、丑牛……亥猪）
    SHENG_XIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

    # 五行属性
    WU_XING = {
        "金": "庚辛申酉",
        "木": "甲乙寅卯",
        "水": "壬癸子亥",
        "火": "丙丁巳午",
        "土": "戊己丑辰未戌",
    }

    # 十神对应关系（以日干为主）
    TEN_DEITIES = {
        "甲": {
            "甲": "比肩",
            "乙": "劫财",
            "丙": "食神",
            "丁": "伤官",
            "戊": "偏财",
            "己": "正财",
            "庚": "七杀",
            "辛": "正官",
            "壬": "偏印",
            "癸": "正印",
        },
        "乙": {
            "甲": "劫财",
            "乙": "比肩",
            "丙": "伤官",
            "丁": "食神",
            "戊": "正财",
            "己": "偏财",
            "庚": "正官",
            "辛": "七杀",
            "壬": "正印",
            "癸": "偏印",
        },
        "丙": {
            "丙": "比肩",
            "丁": "劫财",
            "戊": "食神",
            "己": "伤官",
            "庚": "偏财",
            "辛": "正财",
            "壬": "七杀",
            "癸": "正官",
            "甲": "偏印",
            "乙": "正印",
        },
        "丁": {
            "丙": "劫财",
            "丁": "比肩",
            "戊": "伤官",
            "己": "食神",
            "庚": "正财",
            "辛": "偏财",
            "壬": "正官",
            "癸": "七杀",
            "甲": "正印",
            "乙": "偏印",
        },
        "戊": {
            "戊": "比肩",
            "己": "劫财",
            "庚": "食神",
            "辛": "伤官",
            "壬": "偏财",
            "癸": "正财",
            "甲": "七杀",
            "乙": "正官",
            "丙": "偏印",
            "丁": "正印",
        },
        "己": {
            "戊": "劫财",
            "己": "比肩",
            "庚": "伤官",
            "辛": "食神",
            "壬": "正财",
            "癸": "偏财",
            "甲": "正官",
            "乙": "七杀",
            "丙": "正印",
            "丁": "偏印",
        },
        "庚": {
            "庚": "比肩",
            "辛": "劫财",
            "壬": "食神",
            "癸": "伤官",
            "甲": "偏财",
            "乙": "正财",
            "丙": "七杀",
            "丁": "正官",
            "戊": "偏印",
            "己": "正印",
        },
        "辛": {
            "庚": "劫财",
            "辛": "比肩",
            "壬": "伤官",
            "癸": "食神",
            "甲": "正财",
            "乙": "偏财",
            "丙": "正官",
            "丁": "七杀",
            "戊": "正印",
            "己": "偏印",
        },
        "壬": {
            "壬": "比肩",
            "癸": "劫财",
            "甲": "食神",
            "乙": "伤官",
            "丙": "偏财",
            "丁": "正财",
            "戊": "七杀",
            "己": "正官",
            "庚": "偏印",
            "辛": "正印",
        },
        "癸": {
            "壬": "劫财",
            "癸": "比肩",
            "甲": "伤官",
            "乙": "食神",
            "丙": "正财",
            "丁": "偏财",
            "戊": "正官",
            "己": "七杀",
            "庚": "正印",
            "辛": "偏印",
        },
    }

    # 地支藏干
    ZHI_CANG_GAN = {
        "子": ["癸"],
        "丑": ["己", "癸", "辛"],
        "寅": ["甲", "丙", "戊"],
        "卯": ["乙"],
        "辰": ["戊", "乙", "癸"],
        "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"],
        "未": ["己", "丁", "乙"],
        "申": ["庚", "壬", "戊"],
        "酉": ["辛"],
        "戌": ["戊", "辛", "丁"],
        "亥": ["壬", "甲"],
    }

    def __init__(self):
        if not LUNAR_AVAILABLE:
            raise DependencyError(
                "lunar_python library is not installed. Please install it with: pip install lunar_python"
            )
        self.formatter = BaziFormatter()

    def get_system_name(self) -> str:
        return "八字"

    def get_system_version(self) -> str:
        return "1.0.0"

    def get_chart(self, birth_info: Dict[str, Any], language: str = "zh-CN") -> Dict[str, Any]:
        """
        获取八字排盘

        Args:
            birth_info: 生辰信息，包含:
                - date: 日期 (YYYY-MM-DD)
                - time_index: 时辰序号 (0-12)，或者使用 hour 指定具体小时
                - gender: 性别 (男/女)
                - calendar: 历法 (solar/lunar)，默认solar
                - is_leap_month: 是否闰月（仅农历），默认False
            language: 输出语言（暂未实现，保留接口一致性）

        Returns:
            八字排盘详细信息
        """
        self.validate_birth_info(birth_info)
        # Note: lunar_python doesn't support i18n yet, language parameter is ignored for now

        try:
            # 获取lunar对象
            lunar = self._get_lunar_object(birth_info)

            # 提取四柱：必须走EightChar，不能用Lunar.get*InGanZhi()
            #
            # Lunar.getYearInGanZhi() 以农历新年换年柱，但八字以【立春】换年柱；
            # Lunar.getMonthInGanZhi() 的月柱边界也不是精确的【节】时刻。
            # 因此在立春前后（每年约2%的出生日）以及24个节气交接当天
            # （约1.75%），这两个方法给出的干支与八字口径不一致。
            # EightChar 是lunar_python为八字提供的接口，按立春/节精确换柱。
            eight_char = self._get_eight_char(lunar)
            year_pillar = eight_char.getYear()
            month_pillar = eight_char.getMonth()
            day_pillar = eight_char.getDay()
            hour_pillar = eight_char.getTime()

            # 分解天干地支
            year_gan, year_zhi = year_pillar[0], year_pillar[1]
            month_gan, month_zhi = month_pillar[0], month_pillar[1]
            day_gan, day_zhi = day_pillar[0], day_pillar[1]
            hour_gan, hour_zhi = hour_pillar[0], hour_pillar[1]

            # 计算十神
            deities = self._calculate_ten_deities(
                day_gan,
                [year_gan, month_gan, day_gan, hour_gan, year_zhi, month_zhi, day_zhi, hour_zhi],
            )

            # 计算五行
            wu_xing = self._calculate_wu_xing(
                [year_gan, month_gan, day_gan, hour_gan, year_zhi, month_zhi, day_zhi, hour_zhi]
            )

            zhi_cang_gan = self._get_zhi_cang_gan(year_zhi, month_zhi, day_zhi, hour_zhi)

            # 构建结果
            # solar_date必须是真正的阳历日期：农历输入时birth_info["date"]是农历，
            # 需要从lunar对象反查阳历，否则会把农历日期标成阳历。
            solar_obj = lunar.getSolar()
            result = {
                "solar_date": (
                    f"{solar_obj.getYear():04d}-{solar_obj.getMonth():02d}-{solar_obj.getDay():02d}"
                ),
                "lunar_date": lunar.toString(),
                "gender": birth_info["gender"],
                "pillars": {
                    "year": {"gan": year_gan, "zhi": year_zhi, "pillar": year_pillar},
                    "month": {"gan": month_gan, "zhi": month_zhi, "pillar": month_pillar},
                    "day": {"gan": day_gan, "zhi": day_zhi, "pillar": day_pillar},
                    "hour": {"gan": hour_gan, "zhi": hour_zhi, "pillar": hour_pillar},
                },
                "eight_char": f"{year_pillar} {month_pillar} {day_pillar} {hour_pillar}",
                # 生肖直接取年柱地支对应的生肖：年柱按立春精确时刻换柱，
                # getYearShengXiaoByLiChun() 只按天换，立春当天两者会自相矛盾
                "zodiac": self._zodiac_from_zhi(year_zhi),
                "deities": deities,
                "wu_xing": wu_xing,
                "zhi_cang_gan": zhi_cang_gan,
                "zhi_deities": self._calculate_zhi_deities(day_gan, zhi_cang_gan),
                "day_master": day_gan,  # 日主（日干）
            }

            return result

        except ValidationError:
            raise
        except (ImportError, AttributeError) as e:
            logger.error(f"Missing dependency for chart generation: {e}")
            raise DependencyError(f"依赖缺失: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error generating bazi chart")
            raise SystemError(f"八字排盘失败: {str(e)}")

    def get_fortune(
        self,
        birth_info: Dict[str, Any],
        query_date: Optional[datetime] = None,
        language: str = "zh-CN",
    ) -> Dict[str, Any]:
        """
        获取八字运势（大运、流年）

        Args:
            birth_info: 生辰信息
            query_date: 查询日期，默认当前时间
            language: 输出语言（暂未实现，保留接口一致性）

        Returns:
            运势信息

        Note:
            大运按传统规则推演：阳年男/阴年女顺排，阴年男/阳年女逆排；
            起运时间由出生到月令节气的距离换算（三天折一年）。
            这部分由lunar_python计算，不再是按年龄除以10的近似。
        """
        self.validate_birth_info(birth_info)
        # Note: lunar_python doesn't support i18n yet, language parameter is ignored for now

        if query_date is None:
            query_date = datetime.now()

        try:
            # 获取基本八字
            chart = self.get_chart(birth_info, language)

            # 年份差（保留原字段口径）与虚岁（大运/流年年龄使用虚岁）
            birth_year = int(chart["solar_date"].split("-")[0])
            current_year = query_date.year
            age = current_year - birth_year

            # 查询日期早于出生日期时，大运序号/年龄都是无意义结果，直接拒绝。
            # 按天比较：同年出生日之前的查询同样无效
            birth_solar_date = datetime.strptime(chart["solar_date"], "%Y-%m-%d").date()
            if query_date.date() < birth_solar_date:
                raise ValidationError(
                    f"查询日期不能早于出生日期: {query_date.strftime('%Y-%m-%d')} "
                    f"早于 {chart['solar_date']}"
                )

            nominal_age = age + 1  # 虚岁

            lunar = self._get_lunar_object(birth_info)
            eight_char = self._get_eight_char(lunar)
            day_gan = eight_char.getDayGan()

            # 大运推演（阳男阴女顺排 / 阴男阳女逆排，起运由节气距离决定）
            yun = eight_char.getYun(1 if birth_info["gender"] == "男" else 0)
            da_yun_list = self._build_da_yun_list(yun, day_gan)
            current_da_yun = self._find_current_da_yun(da_yun_list, current_year)

            # 获取流年天干地支（同样以立春换年，与年柱口径保持一致）
            query_solar = Solar.fromDate(query_date)
            query_lunar = query_solar.getLunar()
            liu_nian_gan_zhi = query_lunar.getYearInGanZhiByLiChun()

            result = {
                "query_date": query_date.strftime("%Y-%m-%d"),
                "age": age,
                "nominal_age": nominal_age,
                "day_master": day_gan,
                "qi_yun": self._format_qi_yun(yun),
                "da_yun_direction": "顺排" if yun.isForward() else "逆排",
                "da_yun": current_da_yun,
                "da_yun_list": da_yun_list,
                "liu_nian": {
                    "year": current_year,
                    "gan_zhi": liu_nian_gan_zhi,
                    "zodiac": self._zodiac_from_zhi(liu_nian_gan_zhi[1]),
                    "age": nominal_age,
                    "deities": self._gan_zhi_deities(liu_nian_gan_zhi, day_gan),
                },
                "basic_chart": chart,
            }

            return result

        except ValidationError:
            raise
        except (ImportError, AttributeError) as e:
            logger.error(f"Missing dependency for fortune generation: {e}")
            raise DependencyError(f"依赖缺失: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error calculating bazi fortune")
            raise SystemError(f"运势计算失败: {str(e)}")

    def analyze_element(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析五行强弱

        Args:
            birth_info: 生辰信息

        Returns:
            五行分析结果
        """
        try:
            chart = self.get_chart(birth_info)
            wu_xing = chart["wu_xing"]

            # 计算总分
            total = sum(wu_xing["scores"].values())

            # 计算百分比
            percentages = {
                element: (score / total * 100 if total > 0 else 0)
                for element, score in wu_xing["scores"].items()
            }

            # 找出最强和最弱的五行
            strongest = max(wu_xing["scores"].items(), key=lambda x: x[1])
            weakest = min(wu_xing["scores"].items(), key=lambda x: x[1])

            # 五行缺失
            missing = [elem for elem, score in wu_xing["scores"].items() if score == 0]

            result = {
                "scores": wu_xing["scores"],
                "percentages": percentages,
                "strongest": {"element": strongest[0], "score": strongest[1]},
                "weakest": {"element": weakest[0], "score": weakest[1]},
                "missing": missing,
                "balance": self._judge_balance(wu_xing["scores"]),
                "day_master": chart["day_master"],
                "day_master_element": self._get_element(chart["day_master"]),
            }

            return result

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Unexpected error analyzing wu xing")
            raise SystemError(f"五行分析失败: {str(e)}")

    @staticmethod
    def _format_qi_yun(yun) -> Dict[str, Any]:
        """格式化起运信息

        起运时间是出生到月令节气的距离换算得来（三天折一年、一天折四个月），
        决定第一个大运从哪一年开始，之前的年份只走小运。
        """
        start_solar = yun.getStartSolar()
        years, months, days = yun.getStartYear(), yun.getStartMonth(), yun.getStartDay()

        parts = []
        if years:
            parts.append(f"{years}年")
        if months:
            parts.append(f"{months}个月")
        if days or not parts:
            parts.append(f"{days}天")
        offset = "".join(parts)

        return {
            "years": years,
            "months": months,
            "days": days,
            "solar_date": start_solar.toYmd(),
            "description": f"出生后{offset}起运（{start_solar.toYmd()}）",
        }

    def _gan_zhi_deities(self, gan_zhi: str, day_gan: str) -> Dict[str, Any]:
        """计算一个干支相对日主的十神（天干十神 + 地支藏干十神）"""
        if not gan_zhi or len(gan_zhi) < 2:
            return {}

        gan, zhi = gan_zhi[0], gan_zhi[1]
        deity_map = self.TEN_DEITIES.get(day_gan, {})
        hide_gan = self.ZHI_CANG_GAN.get(zhi, [])

        return {
            "gan": deity_map.get(gan, "未知"),
            "zhi_hide_gan": hide_gan,
            "zhi": [deity_map.get(hidden, "未知") for hidden in hide_gan],
        }

    def _build_da_yun_list(self, yun, day_gan: str) -> List[Dict[str, Any]]:
        """构建完整大运列表

        lunar_python 的第一项是起运前的小运期，其干支为空，这里显式标记出来，
        避免调用方把它当成一个真正的大运。
        """
        da_yun_list: List[Dict[str, Any]] = []
        for da_yun in yun.getDaYun():
            gan_zhi = da_yun.getGanZhi() or ""
            is_pre_start = not gan_zhi

            entry: Dict[str, Any] = {
                "index": da_yun.getIndex(),
                "gan_zhi": gan_zhi,
                "start_age": da_yun.getStartAge(),
                "end_age": da_yun.getEndAge(),
                "start_year": da_yun.getStartYear(),
                "end_year": da_yun.getEndYear(),
                "age_range": f"{da_yun.getStartAge()}-{da_yun.getEndAge()}岁",
                "year_range": f"{da_yun.getStartYear()}-{da_yun.getEndYear()}",
                "is_pre_start": is_pre_start,
            }

            if is_pre_start:
                entry["description"] = f"起运前小运期（{entry['age_range']}）"
            else:
                entry["description"] = f"第{da_yun.getIndex()}步大运 {gan_zhi}"
                entry["deities"] = self._gan_zhi_deities(gan_zhi, day_gan)
                entry["xun_kong"] = da_yun.getXunKong()

            da_yun_list.append(entry)

        return da_yun_list

    @staticmethod
    def _find_current_da_yun(da_yun_list: List[Dict[str, Any]], year: int) -> Dict[str, Any]:
        """按年份定位当前所处的大运；超出推演范围时返回最后一步"""
        for entry in da_yun_list:
            if entry["start_year"] <= year <= entry["end_year"]:
                return entry
        return da_yun_list[-1] if da_yun_list else {}

    @staticmethod
    def _get_eight_char(lunar: Lunar):
        """取八字接口，并钉住晚子时的换日流派（见 DAY_BOUNDARY_SECT）"""
        eight_char = lunar.getEightChar()
        eight_char.setSect(DAY_BOUNDARY_SECT)
        return eight_char

    def _get_lunar_object(self, birth_info: Dict[str, Any]) -> Lunar:
        """获取lunar对象"""
        date_str = birth_info["date"]
        year, month, day = map(int, date_str.split("-"))

        # 计算小时
        if "hour" in birth_info:
            hour = birth_info["hour"]
        elif "time_index" in birth_info:
            # 应用真太阳时修正（如果启用）
            time_index = self.apply_solar_time_correction(birth_info)

            # 时辰只给到两小时精度，代表小时取【时辰中点】：
            # 0=早子时(0点)、1=丑时(2点)、2=寅时(4点) … 11=亥时(22点)、12=晚子时(23点)。
            #
            # 取中点而不是起点，是为了与官网 (spyfree/mingli) 的
            # src/lib/bazi.ts getHourFromTimeIndex 完全一致——见
            # docs/cross-engine-vectors.json 的 conventions.hourFromTimeIndex。
            # 这个差别只在交节当天现形：若某个节交在 11:30，午时(11-13)取起点 11:00
            # 归上一个月建、取中点 12:00 归下一个月建，两端会排出不同的月柱。
            hour = HOUR_BY_TIME_INDEX.get(time_index, 12)
        else:
            hour = 0  # 默认子时

        if birth_info.get("calendar", "solar") == "lunar":
            # 农历：lunar_python 用负月份表示闰月（如闰四月 = -4）
            if birth_info.get("is_leap_month", False):
                month = -abs(month)

            lunar = Lunar.fromYmd(year, month, day)
            # lunar_python 需要用Solar来设置时间
            solar = Solar.fromYmdHms(
                lunar.getSolar().getYear(),
                lunar.getSolar().getMonth(),
                lunar.getSolar().getDay(),
                hour,
                0,
                0,
            )
            return solar.getLunar()
        else:
            # 阳历
            solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
            return solar.getLunar()

    def _calculate_ten_deities(self, day_gan: str, chars: list) -> Dict:
        """计算十神"""
        if day_gan not in self.TEN_DEITIES:
            return {}

        deity_map = self.TEN_DEITIES[day_gan]

        return {
            "year_gan": deity_map.get(chars[0], "未知"),
            "month_gan": deity_map.get(chars[1], "未知"),
            "day_gan": deity_map.get(chars[2], "未知"),
            "hour_gan": deity_map.get(chars[3], "未知"),
        }

    def _calculate_zhi_deities(
        self, day_gan: str, zhi_cang_gan: Dict[str, list]
    ) -> Dict[str, list]:
        """计算地支藏干的十神

        地支不直接对应十神，要先取藏干再逐个映射，
        同一个地支可能藏有多个天干（如寅藏甲丙戊）。
        """
        deity_map = self.TEN_DEITIES.get(day_gan, {})
        if not deity_map:
            return {pillar: [] for pillar in zhi_cang_gan}

        return {
            pillar: [deity_map.get(hidden, "未知") for hidden in hidden_gans]
            for pillar, hidden_gans in zhi_cang_gan.items()
        }

    def _calculate_wu_xing(self, chars: list) -> Dict:
        """计算五行分数"""
        scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}

        for char in chars:
            for element, chars_str in self.WU_XING.items():
                if char in chars_str:
                    scores[element] += 1
                    break

        return {"scores": scores, "description": self._format_wu_xing_desc(scores)}

    def _get_element(self, gan: str) -> str:
        """获取天干的五行属性"""
        for element, chars_str in self.WU_XING.items():
            if gan in chars_str:
                return element
        return "未知"

    def _zodiac_from_zhi(self, zhi: str) -> str:
        """由地支得生肖，保证生肖与产生该地支的干支口径完全一致"""
        return self.SHENG_XIAO[self.ZHI.index(zhi)]

    def _format_wu_xing_desc(self, scores: Dict) -> str:
        """格式化五行描述"""
        parts = [f"{elem}{score}个" for elem, score in scores.items() if score > 0]
        return "、".join(parts)

    def _get_zhi_cang_gan(self, year_zhi, month_zhi, day_zhi, hour_zhi) -> Dict:
        """获取地支藏干"""
        return {
            "year": self.ZHI_CANG_GAN.get(year_zhi, []),
            "month": self.ZHI_CANG_GAN.get(month_zhi, []),
            "day": self.ZHI_CANG_GAN.get(day_zhi, []),
            "hour": self.ZHI_CANG_GAN.get(hour_zhi, []),
        }

    def _judge_balance(self, scores: Dict) -> str:
        """判断五行平衡"""
        values = list(scores.values())
        max_val = max(values)
        min_val = min(values)

        if max_val - min_val <= 1:
            return "五行平衡"
        elif max_val - min_val <= 3:
            return "五行较平衡"
        else:
            return "五行不平衡"

    def get_capabilities(self) -> Dict[str, bool]:
        """Return the capabilities implemented by the Bazi system."""
        return {
            "chart": True,
            "fortune": True,
            "element_analysis": True,
            "palace_analysis": False,
            "compatibility": False,
        }

    def analyze_palace(
        self, birth_info: Dict[str, Any], palace_name: str, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        八字系统不支持宫位分析

        八字（四柱命理）没有宫位的概念，这是紫微斗数的特性

        Args:
            language: 输出语言（保留接口一致性）
        """
        raise NotImplementedError("八字系统不支持宫位分析，请使用紫微斗数系统")
