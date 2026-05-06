content = open('G:/projectopencod/testgenerator/main.py', 'r', encoding='utf-8').read()
# Fix the double )) issue
old = 'vk.selected_group_id = str(body["selected_group_id"]))'
new = 'vk.selected_group_id = str(body["selected_group_id"])'
if old in content:
    content = content.replace(old, new)
    open('G:/projectopencod/testgenerator/main.py', 'w', encoding='utf-8').write(content)
    print('Fixed!')
else:
    print('Not found - checking...')
    idx = content.find('selected_group_id = str')
    print(repr(content[idx:idx+80]))
