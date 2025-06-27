import os
import csv
from bs4 import BeautifulSoup

def extract_tables_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    all_rows = []

    for table_idx, table in enumerate(tables):
        # Get all rows
        rows = table.find_all('tr')
        for row in rows:
            # Get all cells (both td and th)
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            if cell_texts:
                all_rows.append(cell_texts)
    return all_rows

def main():
    folder_path = input("Enter the parent folder path containing your HTML files: ").strip()

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return

    combined_data = []
    header_written = False

    # We'll track max columns to normalize rows later
    max_cols = 0

    # Find all html files recursively
    html_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))

    if not html_files:
        print("No HTML files found in the folder.")
        return

    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        rows = extract_tables_from_html(content)
        if not rows:
            print(f"⚠ No tables found in {filepath}")
            continue

        for row in rows:
            max_cols = max(max_cols, len(row))
            combined_data.append([os.path.relpath(filepath, folder_path)] + row)

    if not combined_data:
        print("No table data extracted from any file.")
        return

    # Normalize rows: pad with empty strings so all rows have same length
    for i in range(len(combined_data)):
        row = combined_data[i]
        if len(row) < max_cols + 1:  # +1 because first col is filename
            combined_data[i] = row + [''] * (max_cols + 1 - len(row))

    output_csv = os.path.join(folder_path, 'combined_output.csv')
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header: File, Col1, Col2, ...
        header = ['SourceFile'] + [f'Col{i+1}' for i in range(max_cols)]
        writer.writerow(header)
        writer.writerows(combined_data)

    print(f"Combined CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
