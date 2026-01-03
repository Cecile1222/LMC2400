import csv
import os
import re

def generate_readings_html(csv_path):
    html_parts = []
    
    # Header
    html_parts.append('    <section id="readings">')
    html_parts.append('        <h2>Reading List</h2>')
    html_parts.append('        <ul class="resource-list">')

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        # Header indices:
        # filename, Q1, Q2, Q3, writer_name, year_of_publish, page_length, key_concepts
        # 0, 1, 2, 3, 4, 5, 6, 7
        
        rows = list(reader)
        # Sort rows by year (index 5). Handle potential non-integer years gracefully if needed, 
        # but assuming valid years for now. converting to int for correct numerical sort.
        rows.sort(key=lambda x: int(x[5]) if x[5].strip().isdigit() else 9999)

        for row in rows:
            if not row or len(row) < 8:
                continue
            
            filename = row[0].strip()

            q1 = row[1].strip()
            q2 = row[2].strip()
            q3 = row[3].strip()
            writer = row[4].strip()
            year = row[5].strip()
            length = row[6].strip()
            keywords = row[7].strip()

            # Clean Title
            title = filename.replace('.pdf', '').replace('_', ' ')
            
            # Start List Item
            html_parts.append('            <li class="reading-item">')
            html_parts.append(f'                <div class="reading-header"><strong>{title}</strong> ({year}) - {writer}</div>')
            html_parts.append(f'                <div class="reading-meta"><em>Keywords: {keywords}</em> | Length: {length} pages</div>')
            
            # Questions
            if q1 or q2 or q3:
                html_parts.append('                <details>')
                html_parts.append('                    <summary>Reading Guide Questions</summary>')
                html_parts.append('                    <ul>')
                if q1: html_parts.append(f'                        <li>{q1}</li>')
                if q2: html_parts.append(f'                        <li>{q2}</li>')
                if q3: html_parts.append(f'                        <li>{q3}</li>')
                html_parts.append('                    </ul>')
                html_parts.append('                </details>')
            
            html_parts.append('            </li>')

    html_parts.append('        </ul>')
    html_parts.append('    </section>')
    return '\n'.join(html_parts)

def update_index_html(index_path, new_content):
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to replace the entire section
    # Matches <section id="readings"> ... </section>
    pattern = re.compile(r'<section id="readings">.*?</section>', re.DOTALL)
    
    if pattern.search(content):
        updated_content = pattern.sub(new_content, content)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Successfully updated index.html")
    else:
        print("Error: Could not find <section id='readings'> in index.html")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, 'ai_studio_data.csv')
    html_file = os.path.join(base_dir, 'index.html')

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
    elif not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
    else:
        new_readings_html = generate_readings_html(csv_file)
        update_index_html(html_file, new_readings_html)
