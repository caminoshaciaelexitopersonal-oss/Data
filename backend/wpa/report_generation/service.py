from typing import Dict, Any
from backend.wpa.report_generation.schemas import ReportGenerationRequest
from backend.report_generator import generate_report # Reusing the existing generator

class ReportGenerationService:
    """
    Service for the "Report Generation" Workflow (WPA).
    Orchestrates the creation of DOCX/PDF reports.
    """
    def generate_report(self, request: ReportGenerationRequest) -> Dict[str, Any]:
        """
        Executes the report generation workflow.
        """
        # The existing generate_report function is simple, but for a more
        # complex scenario, this service would fetch data, visualizations, etc.,
        # from a session store and pass them to the generator.

        # For now, we pass a simplified set of parameters.
        file_path = generate_report(
            title=request.title,
            summary=request.summary,
            visualizations={} # Placeholder
        )

        return {
            "file_path": file_path
        }
