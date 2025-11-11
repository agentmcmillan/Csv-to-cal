# CSV to ICS Calendar Converter

A Python tool to convert CSV event files into ICS (iCalendar) format for easy import into Google Calendar, Apple Calendar, Outlook, and other calendar applications.

## Features

- Converts multiple events from CSV into a single ICS file
- Handles date ranges (e.g., "Jan. 12-16")
- Creates all-day events automatically
- Includes event details: location, description, and categories
- Easy Google Calendar import
- Command-line interface with options

## Installation

1. Make sure you have Python 3.6+ installed
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert your CSV file to ICS:

```bash
python csv_to_ics.py Events.csv
```

This will create an `events.ics` file in the current directory.

### Advanced Options

Specify a custom output file:

```bash
python csv_to_ics.py Events.csv -o my_calendar.ics
```

Specify a different year for events:

```bash
python csv_to_ics.py Events.csv -y 2027
```

### Command-line Options

- `csv_file` - Path to your input CSV file (required)
- `-o, --output` - Output ICS file path (default: events.ics)
- `-y, --year` - Year for the events (default: 2026)
- `-h, --help` - Show help message

## CSV Format

Your CSV file should have the following columns:

- **Month** - Month name (e.g., "January", "Feb.")
- **Event Name** - Name of the event
- **Dates** - Date or date range (e.g., "Jan. 12-16", "April 8 - 11")
- **Location** - Event location (optional)
- **Primary Focus** - Main topic/focus (optional)
- **Geo Cluster** - Geographic region (optional)
- **Meta Tags (Area of Interest)** - Semicolon-separated tags (optional)

### Example CSV

```csv
Month,Event Name,Dates,Location,Primary Focus,Geo Cluster,Meta Tags (Area of Interest)
January,Tech Conference,Jan. 12-16,"San Francisco, CA, USA","Technology, Innovation",NA,Technology; Innovation; Research
February,Industry Summit,Feb. 3-5,"New York, NY, USA",Business Strategy,NA,Strategy; Business; Leadership
```

## Importing to Google Calendar

1. Run the converter to create your ICS file
2. Open [Google Calendar](https://calendar.google.com)
3. Click the **+** button next to "Other calendars" (left sidebar)
4. Select **Import**
5. Click **Select file from your computer**
6. Choose the generated ICS file (e.g., `events.ics`)
7. Select which calendar to add events to
8. Click **Import**

## Importing to Other Calendar Apps

### Apple Calendar (macOS/iOS)
- Double-click the ICS file, or
- File → Import → Select the ICS file

### Microsoft Outlook
- File → Open & Export → Import/Export
- Select "Import an iCalendar (.ics) or vCalendar file"
- Choose the ICS file

### Other Applications
Most calendar applications support importing ICS files through their File or Import menus.

## Troubleshooting

### Date Parsing Issues

If some events don't import correctly, check that:
- The Month column contains valid month names
- The Dates column follows the format "Day-Day" or "MonthAbbrev Day-Day"
- The year is specified correctly with the `-y` option

### Missing Events

The converter will report any events that couldn't be processed. Check the console output for warnings and errors.

## Example Output

After running the converter, you'll see:

```
============================================================
Conversion Complete!
============================================================
Events successfully added: 45
Output file: events.ics

To import to Google Calendar:
  1. Open Google Calendar
  2. Click the '+' next to 'Other calendars'
  3. Select 'Import'
  4. Choose the file: events.ics
============================================================
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Issues and pull requests are welcome!
