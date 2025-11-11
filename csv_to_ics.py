#!/usr/bin/env python3
"""
Convert CSV file to ICS (iCalendar) format
Usage: python csv_to_ics.py <input_csv> [output_ics]
"""

import csv
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def parse_date_range(month_str, dates_str, year=2026):
    """
    Parse date strings like 'Jan. 12-16', 'Feb. 3-5', 'Aug. 10', etc.
    Returns (start_date, end_date) as datetime objects
    """
    # Month mapping
    month_map = {
        'January': 1, 'Jan.': 1, 'Jan': 1,
        'February': 2, 'Feb.': 2, 'Feb': 2,
        'March': 3, 'Mar.': 3, 'Mar': 3,
        'April': 4, 'Apr.': 4, 'Apr': 4,
        'May': 5,
        'June': 6, 'Jun.': 6, 'Jun': 6,
        'July': 7, 'Jul.': 7, 'Jul': 7,
        'August': 8, 'Aug.': 8, 'Aug': 8,
        'September': 9, 'Sept.': 9, 'Sep.': 9, 'Sep': 9,
        'October': 10, 'Oct.': 10, 'Oct': 10,
        'November': 11, 'Nov.': 11, 'Nov': 11,
        'December': 12, 'Dec.': 12, 'Dec': 12,
    }

    # Clean up the dates string - normalize different dash types
    dates_str = dates_str.replace('–', '-').replace('—', '-').strip()

    # Extract month from dates string if present, otherwise use month_str
    date_pattern = r'([A-Za-z]+\.?)\s+(\d+)\s*-\s*(\d+)'
    single_date_pattern = r'([A-Za-z]+\.?)\s+(\d+)'
    range_pattern = r'(\d+)\s*-\s*(\d+)'

    # Try to match full date range with month (e.g., "Jan. 12-16")
    match = re.search(date_pattern, dates_str)
    if match:
        month_name = match.group(1)
        start_day = int(match.group(2))
        end_day = int(match.group(3))
        month = month_map.get(month_name, month_map.get(month_str, 1))
    else:
        # Try single date with month (e.g., "Aug. 10")
        match = re.search(single_date_pattern, dates_str)
        if match:
            month_name = match.group(1)
            start_day = int(match.group(2))
            end_day = start_day
            month = month_map.get(month_name, month_map.get(month_str, 1))
        else:
            # Try simple range without month (e.g., "12-16")
            match = re.search(range_pattern, dates_str)
            if match:
                start_day = int(match.group(1))
                end_day = int(match.group(2))
                month = month_map.get(month_str, 1)
            else:
                # Try single number
                match = re.search(r'(\d+)', dates_str)
                if match:
                    start_day = int(match.group(1))
                    end_day = start_day
                    month = month_map.get(month_str, 1)
                else:
                    # Default fallback
                    start_day = 1
                    end_day = 1
                    month = month_map.get(month_str, 1)

    # Create datetime objects
    start_date = datetime(year, month, start_day)
    end_date = datetime(year, month, end_day)

    # Add one day to end_date since events typically end at the end of the last day
    end_date = end_date + timedelta(days=1)

    return start_date, end_date


def create_ics_event(event_data, event_id):
    """
    Create an ICS event string from event data
    """
    month = event_data['Month']
    event_name = event_data['Event Name']
    dates = event_data['Dates']
    location = event_data['Location']
    primary_focus = event_data['Primary Focus']
    geo_cluster = event_data['Geo Cluster']
    meta_tags = event_data['Meta Tags (Area of Interest)']

    # Parse dates
    start_date, end_date = parse_date_range(month, dates)

    # Format dates for ICS (YYYYMMDD format)
    dtstart = start_date.strftime('%Y%m%d')
    dtend = end_date.strftime('%Y%m%d')

    # Create description
    description_parts = []
    if primary_focus:
        description_parts.append(f"Focus: {primary_focus}")
    if geo_cluster:
        description_parts.append(f"Region: {geo_cluster}")
    if meta_tags:
        description_parts.append(f"Tags: {meta_tags}")

    description = "\\n".join(description_parts)

    # Create unique ID
    uid = f"event-{event_id}@csv-to-cal"

    # Create timestamp
    dtstamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')

    # Build ICS event
    ics_event = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART;VALUE=DATE:{dtstart}
DTEND;VALUE=DATE:{dtend}
SUMMARY:{event_name}
LOCATION:{location}
DESCRIPTION:{description}
STATUS:CONFIRMED
END:VEVENT"""

    return ics_event


def csv_to_ics(csv_path, ics_path):
    """
    Convert CSV file to ICS format
    """
    events = []

    # Read CSV file
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            event = create_ics_event(row, idx)
            events.append(event)

    # Create ICS file
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CSV to Calendar Converter//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Manufacturing Events 2026
X-WR-TIMEZONE:UTC
"""

    # Add all events
    for event in events:
        ics_content += event + "\n"

    # Close calendar
    ics_content += "END:VCALENDAR\n"

    # Write to file
    with open(ics_path, 'w', encoding='utf-8') as icsfile:
        icsfile.write(ics_content)

    print(f"✓ Successfully created {ics_path}")
    print(f"✓ Added {len(events)} events to calendar")


if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Convert CSV file with events to ICS (iCalendar) format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_to_ics.py Events.csv
  python csv_to_ics.py eventsV2.csv EventsV2.ics
  python csv_to_ics.py /path/to/events.csv /path/to/output.ics
        """
    )

    parser.add_argument('csv_file',
                        help='Input CSV file path')
    parser.add_argument('ics_file',
                        nargs='?',
                        help='Output ICS file path (optional, defaults to input name with .ics extension)')

    args = parser.parse_args()

    # Convert paths to Path objects
    csv_path = Path(args.csv_file)

    # Check if CSV file exists
    if not csv_path.exists():
        print(f"✗ Error: CSV file not found: {csv_path}")
        sys.exit(1)

    # Determine output file path
    if args.ics_file:
        ics_path = Path(args.ics_file)
    else:
        # Use same name as CSV but with .ics extension
        ics_path = csv_path.with_suffix('.ics')

    # Convert CSV to ICS
    try:
        csv_to_ics(csv_path, ics_path)
    except Exception as e:
        print(f"✗ Error converting file: {e}")
        sys.exit(1)
