import re

with open('chapter4.ts', 'r', encoding='utf-8') as f:
    ch_content = f.read()

obj_start = ch_content.find('{\n          id: "m1-chapter-4')
if obj_start == -1:
    obj_start = ch_content.find('{')
    
ch_obj = ch_content[obj_start:]

with open('src/App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

ch_idx = -1
for i, line in enumerate(app_lines):
    if 'm1-chapter-3-autonomous-db-dedicated' in line:
        ch_idx = i
        break

if ch_idx == -1:
    print("Could not find previous chapter")
else:
    end_idx = -1
    for i in range(ch_idx, len(app_lines)):
        if '          ]' in app_lines[i] and '        }' in app_lines[i+1] and ('      ]' in app_lines[i+2] or '        },' in app_lines[i+2]):
            end_idx = i+1
            break
            
    if end_idx != -1:
        app_lines[end_idx] = '        },\n'
        app_lines.insert(end_idx + 1, ch_obj + '\n')
        
        with open('src/App.tsx', 'w', encoding='utf-8') as f:
            f.writelines(app_lines)
        print("Injected successfully!")
    else:
        print("Could not find end of previous chapter")
