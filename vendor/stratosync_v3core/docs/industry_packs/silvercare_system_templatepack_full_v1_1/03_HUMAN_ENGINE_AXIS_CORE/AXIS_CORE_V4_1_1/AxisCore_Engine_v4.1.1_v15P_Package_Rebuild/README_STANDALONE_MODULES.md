# Standalone Modules Index

このパッケージには「単体起動型」のモジュール群が同梱されています（外部依存なし）。

## 1) Kabbalah Tree Kernel (8801)
- path: `modules/kabbalah_tree_kernel/`
- run : `run_kernel.sh` / `run_kernel.bat`
- endpoint: `POST /guard`

## 2) Kabbalah Policy Lab (8802)
- path: `modules/kabbalah_policy_lab/`
- run : `run_lab.sh` / `run_lab.bat`
- endpoints: `GET /policy`, `POST /policy`, `POST /test`

## 3) Module Health (8803)
- path: `modules/module_health/`
- run : `run_health.sh` / `run_health.bat`
- endpoint: `GET /health`

## 4) axis_resonance_tree (8804)
- path: `modules/axis_resonance_tree/`
- run : `run_resonance.sh` / `run_resonance.bat`
- endpoints: `POST /resonance/intake`, `POST /resonance/next`, `POST /resonance/relay`

## 一括起動
- mac/linux: `./RUN_ALL_MODULES.sh`
- windows : `RUN_ALL_MODULES.bat`

## 5) axis_acceleration_tree (non-API)
- path: `modules/axis_acceleration_tree/`
- run : `run_after_analysis.sh` / `run_after_analysis.bat`
- usage: called after analysis to accelerate expansion
