"""
Tool Parameter Inspector
Shows the actual parameters each tool expects based on real workflow usage
"""

import inspect

print("=" * 80)
print("WORKFLOW TOOL PARAMETER REFERENCE")
print("=" * 80)

tools_to_check = [
    ("tools.patient_registration_tool", "RegisterPatientTool"),
    ("tools.google_drive_tool", "CreatePatientFolderTool"),
    ("tools.medical_records_tool", "AddAllergyTool"),
    ("tools.medical_records_tool", "AddChronicConditionTool"),
    ("tools.appointment_tool", "CheckDoctorAvailabilityTool"),
    ("tools.billing_sheets_tool", "CreateBillingRecordTool"),
    ("tools.billing_sheets_tool", "GenerateInvoiceTool"),
    ("tools.sheets_monitoring_tools", "UpdatePatientStatusTool"),
    ("tools.sheets_monitoring_tools", "AddStaffUpdateTool"),
]

for module_name, tool_name in tools_to_check:
    print(f"\n{'='*80}")
    print(f"{tool_name}")
    print('='*80)
    
    try:
        # Import the module and tool
        module = __import__(module_name, fromlist=[tool_name])
        tool_class = getattr(module, tool_name)
        
        # Get the _run method signature
        sig = inspect.signature(tool_class._run)
        
        print(f"\n✅ Tool found: {module_name}.{tool_name}")
        print(f"\nParameters:")
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            # Get type annotation
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
            
            # Get default value
            if param.default != inspect.Parameter.empty:
                default = param.default
                print(f"  • {param_name}: {param_type} = {repr(default)}")
            else:
                print(f"  • {param_name}: {param_type} (REQUIRED)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

print("\n" + "=" * 80)
print("WORKFLOW USAGE EXAMPLES")
print("=" * 80)

print("""
RegisterPatientTool:
  ✅ Correct: first_name="John", last_name="Doe", ...
  ❌ Wrong: full_name="John Doe"
  
CreatePatientFolderTool:
  ✅ Check actual parameters
  
AddAllergyTool:
  ✅ Check actual parameters
  
AddChronicConditionTool:
  ✅ Check actual parameters
  
CreateBillingRecordTool:
  ✅ Check actual parameters
  
GenerateInvoiceTool:
  ✅ Check actual parameters
  
UpdatePatientStatusTool:
  ✅ Check actual parameters
  
AddStaffUpdateTool:
  ✅ Check actual parameters
""")
