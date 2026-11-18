"""
Analytics Router - API Endpoints for Analytics & Dashboard Tools
Exposes 5 analytics tools as REST API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Import authentication
from api.auth import get_current_user, require_admin, require_doctor, require_staff

# Import analytics tools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.analytics_tool import (
    GetSystemOverviewTool,
    GetPatientAnalyticsTool,
    GetRevenueAnalyticsTool,
    GetOperationalAnalyticsTool,
    GenerateDashboardReportTool
)

# Create router
router = APIRouter()

# Initialize tools
system_overview_tool = GetSystemOverviewTool()
patient_analytics_tool = GetPatientAnalyticsTool()
revenue_analytics_tool = GetRevenueAnalyticsTool()
operational_analytics_tool = GetOperationalAnalyticsTool()
dashboard_report_tool = GenerateDashboardReportTool()


# ==================== REQUEST/RESPONSE MODELS ====================

class SystemOverviewRequest(BaseModel):
    """Request model for system overview"""
    date: Optional[str] = Field(None, description="Date for snapshot (YYYY-MM-DD). Default: today")


class PatientAnalyticsRequest(BaseModel):
    """Request model for patient analytics"""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")


class RevenueAnalyticsRequest(BaseModel):
    """Request model for revenue analytics"""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    period: Optional[str] = Field("monthly", description="Aggregation period: daily, weekly, monthly, yearly")


class OperationalAnalyticsRequest(BaseModel):
    """Request model for operational analytics"""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")


class DashboardReportRequest(BaseModel):
    """Request model for dashboard report"""
    format: Optional[str] = Field("text", description="Output format: text or json")
    include_charts: Optional[bool] = Field(True, description="Include chart data in JSON format")


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Any
    message: str
    timestamp: str


# ==================== API ENDPOINTS ====================

@router.post("/system-overview", response_model=APIResponse)
async def get_system_overview(
    request: SystemOverviewRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Get hospital system overview with key metrics and alerts
    
    **Permissions:** Admin, Doctor, Staff
    
    **Returns:**
    - One-screen snapshot of hospital operations
    - Active patients, today's appointments, revenue
    - Critical alerts (lab results, inventory, approvals)
    - Financial metrics (revenue, collections, outstanding)
    """
    try:
        result = system_overview_tool._run(date=request.date)
        
        return {
            "success": True,
            "data": {"report": result},
            "message": "System overview retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating system overview: {str(e)}"
        )


@router.post("/patient-analytics", response_model=APIResponse)
async def get_patient_analytics(
    request: PatientAnalyticsRequest,
    current_user: Dict = Depends(require_doctor)
):
    """
    Get comprehensive patient analytics
    
    **Permissions:** Admin, Doctor
    
    **Returns:**
    - Demographics (age, gender, blood type distribution)
    - Visit patterns (new vs returning, average visits)
    - Specialty preferences
    - Financial behavior (average bill, payment methods, insurance)
    """
    try:
        result = patient_analytics_tool._run(
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return {
            "success": True,
            "data": {"report": result},
            "message": "Patient analytics retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating patient analytics: {str(e)}"
        )


@router.post("/revenue-analytics", response_model=APIResponse)
async def get_revenue_analytics(
    request: RevenueAnalyticsRequest,
    current_user: Dict = Depends(require_admin)
):
    """
    Get comprehensive revenue analytics with trends
    
    **Permissions:** Admin only
    
    **Returns:**
    - Revenue breakdown by department, service, payment method
    - Insurance coverage by provider
    - Time-series trends (daily/weekly/monthly/yearly)
    - Collection rate metrics and insights
    """
    try:
        result = revenue_analytics_tool._run(
            start_date=request.start_date,
            end_date=request.end_date,
            period=request.period
        )
        
        return {
            "success": True,
            "data": {"report": result},
            "message": "Revenue analytics retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating revenue analytics: {str(e)}"
        )


@router.post("/operational-analytics", response_model=APIResponse)
async def get_operational_analytics(
    request: OperationalAnalyticsRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Get operational performance analytics
    
    **Permissions:** Admin, Doctor, Staff
    
    **Returns:**
    - Appointment performance (completion, no-show, cancellation rates)
    - Doctor performance (appointments per doctor, specialty distribution)
    - Lab performance (turnaround time, critical results percentage)
    - Pharmacy performance (dispensing, inventory value, low stock)
    """
    try:
        result = operational_analytics_tool._run(
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return {
            "success": True,
            "data": {"report": result},
            "message": "Operational analytics retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating operational analytics: {str(e)}"
        )


@router.post("/dashboard-report", response_model=APIResponse)
async def generate_dashboard_report(
    request: DashboardReportRequest,
    current_user: Dict = Depends(require_admin)
):
    """
    Generate comprehensive dashboard report
    
    **Permissions:** Admin only
    
    **Returns:**
    - Complete hospital analytics combining all systems
    - Executive summary with top insights and recommendations
    - Text format for email/reports
    - JSON format with chart-ready data for frontend dashboard
    """
    try:
        result = dashboard_report_tool._run(
            format=request.format,
            include_charts=request.include_charts
        )
        
        # If JSON format, parse and return structured data
        if request.format == "json":
            import json
            data = json.loads(result)
            return {
                "success": True,
                "data": data,
                "message": "Dashboard report generated successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        # Text format
        return {
            "success": True,
            "data": {"report": result},
            "message": "Dashboard report generated successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard report: {str(e)}"
        )


@router.get("/summary")
async def get_analytics_summary(current_user: Dict = Depends(require_staff)):
    """
    Get quick analytics summary
    
    **Permissions:** Admin, Doctor, Staff
    
    **Returns:** Quick summary of key metrics
    """
    try:
        # Get quick overview
        overview = system_overview_tool._run()
        
        return {
            "success": True,
            "data": {
                "message": "Analytics summary retrieved",
                "overview_available": True,
                "total_tools": 5,
                "tools": [
                    "System Overview",
                    "Patient Analytics",
                    "Revenue Analytics",
                    "Operational Analytics",
                    "Dashboard Report"
                ]
            },
            "message": "Analytics summary retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting analytics summary: {str(e)}"
        )
