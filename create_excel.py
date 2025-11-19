import pandas as pd

# Create a sample DataFrame
data = {'id': [1, 2], 'name': ['test1', 'test2'], 'value': [100, 200]}
df = pd.DataFrame(data)

# Create an Excel writer
try:
    with pd.ExcelWriter('test_data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    print("test_data.xlsx created successfully.")
except Exception as e:
    print(f"Error creating Excel file: {e}")
