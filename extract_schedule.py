from html.parser import HTMLParser
import csv
import sys
import re

class ScheduleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_schedule = False
        self.in_row = False
        self.in_cell = False
        self.div_level = 0 # Track div nesting to know when row ends
        self.cell_div_level = 0 # Track div nesting within cell (though cells seem flat)
        
        self.rows = []
        self.current_row = []
        self.current_cell_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get('class', '').split()
        id_val = attrs_dict.get('id', '')

        if tag == 'section' and id_val == 'schedule':
            self.in_schedule = True
        
        if not self.in_schedule:
            return

        if tag == 'div':
            if 'schedule-row' in classes:
                # Start of a row
                self.in_row = True
                self.div_level = 1 # 1 level deep (the row div itself)
                self.current_row = []
                self.current_cell_text = [] # Clear temp
            elif self.in_row:
                # Inside a row, any direct child div is a cell
                # We assume cells are direct children (depth 2)
                self.div_level += 1
                if self.div_level == 2:
                    self.in_cell = True
                    self.cell_div_level = 1
                    self.current_cell_text = []
                elif self.in_cell:
                    self.cell_div_level += 1
        
        # Determine if this row is the header or body
        # (We can filter later based on content)

    def handle_endtag(self, tag):
        if not self.in_schedule:
            return

        if tag == 'section':
            self.in_schedule = False
        
        if tag == 'div' and self.in_row:
            if self.in_cell:
                if self.cell_div_level > 1:
                    self.cell_div_level -= 1
                else:
                    # Closing the cell
                    self.in_cell = False
                    self.cell_div_level = 0
                    full_text = "".join(self.current_cell_text).strip()
                    # Clean up: replace <br> (which wouldn't be in data) ... wait data is text.
                    # Text content comes from handle_data.
                    # If there was a <br> tag it was skipped by handle_data but we might want a separator.
                    # We'll handle 'br' in starttag if we want to keep it as newline.
                    self.current_row.append(full_text)
            
            self.div_level -= 1
            if self.div_level == 0:
                # Closing the row
                self.in_row = False
                if self.current_row:
                    self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            # simple text cleaning
            text = re.sub(r'\s+', ' ', data)
            self.current_cell_text.append(text)

    def handle_startendtag(self, tag, attrs):
        # Handle self-closing like <br>
        if self.in_cell and tag == 'br':
             self.current_cell_text.append('\n')

def run():
    parser = ScheduleParser()
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        parser.feed(content)
        
        # Filter rows: Ensure 4 columns.
        valid_rows = []
        header = ['Date', 'Topic / Readings', 'Notes', 'Due']
        valid_rows.append(header)
        
        for row in parser.rows:
            # Heuristic: Valid data rows usually have 4 columns.
            # The header row in HTML has 'Date', 'Topic / Readings' etc. 
            # If we extracted the header row from HTML, we should deduplicate or use it.
            # Let's check if the row looks like the header.
            
            cleaned_row = [c.strip() for c in row if c.strip()]
            if not cleaned_row:
                continue
                
            # If it's the header row from HTML
            if 'Date' in row and 'Note' in str(row):
                # Skip, we added our own header, or we can use it.
                continue
                
            # Pad or Trim to 4 cols
            # If it has <4 cols, pad with empty.
            if len(row) < 4:
                row += [''] * (4 - len(row))
            valid_rows.append(row[:4])
            
        with open('schedule.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(valid_rows)
            
        print(f"Successfully wrote {len(valid_rows)} rows (including header) to schedule.csv")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run()
