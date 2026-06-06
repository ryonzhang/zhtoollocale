# -*- coding: utf-8 -*-
"""Generator for probes_focus_seed.json (NOT part of the scored benchmark).
Each base probe gets 3 phrasings (a/b/c) sharing one gold, grouped by
variant_group. Golds are library-computed (lunardate / ephem) or deterministic
arithmetic. Also prints the gold-verification table for human review."""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

DATE = "schedule_event(date: yyyy-mm-dd)"
AMT  = "set_amount(amount_cny: number)"
WT   = "set_weight(weight_kg: number)"
HT   = "set_profile(height_m: number)"

# (gid, category, family, tool, gold, source, [3 utterances], flag)
BASE = [
 # ---------------- LUNAR (13) ----------------
 ("f-L01","lunar_date","lunar",DATE,{"date":"2026-06-19"},"lunardate lunar 2026-5-5 (端午)",
  ["今年端午节（农历五月初五）安排一场龙舟比赛。",
   "帮我把今年的端午，也就是农历五月初五那天，记到日历上。",
   "今年农历五月初五是端午节，订一桌团圆饭。"],None),
 ("f-L02","lunar_date","lunar",DATE,{"date":"2026-09-25"},"lunardate lunar 2026-8-15 (中秋, name only)",
  ["今年中秋节那天给家里订月饼。",
   "把今年的中秋节标记成休息日。",
   "今年中秋，安排一次家庭聚餐。"],None),
 ("f-L03","lunar_date","lunar",DATE,{"date":"2026-10-18"},"lunardate lunar 2026-9-9 (重阳, name only)",
  ["今年重阳节带爷爷去登高。",
   "今年的重阳节给老人订一束花。",
   "把今年重阳节那天记下来。"],None),
 ("f-L04","lunar_date","lunar",DATE,{"date":"2026-08-19"},"lunardate lunar 2026-7-7 (七夕, name only)",
  ["今年七夕订一束玫瑰。",
   "今年的七夕节安排一次约会。",
   "把今年七夕那天记到日历。"],None),
 ("f-L05","lunar_date","lunar",DATE,{"date":"2027-02-06"},"lunardate lunar 2027-1-1 (大年初一, folk name, no hint)",
  ["帮我订明年大年初一回老家的火车票。",
   "明年大年初一那天给亲戚拜年。",
   "把明年的大年初一标成春节第一天。"],None),
 ("f-L06","lunar_date","lunar",DATE,{"date":"2027-02-20"},"lunardate lunar 2027-1-15 (元宵, with hint)",
  ["明年元宵节（农历正月十五）订灯会门票。",
   "把明年农历正月十五，也就是元宵节那天记一下。",
   "明年的元宵，正月十五，安排猜灯谜活动。"],None),
 ("f-L07","lunar_date","lunar",DATE,{"date":"2027-01-15"},"lunardate lunar 2026-12-8 (腊八, folk name)",
  ["明年腊八那天煮腊八粥。",
   "把明年的腊八节记到日历上。",
   "明年腊八，给同事们准备腊八蒜。"],
  "AMBIGUOUS(year-boundary): 腊八 sits at the lunar/solar year edge. Gold = the 腊八 falling in calendar 2027 (2027-01-15). A reading of '明年腊八' as lunar-2027's 腊八 -> 2028-01-04 is defensible; flagged pre-run."),
 ("f-L08","lunar_date","lunar",DATE,{"date":"2027-09-15"},"lunardate lunar 2027-8-15 (中秋, next year)",
  ["明年中秋节订一间海景房。",
   "把明年的中秋标记到行程里。",
   "明年中秋，安排回家。"],None),
 ("f-L09","lunar_date","lunar",DATE,{"date":"2027-06-09"},"lunardate lunar 2027-5-5 (端午, next year)",
  ["明年端午节包粽子。",
   "把明年的端午那天请个假。",
   "明年端午，约朋友看龙舟。"],None),
 ("f-L10","lunar_date","lunar",DATE,{"date":"2026-07-14"},"lunardate lunar 2026-6-1 (pure lunar date, no festival)",
  ["今年农历六月初一那天有个法会，记一下。",
   "把今年农历的六月初一标到日历上。",
   "今年农历六月初一，安排开业。"],None),
 ("f-L11","lunar_date","lunar",DATE,{"date":"2027-04-09"},"lunardate lunar 2027-3-3 (pure lunar date, no festival)",
  ["明年农历三月初三那天上山祭祖。",
   "把明年农历三月初三记到日程里。",
   "明年农历的三月初三，安排一次踏青。"],None),
 ("f-L12","lunar_date","lunar",DATE,{"date":"2028-07-07"},"lunardate lunar 2028 leap-month run-5 day-15 (闰五月十五)",
  ["后年农历闰五月十五那天有个仪式，帮我记下。",
   "把后年的闰五月十五（农历）标到日历上。",
   "后年农历闰五月十五，安排家祭。"],
  "HARD: requires knowing 2028 has a leap 5th month. Gold from lunardate (闰5月15 -> 2028-07-07)."),
 ("f-L13","lunar_date","lunar",DATE,{"date":"2028-01-26"},"lunardate lunar 2028-1-1 (大年初一, 后年)",
  ["后年大年初一那天全家照相。",
   "把后年的大年初一标成春节。",
   "后年大年初一，安排团圆饭。"],None),
 # ---------------- CONTROLS (3) — must NOT be lunar-converted ----------------
 ("f-C1","date_control","control",DATE,{"date":"2027-04-05"},"ephem solar-term Qingming λ=15° (SOLAR term, not lunar)",
  ["明年清明节那天去扫墓。",
   "把明年的清明节记到日历上。",
   "明年清明，安排回乡祭祖。"],
  "CONTROL: 清明 is a solar term (~Apr 4-5), NOT a lunar-calendar date. Tests over-application of lunar conversion."),
 ("f-C2","date_control","control",DATE,{"date":"2026-10-01"},"fixed Gregorian National Day 10-01",
  ["今年国庆节那天去看升旗。",
   "把今年的国庆节标成假期第一天。",
   "今年国庆，安排出游。"],
  "CONTROL: fixed 10-01."),
 ("f-C3","date_control","control",DATE,{"date":"2026-12-25"},"fixed Gregorian Christmas 12-25",
  ["今年圣诞节那天交换礼物。",
   "把今年的圣诞节记到日历上。",
   "今年圣诞，订一棵圣诞树。"],
  "CONTROL: fixed 12-25."),
 # ---------------- INTERNAL-ZERO NUMERALS (5) ----------------
 ("f-N01","numeral_wan_yi","internal_zero",AMT,{"amount_cny":100500000},"1e8 + 50*1e4 = 100,500,000 (一亿零五十万)",
  ["账户余额一亿零五十万。",
   "这个项目总投资一亿零五十万元。",
   "我们公司账上现在有一亿零五十万。"],None),
 ("f-N02","numeral_wan_yi","internal_zero",AMT,{"amount_cny":100500},"10*1e4 + 500 = 100,500 (十万零五百)",
  ["这笔款项十万零五百。",
   "报价十万零五百元。",
   "余额是十万零五百。"],None),
 ("f-N03","numeral_wan_yi","internal_zero",AMT,{"amount_cny":10050},"1e4 + 50 = 10,050 (一万零五十)",
  ["这台设备一万零五十。",
   "押金一万零五十元。",
   "总共一万零五十。"],None),
 ("f-N04","numeral_wan_yi","internal_zero",AMT,{"amount_cny":10005},"1e4 + 5 = 10,005 (一万零五)",
  ["这单一万零五。",
   "收款一万零五元。",
   "合计一万零五。"],None),
 ("f-N14","numeral_wan_yi","internal_zero",AMT,{"amount_cny":100050000},"1e8 + 5*1e4 = 100,050,000 (一亿零五万, contrast to N01)",
  ["账户余额一亿零五万。",
   "这笔资金一亿零五万元。",
   "账上有一亿零五万。"],
  "CONTRAST to f-N01 (一亿零五十万). Distinguishes 零五十万 vs 零五万."),
 # ---------------- ELLIPTICAL NUMERALS (3) ----------------
 ("f-N05","numeral_wan_yi","elliptical",AMT,{"amount_cny":35000},"三万五 = 三万五千 = 35,000",
  ["这批货三万五。",
   "报价三万五，行就成交。",
   "总价三万五。"],None),
 ("f-N06","numeral_wan_yi","elliptical",AMT,{"amount_cny":2800},"两千八 = 两千八百 = 2,800",
  ["这台手机两千八。",
   "房租两千八一个月。",
   "一共两千八。"],None),
 ("f-N07","numeral_wan_yi","elliptical",AMT,{"amount_cny":120},"一百二 = 一百二十 = 120",
  ["这件衣服一百二块。",
   "门票一百二一张。",
   "结账一百二。"],
  "MILD: '一百二' standardly 120 in money context; the 块/张 framing fixes it."),
 # ---------------- CAPITAL-FORM NUMERALS (2) ----------------
 ("f-N08","numeral_wan_yi","capital",AMT,{"amount_cny":12000},"capital 壹万贰仟 = 12,000",
  ["发票金额：壹万贰仟元整。",
   "大写金额壹万贰仟元。",
   "合同价壹万贰仟元整。"],None),
 ("f-N09","numeral_wan_yi","capital",AMT,{"amount_cny":350},"capital 叁佰伍拾 = 350",
  ["收据上写叁佰伍拾元整。",
   "大写叁佰伍拾元。",
   "金额叁佰伍拾元整。"],None),
 # ---------------- MIXED DIGIT-CHARACTER (2) ----------------
 ("f-N10","numeral_wan_yi","mixed_digit",AMT,{"amount_cny":120000000},"1.2亿 = 120,000,000",
  ["这轮融资1.2亿。",
   "估值1.2亿元。",
   "总盘子1.2亿。"],None),
 ("f-N11","numeral_wan_yi","mixed_digit",AMT,{"amount_cny":35000},"3万5 = 35,000",
  ["这车3万5拿下。",
   "差不多3万5。",
   "报价3万5。"],None),
 # ---------------- LONG CHAINS (2) ----------------
 ("f-N12","numeral_wan_yi","long_chain",AMT,{"amount_cny":230500000},"2e8 + 3050*1e4 = 230,500,000 (两亿三千零五十万)",
  ["总预算两亿三千零五十万。",
   "这个项目报价两亿三千零五十万元。",
   "合同总额两亿三千零五十万。"],None),
 ("f-N13","numeral_wan_yi","long_chain",AMT,{"amount_cny":1234567800},"12e8+3456e4+7800 = 1,234,567,800",
  ["总投资十二亿三千四百五十六万七千八百。",
   "账面金额十二亿三千四百五十六万七千八百元。",
   "规模达到十二亿三千四百五十六万七千八百。"],None),
 # ---------------- UNITS / HALF (6) ----------------
 ("f-U01","unit_conversion","units_half",WT,{"weight_kg":0.125},"2.5 liang * 0.05 = 0.125 kg (二两半)",
  ["这包瓜子二两半，记一下重量。",
   "称二两半，登记成公斤。",
   "重量是二两半。"],None),
 ("f-U02","unit_conversion","units_half",WT,{"weight_kg":1.75},"3.5 jin * 0.5 = 1.75 kg (三斤半)",
  ["这块排骨三斤半，记成公斤。",
   "称三斤半，登记重量。",
   "重量三斤半。"],None),
 ("f-U03","unit_conversion","units_half",WT,{"weight_kg":0.025},"0.5 liang * 0.05 = 0.025 kg (半两)",
  ["这点茶叶半两，记成公斤。",
   "称半两，登记重量。",
   "重量半两。"],None),
 ("f-U04","unit_conversion","units_half",HT,{"height_m":1.75},"一米七五 = 1.75 m (height, numeral-in-unit)",
  ["我身高一米七五。",
   "登记身高一米七五。",
   "他个子一米七五。"],None),
 ("f-U05","unit_conversion","units_half",WT,{"weight_kg":2.0},"两公斤 = 2.0 kg (公斤 already kg; do NOT halve)",
  ["这袋米两公斤，记一下。",
   "称两公斤，登记重量。",
   "重量两公斤。"],
  "CONTRAST pair with f-U06: 公斤 is kg directly."),
 ("f-U06","unit_conversion","units_half",WT,{"weight_kg":1.0},"两斤 = 1.0 kg (1斤=0.5kg)",
  ["这袋米两斤，记一下。",
   "称两斤，登记成公斤。",
   "重量两斤。"],
  "CONTRAST pair with f-U05: 斤 = 0.5 kg."),
]

