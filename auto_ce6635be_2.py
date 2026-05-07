```python
#!/usr/bin/env python3
"""
Meeting Minutes Formatter

A self-contained Python script that formats extracted meeting elements into 
structured markdown or HTML meeting minutes. The script processes meeting data
and organizes it into clear sections for attendees, agenda items, decisions made,
and action items assigned during the meeting.

Features:
- Supports both Markdown and HTML output formats
- Structured sections for complete meeting documentation
- Error handling for malformed input data
- Extensible design for additional meeting elements

Usage:
    python script.py

The script includes sample meeting data and demonstrates formatting capabilities
for typical meeting documentation workflows.
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ActionItem:
    """Represents a single action item from a meeting."""
    task: str
    assignee: str
    due_date: Optional[str] = None
    priority: str = "medium"


@dataclass
class Decision:
    """Represents a decision made during the meeting."""
    topic: str
    decision: str
    rationale: Optional[str] = None


@dataclass
class MeetingData:
    """Container for all meeting information."""
    title: str
    date: str
    attendees: List[str]
    agenda_items: List[str]
    decisions: List[Decision]
    action_items: List[ActionItem]
    notes: List[str] = field(default_factory=list)


class MeetingMinutesFormatter:
    """Formats meeting data into structured markdown or HTML."""
    
    def __init__(self):
        self.supported_formats = ['markdown', 'html']
    
    def format_meeting_minutes(self, meeting_data: MeetingData, output_format: str = 'markdown') -> str:
        """
        Format meeting data into structured minutes.
        
        Args:
            meeting_data: MeetingData object containing all meeting information
            output_format: Output format ('markdown' or 'html')
            
        Returns:
            Formatted meeting minutes as string
            
        Raises:
            ValueError: If output_format is not supported
        """
        if output_format.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {output_format}. Supported formats: {self.supported_formats}")
        
        if output_format.lower() == 'markdown':
            return self._format_markdown(meeting_data)
        else:
            return self._format_html(meeting_data)
    
    def _format_markdown(self, meeting_data: MeetingData) -> str:
        """Format meeting data as Markdown."""
        lines = []
        
        # Header
        lines.append(f"# {meeting_data.title}")
        lines.append(f"**Date:** {meeting_data.date}")
        lines.append("")
        
        # Attendees
        lines.append("## Attendees")
        for attendee in meeting_data.attendees:
            lines.append(f"- {attendee}")
        lines.append("")
        
        # Agenda
        lines.append("## Agenda")
        for i, item in enumerate(meeting_data.agenda_items, 1):
            lines.append(f"{i}. {item}")
        lines.append("")
        
        # Decisions
        if meeting_data.decisions:
            lines.append("## Decisions Made")
            for decision in meeting_data.decisions:
                lines.append(f"### {decision.topic}")
                lines.append(f"**Decision:** {decision.decision}")
                if decision.rationale:
                    lines.append(f"**Rationale:** {decision.rationale}")
                lines.append("")
        
        # Action Items
        if meeting_data.action_items:
            lines.append("## Action Items")
            lines.append("| Task | Assignee | Due Date | Priority |")
            lines.append("|------|----------|----------|----------|")
            for item in meeting_data.action_items:
                due_date = item.due_date or "TBD"
                lines.append(f"| {item.task} | {item.assignee} | {due_date} | {item.priority} |")
            lines.append("")
        
        # Notes
        if meeting_data.notes:
            lines.append("## Additional Notes")
            for note in meeting_data.notes:
                lines.append(f"- {note}")
        
        return "\n".join(lines)
    
    def _format_html(self, meeting_data: MeetingData) -> str:
        """Format meeting data as HTML."""
        html_parts = []
        
        # HTML structure start
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='en'>")
        html_parts.append("<head>")
        html_parts.append("    <meta charset='UTF-8'>")
        html_parts.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_parts.append(f"    <title>{meeting_data.title}</title>")
        html_parts.append("    <style>")
        html_parts.append("        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }")
        html_parts.append("        table { border-collapse: collapse; width: 100%; }")
        html_parts.append("        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html_parts.append("        th { background-color: #f2f2f2; }")
        html_parts.append("        .priority-high { color: #d32f2f; font-weight: bold; }")
        html_parts.append("        .priority-medium { color: #f57c00; }")
        html_parts.append("        .priority-low { color: #388e3c; }")
        html_parts.append("    </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # Header
        html_parts.append(f"    <h1>{meeting_data.title}</h1>")
        html_parts.append(f"    <p><strong>Date:</strong> {meeting_data.date}</p>")
        
        # Attendees
        html_parts.append("    <h2>Attendees</h2>")
        html_parts.append("    <ul>")
        for attendee in meeting_data.attendees:
            html_parts.append(f"        <li>{attendee}</li>")
        html_parts.append("    </ul>")
        
        # Agenda
        html_parts.append("    <h2>Agenda</h2>")
        html_parts.append("    <ol>")
        for item in meeting_data.agenda_items:
            html_parts.append(f"        <li>{item}</li>")
        html_parts.append("    </ol>")
        
        # Decisions
        if meeting_data.decisions:
            html_parts.append("    <h2>Decisions Made</h2>")
            for decision in meeting_data.decisions:
                html_parts.append(f"        <h3>{decision.topic}</h3>")
                html_parts.append(f"        <p><strong>Decision:</strong> {decision.decision}</p>")
                if decision.rationale:
                    html_parts.append(f"        <p><strong>Rationale:</strong> {decision.rationale}</p>")
        
        # Action Items
        if meeting_data.action_items:
            html_parts.append("    <h2>Action Items</h2>")
            html_parts.append("    <table>")
            html_parts.append("        <thead>")
            html_parts.append("            <tr><th>Task</th><th>Assignee</th><th>Due Date</th><th>Priority</th></tr>")
            html_parts.append("        </thead>")
            html_parts.append("        <tbody>")
            for item in meeting_data.action_items:
                due_date = item.due_date or "T