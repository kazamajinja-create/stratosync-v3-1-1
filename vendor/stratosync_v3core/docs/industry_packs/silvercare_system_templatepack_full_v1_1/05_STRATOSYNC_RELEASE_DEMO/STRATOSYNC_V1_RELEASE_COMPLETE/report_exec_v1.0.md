# STRATOSYNC Executive Summary (DEMO)

- Case ID: `DEMO-JP-FOODSVC-001`
- Company: **HanaBite Foods Co., Ltd.**
- Industry: Food service / multi-store (SME)
- Revenue: 520,000,000 JPY / year

## Key Findings

- **Key-person dependency is high** (Founder dependency index 78). Scale will amplify variance unless decision patterns and role fit are stabilized.

- **Operational standardization is the bottleneck**: StoreOps pressure baseline 0.72; mismatch drives friction hotspots.

- **Pareto scenarios**: S-A, S-B, S-C (non-dominated in finance/risk/orgload/align).


## Scenario Comparison (0–100)

| Scenario | Finance | Risk | OrgLoad | Align | Composite |
|---|---|---|---|---|---|
| S-A Scale Fast (10 stores in 12m) | 100.0 | 0.0 | 0.0 | 62 | 44.3 |
| S-B Stabilize then Scale (8 stores) | 50.0 | 57.14 | 50.5 | 78 | 56.11 |
| S-C Optimize Margin (6 stores) | 0.0 | 100.0 | 100.0 | 70 | 60.5 |


## Top Org Friction Hotspots (baseline)

| person_id | role_candidate | org_unit | friction_prob |
|---|---|---|---|
| P003 | FinanceControlLead | StoreOps | 0.823 |
| P003 | FinanceControlLead | Sales | 0.759 |
| P002 | GrowthInitiativeLead | StoreOps | 0.757 |
| P003 | FinanceControlLead | HQ | 0.728 |
| P001 | FinanceControlLead | StoreOps | 0.724 |
| P003 | StoreOpsManager | StoreOps | 0.697 |
| P003 | PeopleStabilityLead | StoreOps | 0.697 |
| P003 | FinanceControlLead | People | 0.695 |


## Recommendation (DEMO)

- If **standardization capacity** is limited, start with **S-B** (stabilize then scale) to reduce org load while maintaining growth.

- Reduce key-person dependency: assign a **StoreOpsManager** role with highest fit and formalize decision cadence.


## Mode 6: Strategic Alignment (DEMO)
### CEO × Scenario Fit (0–100)
- S-A: Fit **91.71**, Stretch 8.29
- S-B: Fit **84.71**, Stretch 15.29
- S-C: Fit **75.43**, Stretch 24.57

### Organizational Resilience Index
- ORI: **66.62** (mean_friction=0.5061, dependency=0.186, avgDSS=74.8)

## Mode 7: Executive Synthesis (DEMO)
- Executive Health Score: **64.74**
- Best Scenario (by composite): **S-C** (score=60.5)

### 90-Day Priority Actions
- **P1 標準化（StoreOps）**: 店舗運用の標準手順を2週間で固定し、チェックリスト運用を開始（全店舗）。  
  理由: StoreOpsの圧力が高く、摩擦が増幅しやすい。
- **P1 属人依存の低減**: 高依存ロール「FinanceControlLead」の代替要員を1名指名し、週次で引継ぎ・意思決定ログを蓄積。  
  理由: 単一障害点（SPOF）を減らす。
- **P2 戦略選択の条件化**: 基本戦略は S-C を採用。ただし成長率・採用速度の条件レンジを定義し、逸脱時はシナリオ切替。  
  理由: Mode4の分岐思想を実務に落とす。
- **P2 摩擦ホットスポット対処**: StoreOpsでの摩擦確率が高い候補配置（P003→FinanceControlLead）は、配置前に役割境界と裁量を明文化。  
  理由: 摩擦の“条件”を先に潰す。
- **P3 意思決定リズムの統一**: 経営会議の意思決定テンプレ（前提/選択肢/リスク/反証）を導入し、バイアス検知を定例化。  
  理由: 判断の再現性と学習速度を上げる。
