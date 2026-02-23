@echo off
setlocal
cd /d %~dp0
start "kabbalah_tree_kernel" cmd /c "cd modules\kabbalah_tree_kernel && python -m kabbalah_tree_kernel.server"
start "kabbalah_policy_lab" cmd /c "cd modules\kabbalah_policy_lab && python -m kabbalah_policy_lab.server"
start "module_health" cmd /c "cd modules\module_health && python -m module_health.server"
start "axis_resonance_tree" cmd /c "cd modules\axis_resonance_tree && python -m axis_resonance_tree.server"
echo Started: kernel(8801), lab(8802), health(8803), resonance(8804)
endlocal
