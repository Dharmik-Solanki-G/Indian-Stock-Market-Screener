import pandas as pd

# Load the Excel file
file_path = r"C:\Users\Techcureindia\Downloads\Average MCAP_July2024ToDecember 2024.xlsx"
xls = pd.ExcelFile(file_path)

# Show available sheet names
print("Available sheets:", xls.sheet_names)

# Try to load the most likely sheet (adjust if needed)
sheet_to_use = xls.sheet_names[0]  # Default to the first one, or change manually if needed

# Load the sheet
df_avg_mcap = pd.read_excel(xls, sheet_name=sheet_to_use)

# Check which column has symbols
print("Available columns:", df_avg_mcap.columns)

# Assuming the column is named "Symbol" or similar — adjust if needed
symbol_col = "Symbol"  # <- change this if your column name is different

# Extract and format the symbols
symbols = df_avg_mcap[symbol_col].dropna().astype(str).str.upper().str.strip()
formatted_symbols = [f'"{symbol}.NS"' for symbol in symbols]

# Now build the string with a newline after every 15 symbols
lines = []
for i in range(0, len(formatted_symbols), 15):
    chunk = formatted_symbols[i:i+15]
    lines.append(", ".join(chunk))

all_nse_stocks = "all_nse_stocks = [\n    " + ",\n    ".join(lines) + "\n]"

# Print preview
print(all_nse_stocks)  # Preview the first 1000 characters of the result
