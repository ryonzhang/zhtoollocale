# ZhToolLocale v0.4 — Gemini experiment matrix

Reference date injected into every prompt: **2026-06-05 (Friday)**.  Provider: gemini (OpenAI-compatible endpoint). Temperature 0.

## 1. Results matrix

| Model id | Tier | Tier-1 (23) | Tier-2 hard (20) | Errors |
|---|---|---|---|---|
| `gemini-2.5-flash` | A (strong) | 23/23 (100.0%) | 19/20 (95.0%) | none |
| `gemini-2.0-flash` | B (mid) | 0/23 (0.0%) | 0/20 (0.0%) | 25× 404 NOT_FOUND; 22× 404 NOT_FOUND |
| `gemini-2.5-flash-lite` | C (small) | 22/23 (95.7%) | 18/20 (90.0%) | none |

## 2. Per-category breakdown — Tier-2 HARD

| Category | `2.5-flash` | `2.0-flash` | `2.5-flash-lite` |
|---|---|---|---|
| address | 1/1 | 0/1 | 1/1 |
| currency | 3/3 | 0/3 | 3/3 |
| fuzzy_quantity | 1/1 | 0/1 | 1/1 |
| lunar_date | 0/1 | 0/1 | 0/1 |
| numeral_wan_yi | 5/5 | 0/5 | 5/5 |
| person_name | 2/2 | 0/2 | 1/2 |
| relative_date | 4/4 | 0/4 | 4/4 |
| unit_conversion | 3/3 | 0/3 | 3/3 |

## 3. All failed probes (verbatim), tagged model + tier

