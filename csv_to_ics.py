#!/usr/bin/env python3
"""
CSV to ICS Converter
Converts a CSV file of events into a single ICS calendar file for Google Calendar import.
"""

import csv
import re
from datetime import datetime, date
from icalendar import Calendar, Event
from dateutil import parser
import argparse


def parse_date_range(month_str, dates_str, year=2026):
    """
    Parse date range from CSV format like 'January' and 'Jan. 12-16'.
    Returns tuple of (start_date, end_date).
    """
    # Clean up the dates string - handle different dash types
    dates_str = dates_str.replace('–', '-').replace('—', '-').strip()

    # Parse the month
    month_abbrev = month_str.strip()

    # Handle date ranges like "Jan. 12-16" or "April 8 - 11"
    # Match patterns like "12-16" or "8 - 11"
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', dates_str)

    if range_match:
        start_day = int(range_match.group(1))
        end_day = int(range_match.group(2))

        # Parse start date
        date_str = f"{month_abbrev} {start_day}, {year}"
        start_date = parser.parse(date_str, fuzzy=True).date()

        # For end date, check if it might be in the next month
        # (e.g., "Dec. 30-Jan. 2")
        try:
            end_date_str = f"{month_abbrev} {end_day}, {year}"
            end_date = parser.parse(end_date_str, fuzzy=True).date()

            # If end_date is before start_date, it's probably next month/year
            if end_date < start_date:
                if start_date.month == 12:
                    # December wrapping to January
                    end_date = date(year + 1, 1, end_day)
                else:
                    # Move to next month
                    next_month = start_date.month + 1
                    end_date = date(year, next_month, end_day)
        except:
            end_date = start_date

        return start_date, end_date

    # Handle single date like "April 8"
    single_match = re.search(r'(\d+)', dates_str)
    if single_match:
        day = int(single_match.group(1))
        date_str = f"{month_abbrev} {day}, {year}"
        single_date = parser.parse(date_str, fuzzy=True).date()
        return single_date, single_date

    # Fallback: try to parse the entire string
    try:
        parsed_date = parser.parse(f"{month_abbrev} {dates_str}, {year}", fuzzy=True).date()
        return parsed_date, parsed_date
    except:
        # If all else fails, return None
        return None, None


def csv_to_ics(csv_file, output_file='events.ics', year=2026):
    """
    Convert CSV file to ICS calendar file.

    Args:
        csv_file: Path to input CSV file
        output_file: Path to output ICS file
        year: Year for the events (default: 2026)
    """
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//CSV to ICS Converter//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'Imported Events')
    cal.add('x-wr-timezone', 'UTC')

    events_added = 0
    errors = []

    # Read CSV and create events
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=2):
            try:
                event_name = row.get('Event Name', '').strip()
                month = row.get('Month', '').strip()
                dates = row.get('Dates', '').strip()
                location = row.get('Location', '').strip()
                primary_focus = row.get('Primary Focus', '').strip()
                geo_cluster = row.get('Geo Cluster', '').strip()
                meta_tags = row.get('Meta Tags (Area of Interest)', '').strip()

                if not event_name:
                    continue

                # Parse dates
                start_date, end_date = parse_date_range(month, dates, year)

                if not start_date or not end_date:
                    errors.append(f"Row {row_num}: Could not parse date for '{event_name}'")
                    continue

                # Create event
                event = Event()
                event.add('summary', event_name)
                event.add('dtstart', start_date)
                # For all-day events, dtend should be the day after the last day
                event.add('dtend', end_date)

                if location:
                    event.add('location', location)

                # Build description
                description_parts = []
                if primary_focus:
                    description_parts.append(f"Focus: {primary_focus}")
                if geo_cluster:
                    description_parts.append(f"Region: {geo_cluster}")
                if meta_tags:
                    description_parts.append(f"Topics: {meta_tags}")

                if description_parts:
                    event.add('description', '\n'.join(description_parts))

                # Add categories from meta tags
                if meta_tags:
                    categories = [tag.strip() for tag in meta_tags.split(';')]
                    event.add('categories', categories)

                cal.add_component(event)
                events_added += 1

            except Exception as e:
                errors.append(f"Row {row_num}: Error processing '{event_name}': {str(e)}")
                continue

    # Write to file
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())

    # Print summary
    print(f"\n{'='*60}")
    print(f"Conversion Complete!")
    print(f"{'='*60}")
    print(f"Events successfully added: {events_added}")
    print(f"Output file: {output_file}")

    if errors:
        print(f"\nWarnings/Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")

    print(f"\nTo import to Google Calendar:")
    print(f"  1. Open Google Calendar")
    print(f"  2. Click the '+' next to 'Other calendars'")
    print(f"  3. Select 'Import'")
    print(f"  4. Choose the file: {output_file}")
    print(f"{'='*60}\n")

    return events_added, errors


def main():
    parser = argparse.ArgumentParser(
        description='Convert CSV events file to ICS calendar format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python csv_to_ics.py Events.csv
  python csv_to_ics.py Events.csv -o my_calendar.ics
  python csv_to_ics.py Events.csv -y 2027
        """
    )

    parser.add_argument('csv_file', help='Input CSV file path')
    parser.add_argument('-o', '--output', default='events.ics',
                       help='Output ICS file path (default: events.ics)')
    parser.add_argument('-y', '--year', type=int, default=2026,
                       help='Year for the events (default: 2026)')

    args = parser.parse_args()

    try:
        csv_to_ics(args.csv_file, args.output, args.year)
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.csv_file}'")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
