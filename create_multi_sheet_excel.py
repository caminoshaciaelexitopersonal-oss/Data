import pandas as pd

df1 = pd.DataFrame({'Data1': [10, 20], 'Data2': [30, 40]})
df2 = pd.DataFrame({'Info1': [50, 60], 'Info2': [70, 80]})

with pd.ExcelWriter('multi_sheet_test.xlsx', engine='xlsxwriter') as writer:
    df1.to_excel(writer, sheet_name='Sales', index=False)
    df2.to_excel(writer, sheet_name='Inventory', index=False)
