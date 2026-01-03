import csv
import os
import re

def generate_schedule_html(csv_path):
    html_parts = []
    
    # Header
    html_parts.append('    <section id="schedule">')
    html_parts.append('        <h2>Schedule</h2>')
    html_parts.append('        <div class="schedule-header schedule-row">')
    html_parts.append('            <div>Date</div>')
    html_parts.append('            <div>Type</div>')
    html_parts.append('            <div>Topic / Readings</div>')
    html_parts.append('            <div>Notes</div>')
    html_parts.append('            <div>Due</div>')
    html_parts.append('        </div>')

    current_month = None

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        for row in reader:
            if not row or len(row) < 5:
                continue
            
            date = row[0].strip()
            type_col = row[1].strip()
            topic = row[2].strip()
            notes = row[3].strip()
            due = row[4].strip()

            # stop if empty date (end of file)
            if not date:
                continue

            # Determine Month
            month_match = re.search(r'([A-Za-z]+)', date)
            if month_match:
                month = month_match.group(1)
                full_month_map = {
                    'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 
                    'Apr': 'April', 'May': 'May', 'Jun': 'June',
                    'Jul': 'July', 'Aug': 'August', 'Sep': 'September',
                    'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
                }
                full_month = full_month_map.get(month, month)
                
                if full_month != current_month:
                    current_month = full_month
                    html_parts.append('')
                    html_parts.append(f'        <!-- {current_month} -->')

            # Format newlines and slashes in topic to <br>
            # Replace / (with optional surrounding whitespace) with <br>
            # Clean up potential messiness where a ? ends a sentence immediately followed by text
            # But primarily rely on / and newlines as requested
            
            topic_clean = topic
            # Replace / with <br>
            topic_clean = re.sub(r'\s*/\s*', '<br>', topic_clean)
            # Replace newlines with <br>
            topic_clean = topic_clean.replace('\n', '<br>')
            
            # Capitalize first letter of each line
            parts = topic_clean.split('<br>')
            capitalized_parts = []
            for part in parts:
                part = part.strip()
                if part:
                    # maximize first char, leave rest alone (don't use capitalize() as it lowers the rest)
                    part = part[0].upper() + part[1:]
                capitalized_parts.append(part)
            
            topic_html = '<br>'.join(capitalized_parts)
            
            html_parts.append('        <div class="schedule-row">')
            html_parts.append(f'            <div class="schedule-date">{date}</div>')
            html_parts.append(f'            <div>{type_col}</div>')
            html_parts.append(f'            <div>{topic_html}</div>')
            html_parts.append(f'            <div>{notes}</div>')
            html_parts.append(f'            <div>{due}</div>')
            html_parts.append('        </div>')

    html_parts.append('    </section>')
    return '\n'.join(html_parts)

def update_index_html(index_path, new_content):
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to replace the entire section
    # Matches <section id="schedule"> ... </section>
    pattern = re.compile(r'<section id="schedule">.*?</section>', re.DOTALL)
    
    if pattern.search(content):
        updated_content = pattern.sub(new_content, content)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Successfully updated index.html")
    else:
        print("Error: Could not find <section id='schedule'> in index.html")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, 'schedule.csv')
    html_file = os.path.join(base_dir, 'index.html')

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
    elif not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
    else:
        new_schedule_html = generate_schedule_html(csv_file)
        update_index_html(html_file, new_schedule_html)
