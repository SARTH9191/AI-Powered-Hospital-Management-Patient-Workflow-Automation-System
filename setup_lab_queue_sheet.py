"""
Setup Lab Queue Sheet with proper headers
"""
import os
from dotenv import load_dotenv
from tools.google_sheets_tool import SheetsToolBase

# Load environment variables
load_dotenv()

def setup_lab_queue_sheet():
    """Create Lab Queue sheet with headers if not exists"""
    
    spreadsheet_id = os.getenv('LAB_RESULTS_MONITORING_SHEET_ID')
    
    if not spreadsheet_id:
        print("❌ LAB_RESULTS_MONITORING_SHEET_ID not found in .env")
        return
    
    print(f"\n🔧 Setting up Lab Queue Sheet...")
    print(f"📊 Spreadsheet ID: {spreadsheet_id}")
    print("=" * 60)
    
    # Initialize sheets service
    sheets_tool = SheetsToolBase()
    
    try:
        # Check if "Lab Queue" sheet exists
        sheet_metadata = sheets_tool.sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheets = sheet_metadata.get('sheets', [])
        lab_queue_exists = False
        
        for sheet in sheets:
            title = sheet.get('properties', {}).get('title', '')
            if title == 'Lab Queue':
                lab_queue_exists = True
                print(f"✅ 'Lab Queue' sheet already exists")
                break
        
        # Create Lab Queue sheet if it doesn't exist
        if not lab_queue_exists:
            print(f"📝 Creating 'Lab Queue' sheet...")
            
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': 'Lab Queue',
                            'gridProperties': {
                                'frozenRowCount': 1,
                                'columnCount': 11
                            }
                        }
                    }
                }]
            }
            
            sheets_tool.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            print(f"✅ 'Lab Queue' sheet created")
        
        # Add/update headers
        headers = [[
            'Patient ID',
            'Patient Name',
            'Email',
            'Phone',
            'Test Names',
            'Appointment Date',
            'Status',
            'Lab Results',
            'Doc Link',
            'Created At',
            'Updated At'
        ]]
        
        sheets_tool.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Lab Queue!A1:K1',
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        # Format headers
        # Get sheet ID
        sheet_metadata = sheets_tool.sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheet_id = 0
        for sheet in sheet_metadata.get('sheets', []):
            if sheet.get('properties', {}).get('title') == 'Lab Queue':
                sheet_id = sheet.get('properties', {}).get('sheetId')
                break
        
        # Apply formatting
        requests = [
            # Header row formatting (blue background, white bold text)
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.26, 'green': 0.52, 'blue': 0.96},
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                                'fontSize': 11
                            },
                            'horizontalAlignment': 'CENTER',
                            'verticalAlignment': 'MIDDLE'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
                }
            },
            # Auto-resize columns
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 11
                    }
                }
            },
            # Set column widths for better visibility
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 1
                    },
                    'properties': {
                        'pixelSize': 150
                    },
                    'fields': 'pixelSize'
                }
            },
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 1,
                        'endIndex': 2
                    },
                    'properties': {
                        'pixelSize': 180
                    },
                    'fields': 'pixelSize'
                }
            },
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 4,
                        'endIndex': 5
                    },
                    'properties': {
                        'pixelSize': 250
                    },
                    'fields': 'pixelSize'
                }
            },
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 7,
                        'endIndex': 8
                    },
                    'properties': {
                        'pixelSize': 300
                    },
                    'fields': 'pixelSize'
                }
            },
            # Freeze header row
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            },
            # Add data validation for Status column (G)
            {
                'setDataValidation': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000,
                        'startColumnIndex': 6,
                        'endColumnIndex': 7
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [
                                {'userEnteredValue': 'PENDING'},
                                {'userEnteredValue': 'IN_PROGRESS'},
                                {'userEnteredValue': 'COMPLETED'}
                            ]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
                }
            },
            # Conditional formatting for Status column
            # PENDING = Yellow
            {
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': 1000,
                            'startColumnIndex': 6,
                            'endColumnIndex': 7
                        }],
                        'booleanRule': {
                            'condition': {
                                'type': 'TEXT_EQ',
                                'values': [{'userEnteredValue': 'PENDING'}]
                            },
                            'format': {
                                'backgroundColor': {'red': 1, 'green': 0.95, 'blue': 0.8},
                                'textFormat': {'bold': True, 'foregroundColor': {'red': 0.85, 'green': 0.65, 'blue': 0}}
                            }
                        }
                    },
                    'index': 0
                }
            },
            # IN_PROGRESS = Light Blue
            {
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': 1000,
                            'startColumnIndex': 6,
                            'endColumnIndex': 7
                        }],
                        'booleanRule': {
                            'condition': {
                                'type': 'TEXT_EQ',
                                'values': [{'userEnteredValue': 'IN_PROGRESS'}]
                            },
                            'format': {
                                'backgroundColor': {'red': 0.85, 'green': 0.92, 'blue': 1},
                                'textFormat': {'bold': True, 'foregroundColor': {'red': 0, 'green': 0.4, 'blue': 0.8}}
                            }
                        }
                    },
                    'index': 1
                }
            },
            # COMPLETED = Light Green
            {
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': 1000,
                            'startColumnIndex': 6,
                            'endColumnIndex': 7
                        }],
                        'booleanRule': {
                            'condition': {
                                'type': 'TEXT_EQ',
                                'values': [{'userEnteredValue': 'COMPLETED'}]
                            },
                            'format': {
                                'backgroundColor': {'red': 0.85, 'green': 0.95, 'blue': 0.85},
                                'textFormat': {'bold': True, 'foregroundColor': {'red': 0, 'green': 0.6, 'blue': 0}}
                            }
                        }
                    },
                    'index': 2
                }
            },
            # Alternate row colors for better readability
            {
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [{
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': 1000,
                            'startColumnIndex': 0,
                            'endColumnIndex': 11
                        }],
                        'booleanRule': {
                            'condition': {
                                'type': 'CUSTOM_FORMULA',
                                'values': [{'userEnteredValue': '=ISEVEN(ROW())'}]
                            },
                            'format': {
                                'backgroundColor': {'red': 0.96, 'green': 0.96, 'blue': 0.96}
                            }
                        }
                    },
                    'index': 3
                }
            }
        ]
        
        sheets_tool.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        print(f"✅ Headers and formatting applied successfully")
        
        # Add sample/instruction row
        sample_row = [[
            'SAMPLE123',
            'Sample Patient',
            'example@email.com',
            '1234567890',
            'CBC, Lipid Profile, Blood Glucose',
            '2025-11-16 at 09:00 AM',
            'PENDING',
            'Enter results here when completed (one per line)',
            'https://docs.google.com/document/d/sample/edit',
            '2025-11-15 20:00:00',
            '2025-11-15 20:00:00'
        ]]
        
        sheets_tool.sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Lab Queue!A2:K2',
            valueInputOption='USER_ENTERED',
            body={'values': sample_row}
        ).execute()
        
        # Add note/instructions row
        instructions_row = [[
            '📋 INSTRUCTIONS:',
            'Update Status dropdown →',
            'Fill results when done →',
            'AI auto-reads when COMPLETED',
            '',
            '',
            'PENDING',
            'Format: Test Name: Value (Status)\nExample: RBC: 5.2 M/uL (Normal)',
            '',
            '',
            ''
        ]]
        
        sheets_tool.sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Lab Queue!A3:K3',
            valueInputOption='USER_ENTERED',
            body={'values': instructions_row}
        ).execute()
        
        # Make instruction row italic and gray
        instruction_format_requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 2,
                    'endRowIndex': 3,
                    'startColumnIndex': 0,
                    'endColumnIndex': 11
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'italic': True,
                            'foregroundColor': {'red': 0.5, 'green': 0.5, 'blue': 0.5},
                            'fontSize': 9
                        },
                        'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 1}
                    }
                },
                'fields': 'userEnteredFormat(textFormat,backgroundColor)'
            }
        }]
        
        sheets_tool.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': instruction_format_requests}
        ).execute()
        
        print(f"✅ Sample data and instructions added")
        
        print(f"\n📋 Lab Queue Columns:")
        for i, header in enumerate(headers[0], 1):
            print(f"   {i}. {header}")
        
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}"
        print(f"\n🔗 Lab Queue Sheet URL:")
        print(f"   {sheet_url}")
        
        print(f"\n✅ Lab Queue Sheet is ready!")
        print(f"\n💡 Lab technicians can now:")
        print(f"   1. View pending appointments in the Lab Queue sheet")
        print(f"   2. Update 'Status' column: PENDING → IN_PROGRESS → COMPLETED")
        print(f"   3. Enter lab results in 'Lab Results' column")
        print(f"   4. AI will auto-read results when status = COMPLETED")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    setup_lab_queue_sheet()
