"""
Quick script to check what's in the Lab Results sheet
"""

from tools.sheets_monitoring_tools import ReadLabResultsTool

# Initialize tool
tool = ReadLabResultsTool()

# Read all lab results
print("=" * 80)
print("CHECKING LAB RESULTS SHEET")
print("=" * 80)

result = tool._run(patient_id="REG2025533820")
print(result)

print("\n" + "=" * 80)
print("If you see 'No lab results found', you need to add results to Google Sheets")
print("Sheet ID: 1mx0AbkSIaqmDKnZ-oaskiclmH7BqPK8QJKoeRyDCo-4")
print("=" * 80)
