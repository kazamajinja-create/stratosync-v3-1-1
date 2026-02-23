"""
ローカル簡易デモ（APIを直接叩かずにモジュール関数を呼ぶ版）
実行:
python demo_local.py
"""
from omega_qcs.models import CaseCreate, IntakeSubmit, Constraints, ReportBuildRequest, SessionStart, SessionNote, SessionFinalize
from omega_qcs.omega_case_registry import create_case, set_status
from omega_qcs.omega_intake import submit_intake
from omega_qcs.omega_quantum_analyzer import analyze
from omega_qcs.omega_report_builder import build_report
from omega_qcs.omega_session_orchestrator import start_session, add_note, finalize
from omega_qcs.omega_deliverables_pack import deliver

case = create_case(CaseCreate(client_type="corporate", theme="新規事業を続行するか撤退するか", notes="デモ"))
submit_intake(IntakeSubmit(
    case_id=case.case_id,
    background="売上が伸び悩み、チームの疲弊が見える。意思決定の期限は1ヶ月。主要顧客からの要望もある。",
    constraints=Constraints(money="追加投資は月50万円まで", people="専任は2名", time="1ヶ月で判断", role="最終決裁者"),
    options_known=["現状維持で改善を試す", "方向転換して集中する"],
    avoid_options=["撤退/縮小"],
    success_definition="信用を落とさずに次の打ち手へ移る",
    risk_tolerance="短期売上減は許容"
))
analyze(case.case_id)
build_report(ReportBuildRequest(case_id=case.case_id, format="both"))
start_session(SessionStart(case_id=case.case_id, duration_min=90))
add_note(SessionNote(case_id=case.case_id, step="READ", note="前提条件の誤読を修正"))
add_note(SessionNote(case_id=case.case_id, step="DEEPEN", note="A/Bで得るもの失うものを言語化"))
finalize(SessionFinalize(case_id=case.case_id, decisions_pending=["撤退条件の数値定義"], axis_criteria=["信用を守る", "疲弊を増やさない", "期限内に決める"]))
d = deliver(case.case_id)
print("DELIVERED:", d["zip_path"])
