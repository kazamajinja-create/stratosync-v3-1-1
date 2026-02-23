import json

with open('sample_medical_data.json','r',encoding='utf-8') as f:
    data = json.load(f)

print("QCS Basic Medical Edition v1 - Sample Data Loaded")
print("Clinic:", data['clinic_profile']['clinic_name'])
