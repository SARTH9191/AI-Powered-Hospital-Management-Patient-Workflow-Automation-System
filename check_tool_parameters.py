"""
Tool Parameter Inspector
========================
Quick tool to check exact parameters for any tool
"""

import inspect

def inspect_tool(tool_class):
    """Show exact parameters for a tool's _run method"""
    _run_method = tool_class._run
    sig = inspect.signature(_run_method)
    
    print(f"\n{'='*60}")
    print(f"Tool: {tool_class.__name__}")
    print(f"{'='*60}")
    print(f"\nMethod signature:")
    print(f"  _run{sig}")
    
    print(f"\nParameters:")
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
        
        required = param.default == inspect.Parameter.empty
        default = param.default if not required else "REQUIRED"
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
        
        status = "🔴 REQUIRED" if required else f"🟢 Optional (default={default})"
        print(f"  • {param_name}: {param_type} - {status}")
    
    print()

# Quick check any tool
if __name__ == "__main__":
    print("TOOL PARAMETER QUICK REFERENCE")
    print("="*60)
    
    # Add any tool you want to check
    from tools.patient_registration_tool import RegisterPatientTool
    from tools.google_sheets_tool import AddPatientRecordTool, AddLabResultTool
    from tools.medical_records_tool import AddAllergyTool
    from tools.billing_sheets_tool import CreateBillingRecordTool
    from tools.docs_monitoring_tools import CreateMedicalDocumentTool, ShareMedicalDocumentTool
    from tools.sheets_monitoring_tools import AddDoctorNoteTool, UpdatePatientStatusTool, AddStaffUpdateTool
    from tools.google_calendar_tool import CreateAppointmentTool
    from tools.gmail_tool import SendGmailTool
    
    tools_to_check = [
        RegisterPatientTool,
        AddPatientRecordTool,
        AddLabResultTool,
        AddAllergyTool,
        CreateBillingRecordTool,
        CreateMedicalDocumentTool,
        ShareMedicalDocumentTool,
        AddDoctorNoteTool,
        UpdatePatientStatusTool,
        AddStaffUpdateTool,
        CreateAppointmentTool,
        SendGmailTool
    ]
    
    for tool_class in tools_to_check:
        inspect_tool(tool_class)
    
    print("\n💡 TIP: Copy the exact parameter names when calling tools!")
    print("   Always use keyword arguments: tool._run(param1=value1, param2=value2)")
