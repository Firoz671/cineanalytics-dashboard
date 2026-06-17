import json
with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb','r',encoding='utf-8') as f:
    content = f.read()

old = '"from IPython.display import HTML, display"'
new = '""'
content = content.replace(old, new, 1)

with open('D:\\MOVIES DATA\\01_data_cleaning.ipynb','w',encoding='utf-8') as f:
    f.write(content)
print('Replaced successfully')
