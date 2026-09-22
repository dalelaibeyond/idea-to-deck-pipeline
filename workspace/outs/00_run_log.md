# Run Log — Idea to Deck Pipeline

Append-only across sessions: each `index.py clean` starts a new session, and
the Orchestrator **appends a new `## Run <session_id>` section per run** —
never modify or overwrite earlier sections (`clean` archives a copy of this
file with each run's snapshot). Within a run: **one line per Gate decision,
one line per retry / circuit-breaker event**; nothing else belongs here —
non-gate render details are not logged, raise them in conversation instead.
(Full token/latency telemetry is a v0.5 production-ready requirement, not
v0.2.)

---

## Run deck_20260919_658

| Field | Value |
|-------|-------|
| session_id | deck_20260919_658 |
| started_at | 2026-09-19T04:45:41+00:00 |
| target_format | pptx |
| circuit_breaker_triggered | no |

### Gate Decisions (one line each)

| Time | Gate | Decision | Chosen | Notes |
|------|------|----------|--------|-------|
| 13:05 | Gate 1 — facts confirmation | user-selected | 确认全部事实/假设；财务数据联网检索未果→定性描述；路线图3年三阶段；篇幅约10页 | 补查ics.com.ph/about-us新增F9演化时间线 |
| 13:12 | Gate 2 — narrative framework | user-selected | SCQA | 10页：S(2)-C(3)-QA(4)-Why us(5,6)-Where(7)-Roadmap(8)-Moat(9)-CTA(10) |
| 13:18 | Gate 3 — visual archetype | user-selected | McKinsey × Executive 120s Hybrid | #003366/#E8A33D，slide3痛感红#C0392B，slide6获得感绿#27AE60 |

### Retry & Circuit-Breaker Events

| Time | Step | Event | Detail |
|------|------|-------|--------|
| (none) | | | |

---

## Run deck_20260919_737

| Field | Value |
|-------|-------|
| session_id | deck_20260919_737 |
| started_at | 2026-09-19T08:42:53+00:00 |
| target_format | pptx |
| circuit_breaker_triggered | no |

### Gate Decisions (one line each)

| Time | Gate | Decision | Chosen | Notes |
|------|------|----------|--------|-------|
| 09:xx | Gate 1 — facts confirmation | user-selected | 确认事实/假设清单；补充目标=董事会/高管层、中文输出、批准AI-Agent专项、3年三阶段、约10页 | 新增enrichment：F6 ReN3智能体合作2026-04、F7 2026 AI进入企业工作流、F9无公开财报负向发现、F10员工-1.2%停滞；A5贬损性评价剔除正片 |
| 09:xx | Gate 2 — narrative framework | user-selected | SCQA | 10页：Cover(1)-S(2)-C(3)-Q(4)-Signal(5)-Why us(6)-Agent场景(7)-Roadmap(8)-Moat(9)-CTA(10) |
| 09:xx | Gate 3 — visual archetype | user-selected | McKinsey × Exec 120s Hybrid | 库内已有 archetype；主#003366/金#E8A33D；p3痛感红#C0392B、p9获得感绿#27AE60 |

### Retry & Circuit-Breaker Events

| Time | Step | Event | Detail |
|------|------|-------|--------|
| (none) | | | |

## Run deck_20260922_975

| Field | Value |
|-------|-------|
| session_id | deck_20260922_975 |
| started_at | 2026-09-22T01:59:15+00:00 |
| target_format | pptx |
| circuit_breaker_triggered | no |

### Gate Decisions (one line each)

| Time | Gate | Decision | Chosen | Notes |
|------|------|----------|--------|-------|
| 22 SEP | Gate 1 — facts confirmation | user-selected | 13 slides · full simple English (no jargon) · SCQA/McKinsey-120s, big key numbers · KYS+RSI explained in 1–2 pages + full 4-tier architecture · high-level 3-year plan | 用三层一页讲KYS；RSI封闭闭环；数字沿用仲裁基线 |
| 22 SEP | Gate 2 — narrative framework | user-selected | SCQA (pre-decided at Gate 1) | 13屏结构已产出并经用户确认卡片表 |
| 22 SEP | Gate 3 — visual archetype | user-selected | McKinsey × Executive 120s Hybrid (existing archetype) | 库内已有 mckinsey_exec_hybrid.yaml，直接复用；主#003366/金#E8A33D；p3痛红#C0392B、p6/8/11/12得绿#27AE60 |

### Retry & Circuit-Breaker Events

| Time | Step | Event | Detail |
|------|------|-------|--------|
| (none) | | | |
