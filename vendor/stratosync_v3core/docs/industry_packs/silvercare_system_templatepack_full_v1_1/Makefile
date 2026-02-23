.PHONY: demo demo_pdf demo_tp demo_med demo_dental verify

INPUT=05_STRATOSYNC_RELEASE_DEMO/STRATOSYNC_V1_RELEASE_COMPLETE/integrated_case.v1.0.json
OUTDIR=out_demo
TP=TEMPLATE_PACKS/TemplatePack_JP_FoodService_v1_skeleton.json
TP_MED=TEMPLATE_PACKS/TemplatePack_JP_MedicalClinic_v1.json
TP_DENTAL=TEMPLATE_PACKS/TemplatePack_JP_DentalClinic_v1_1.json

demo:
	python run_demo.py --input $(INPUT) --out $(OUTDIR)

demo_pdf:
	python run_demo.py --input $(INPUT) --out $(OUTDIR) --regen-pdf

demo_tp:
	python run_demo.py --input $(INPUT) --template $(TP) --out $(OUTDIR)

demo_med:
	python run_demo.py --input $(INPUT) --template $(TP_MED) --out $(OUTDIR)

demo_dental:
	python run_demo.py --input $(INPUT) --template $(TP_DENTAL) --out $(OUTDIR)

verify:
	python -c "import json; p='00_MANIFEST/INTEGRATION_MANIFEST_v1.1.json'; print('manifest ok' if json.load(open(p,'r',encoding='utf-8')) else 'manifest missing')"

# Full demo (applies TemplatePack, which computes Mode1 demo from sample KPI)
demo_med_full:
	python run_demo.py --input $(INPUT) --template $(TP_MED) --out $(OUTDIR)
demo_dental_full:
	python run_demo.py --input $(INPUT) --template $(TP_DENTAL) --out $(OUTDIR)


demo_report:
	python run_demo.py --input $(INPUT) --out $(OUTDIR) --write-report
demo_med_report:
	python run_demo.py --input $(INPUT) --template $(TP_MED) --out $(OUTDIR) --write-report
demo_dental_report:
	python run_demo.py --input $(INPUT) --template $(TP_DENTAL) --out $(OUTDIR) --write-report


demo_silvercare_report:
	TEMPLATE=TEMPLATE_PACKS/TemplatePack_JP_SilverCare_v1_0.json WRITE_REPORT=1 bash run_demo.sh
