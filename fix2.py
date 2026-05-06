with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'vk.selected_group_id = str(body["selected_group_id"]))'
new = 'vk.selected_group_id = str(body["selected_group_id"])'

if old in content:
    content = content.replace(old, new)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed double ))!')
else:
    idx = content.find('selected_group_id = str')
    print('Not found, context:', repr(content[idx:idx+80]))
