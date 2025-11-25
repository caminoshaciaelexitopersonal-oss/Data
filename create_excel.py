import pandas as pd

data = {'ID': [5, 6, 7],
        'Producto': ['A', 'B', 'C'],
        'Ventas': [100, 150, 200]}
df = pd.DataFrame(data)

df.to_excel('test_data.xlsx', index=False, sheet_name='Ventas')
