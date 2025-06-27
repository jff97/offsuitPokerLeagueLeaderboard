import os
import pandas as pd
from bs4 import BeautifulSoup

# Ask for folder via terminal
folder_path = input("Enter the full path to the folder containing your HTML files: ").strip('"')

output_folder = os.path.join(folder_path, "output")
os.makedirs(output_folder, exist_ok=True)

excel_writer = pd.ExcelWriter(os.path.join(output_folder, "combined_output.xlsx"), engine="xlsxwriter")

# Process each HTML file
for filename in os.listdir(folder_path):
    if not filename.lower().endswith(".html"):
        continue

    file_path = os.path.join(folder_path, filename)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        soup = BeautifulSoup(file, "html.parser")

    table = soup.find("table")
    if table is None:
        print(f"⚠ No table found in {filename}")
        continue

    rows = []
    for tr in table.find_all("tr"):
        row = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        rows.append(row)

    df = pd.DataFrame(rows)
    df.insert(0, "SourceFile", filename)

    # Save to individual CSV
    csv_name = os.path.splitext(filename)[0] + ".csv"
    df.to_csv(os.path.join(output_folder, csv_name), index=False, header=False)

    # Add to Excel as separate sheet
    sheet_name = os.path.splitext(filename)[0][:31]  # Excel sheet names max out at 31 chars
    df.to_excel(excel_writer, sheet_name=sheet_name, index=False, header=False)

# Save the Excel workbook
excel_writer.close()

print(f"\n✅ Done! All output is in: {output_folder}")