probes = []
for gid, cat, family, tool, gold, source, utts, flag in BASE:
    for i, u in enumerate(utts):
        suffix = "abc"[i]
        probes.append({
            "id": f"{gid}-{suffix}",
            "category": cat,
            "family": family,
            "variant_group": gid,
            "layer": "arguments",
            "utterance_zh": u,
            "tool": tool,
            "expected_args": gold,
            "gold_source": source,
            **({"flag": flag} if flag else {}),
        })

data = {
    "benchmark": "ZhToolLocale-focus-v0.1",
    "description": "Focused failure-family set: lunar dates + numeral nesting + units/half, each base probe in 3 paraphrase variants (same gold). Golds: lunardate / ephem / deterministic arithmetic. reference 2026-06-05 Friday.",
    "reference_date": "2026-06-05",
    "reference_weekday": "Friday",
    "layers": ["arguments"],
    "categories": sorted({p["category"] for p in probes}),
    "probes": probes,
}
with io.open(os.path.join(HERE, "probes_focus_seed.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ---- gold-verification table ----
print(f"Generated probes_focus_seed.json: {len(BASE)} base probes x 3 variants = {len(probes)} entries\n")
print("GOLD-VERIFICATION TABLE (one row per base probe; all 3 variants share the gold)")
print(f"{'group':7s} {'family':13s} {'gold':>13s}  input (variant a)  | source")
print("-" * 110)
for gid, cat, family, tool, gold, source, utts, flag in BASE:
    gval = list(gold.values())[0]
    print(f"{gid:7s} {family:13s} {str(gval):>13s}  {utts[0]}")
    print(f"{'':7s} {'':13s} {'':>13s}    source: {source}")
    if flag:
        print(f"{'':7s} {'':13s} {'':>13s}    >> FLAG: {flag}")
print("\nFLAGGED probes (review before trusting their FAILs):")
for gid, cat, family, tool, gold, source, utts, flag in BASE:
    if flag:
        print(f"  {gid}: {flag.split(':')[0]}")
