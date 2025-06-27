import os
import glob
import pandas as pd
from bs4 import BeautifulSoup

def get_html_files(folder_path):
    return glob.glob(os.path.join(folder_path, "*.html"))

def parse_table_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    table = soup.find("table")
    if not table:
        return None
    rows = []
    for tr in table.find_all("tr"):
        cols = tr.find_all(["td", "th"])
        row = [td.get_text(strip=True) for td in cols]
        rows.append(row)
    if len(rows) < 2:
        return None
    header = rows[0]
    df = pd.DataFrame(rows[1:], columns=header)
    return df

def filter_totals(df):
    if "TOTALS" not in df.columns:
        return df
    # Clean the TOTALS column to extract just the numeric part, ignoring text like "points"
    def parse_points(value):
        if not isinstance(value, str):
            return 0
        # extract digits, e.g. "0 points" -> 0, "12 points" -> 12
        import re
        match = re.search(r'\d+', value)
        if match:
            return int(match.group())
        else:
            return 0
    totals_numeric = df["TOTALS"].apply(parse_points)
    filtered_df = df[totals_numeric != 0]
    return filtered_df


def save_csv(df, output_folder, base_name):
    path = os.path.join(output_folder, f"{base_name}.csv")
    df.to_csv(path, index=False)

def write_to_excel(df, excel_writer, sheet_name):
    df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

def main():
    folder = input("Enter folder path containing HTML files: ").strip()
    if not os.path.isdir(folder):
        print(f"Error: Folder '{folder}' does not exist.")
        return
    
    output_folder = os.path.join(folder, "output")
    os.makedirs(output_folder, exist_ok=True)
    
    excel_path = os.path.join(output_folder, "combined_output.xlsx")
    excel_writer = pd.ExcelWriter(excel_path, engine="xlsxwriter")
    
    html_files = get_html_files(folder)
    if not html_files:
        print("No HTML files found in folder.")
        return
    
    for file_path in html_files:
        df = parse_table_from_html(file_path)
        if df is None:
            print(f"No table found in {os.path.basename(file_path)}. Skipping.")
            continue
        
        df_filtered = filter_totals(df)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        save_csv(df_filtered, output_folder, base_name)
        
        sheet_name = base_name[:31]  # Excel sheet name max length
        write_to_excel(df_filtered, excel_writer, sheet_name)
        
        print(f"Processed {base_name}: {len(df_filtered)} rows saved.")
    
    excel_writer.close()
    print(f"\nAll done! CSVs and Excel file saved in: {output_folder}")

if __name__ == "__main__":
    main()