- `gemini-2.5-flash` [tier-2] [FAIL] h-ld-01  lunar_date       pred={'date': '2027-02-18'} gold={'date': '2027-02-06'}
- `gemini-2.0-flash` [tier-1] [FAIL] rd-01    relative_date    pred={} gold={'date': '2026-06-08', 'time': '10:00'}
- `gemini-2.0-flash` [tier-1] [FAIL] rd-02    relative_date    pred={} gold={'date': '2026-06-10', 'time': '15:00'}
- `gemini-2.0-flash` [tier-1] [FAIL] rd-03    relative_date    pred={} gold={'date': '2026-06-30'}
- `gemini-2.0-flash` [tier-1] [FAIL] rd-04    relative_date    pred={} gold={'date': '2026-07-01'}
- `gemini-2.0-flash` [tier-1] [FAIL] ld-01    lunar_date       pred={} gold={'date': '2026-09-25'}
- `gemini-2.0-flash` [tier-1] [FAIL] nm-01    numeral_wan_yi   pred={} gold={'amount_cny': 12000}
- `gemini-2.0-flash` [tier-1] [FAIL] nm-02    numeral_wan_yi   pred={} gold={'amount_cny': 2500000}
- `gemini-2.0-flash` [tier-1] [FAIL] nm-03    numeral_wan_yi   pred={} gold={'amount_cny': 3500}
- `gemini-2.0-flash` [tier-1] [FAIL] cur-01   currency         pred={} gold={'price_cny': 3.5}
- `gemini-2.0-flash` [tier-1] [FAIL] cur-02   currency         pred={} gold={'amount_cny': 500000}
- `gemini-2.0-flash` [tier-1] [FAIL] un-01    unit_conversion  pred={} gold={'item': '苹果', 'weight_kg': 1.0}
- `gemini-2.0-flash` [tier-1] [FAIL] un-02    unit_conversion  pred={} gold={'height_m': 1.8}
- `gemini-2.0-flash` [tier-1] [FAIL] un-03    unit_conversion  pred={} gold={'distance_m': 3000}
- `gemini-2.0-flash` [tier-1] [FAIL] pn-01    person_name      pred={} gold={'family_name': '张', 'given_name': '伟'}
- `gemini-2.0-flash` [tier-1] [FAIL] pn-02    person_name      pred={} gold={'family_name': '欧阳', 'given_name': '娜娜'}
- `gemini-2.0-flash` [tier-1] [FAIL] ad-01    address          pred={} gold={'city': '北京市', 'district': '海淀区', 'street': '中关村大街', 'number': '1'}
- `gemini-2.0-flash` [tier-1] [FAIL] ph-01    phone            pred={} gold={'number': '13800138000'}
- `gemini-2.0-flash` [tier-1] [FAIL] cl-01    classifier       pred={} gold={'item': '美式咖啡', 'quantity': 3}
- `gemini-2.0-flash` [tier-1] [FAIL] cs-01    code_switch      pred={} gold={'date': '2026-06-06', 'time': '15:00', 'destination': '上海'}
- `gemini-2.0-flash` [tier-1] [FAIL] fw-01    fullwidth        pred={} gold={'amount_cny': 1234}
- `gemini-2.0-flash` [tier-1] [FAIL] fq-01    fuzzy_quantity   pred={} gold={'item': '鸡蛋', 'quantity': 6}
- `gemini-2.0-flash` [tier-1] [FAIL] rec-01   unit_conversion  pred={} gold={'item': '香蕉', 'weight_kg': 1.0}
- `gemini-2.0-flash` [tier-1] [FAIL] rec-02   numeral_wan_yi   pred={} gold={'amount_cny': 12000}
- `gemini-2.0-flash` [tier-2] [FAIL] h-nm-01  numeral_wan_yi   pred={} gold={'amount_cny': 123000000}
- `gemini-2.0-flash` [tier-2] [FAIL] h-nm-02  numeral_wan_yi   pred={} gold={'amount_cny': 12000}
- `gemini-2.0-flash` [tier-2] [FAIL] h-nm-03  numeral_wan_yi   pred={} gold={'amount_cny': 35600}
- `gemini-2.0-flash` [tier-2] [FAIL] h-nm-04  numeral_wan_yi   pred={} gold={'quantity': 2050}
- `gemini-2.0-flash` [tier-2] [FAIL] h-un-01  unit_conversion  pred={} gold={'item': '牛肉', 'weight_kg': 1.25}
- `gemini-2.0-flash` [tier-2] [FAIL] h-un-02  unit_conversion  pred={} gold={'item': '虾仁', 'weight_kg': 0.25}
- `gemini-2.0-flash` [tier-2] [FAIL] h-un-03  unit_conversion  pred={} gold={'item': '茶叶', 'weight_kg': 0.15}
- `gemini-2.0-flash` [tier-2] [FAIL] h-rd-01  relative_date    pred={} gold={'date': '2026-06-19'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-rd-02  relative_date    pred={} gold={'date': '2026-06-19'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-tm-01  relative_date    pred={} gold={'date': '2026-06-05', 'time': '15:15'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-tm-02  relative_date    pred={} gold={'date': '2026-06-06', 'time': '01:00'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-dc-01  currency         pred={} gold={'amount_cny': 160}
- `gemini-2.0-flash` [tier-2] [FAIL] h-dc-02  currency         pred={} gold={'amount_cny': 1300}
- `gemini-2.0-flash` [tier-2] [FAIL] h-pn-01  person_name      pred={} gold={'family_name': '司马', 'given_name': '懿'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-pn-02  person_name      pred={} gold={'family_name': '张', 'given_name': '三丰'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-ad-01  address          pred={} gold={'city': '上海市', 'district': '浦东新区', 'street': '世纪大道', 'number': '100', 'building': '3', 'room': '502'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-fz-01  fuzzy_quantity   pred={} gold={'item': '玫瑰', 'quantity': 18}
- `gemini-2.0-flash` [tier-2] [FAIL] h-ld-01  lunar_date       pred={} gold={'date': '2027-02-06'}
- `gemini-2.0-flash` [tier-2] [FAIL] h-rec-01 numeral_wan_yi   pred={} gold={'amount_cny': 12000}
- `gemini-2.0-flash` [tier-2] [FAIL] h-rec-02 currency         pred={} gold={'amount_cny': 375}
- `gemini-2.5-flash-lite` [tier-1] [FAIL] ld-01    lunar_date       pred={'date': '2026-09-26'} gold={'date': '2026-09-25'}
- `gemini-2.5-flash-lite` [tier-2] [FAIL] h-pn-02  person_name      pred={'family_name': '张三丰', 'given_name': None} gold={'family_name': '张', 'given_name': '三丰'}
- `gemini-2.5-flash-lite` [tier-2] [FAIL] h-ld-01  lunar_date       pred={'date': '2027-02-14'} gold={'date': '2027-02-06'}

## 4. Exact model ids that ran

- Model A: `gemini-2.5-flash` — ran.
- Model B: `gemini-2.0-flash` — **retired/unavailable** (404 NOT_FOUND on every call); no fallback was specified for Model B, so its cells are 0/N artifacts of unavailability, not model errors.
- Model C: requested `gemini-2.5-flash-lite` — **available, ran** (no fallback needed).
- Model D (Ollama qwen2.5): skipped — Ollama not installed.

## 5. Errors / rate-limit notes

- `gemini-2.0-flash` returned HTTP 404 `NOT_FOUND` ("no longer available") for all probes in both tiers.
- No rate-limiting was encountered on any successful run.
