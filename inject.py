import re

with open('chapter3.ts', 'r', encoding='utf-8') as f:
    ch3_content = f.read()

# Remove the surrounding brackets that I might have generated, or just extract the object
# Since my generate script outputted:
#         {
#           id: "m1-chapter-3...",
# ...
#         }
# Let's just find where id: "m1-chapter-3 is.
obj_start = ch3_content.find('{\n          id: "m1-chapter-3')
if obj_start == -1:
    # try looking for just {
    obj_start = ch3_content.find('{')
    
ch3_obj = ch3_content[obj_start:]

with open('src/App.tsx', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

# The end of Chapter 2 is at line 168 (index 167):
# 167:           ]
# 168:         }
# 169:       ]

# Find where 'm1-chapter-2-autonomous-db-serverless' is
ch2_idx = -1
for i, line in enumerate(app_lines):
    if 'm1-chapter-2-autonomous-db-serverless' in line:
        ch2_idx = i
        break

if ch2_idx == -1:
    print("Could not find ch2")
else:
    # find the next ], } that closes chapter 2.
    end_idx = -1
    for i in range(ch2_idx, len(app_lines)):
        if '          ]' in app_lines[i] and '        }' in app_lines[i+1] and '      ]' in app_lines[i+2]:
            end_idx = i+1
            break
            
    if end_idx != -1:
        # replace line end_idx with         }, and then insert ch3
        app_lines[end_idx] = '        },\n'
        
        # prepend spaces to ch3_obj to align it if necessary, but it should be already aligned
        app_lines.insert(end_idx + 1, ch3_obj + '\n')
        
        with open('src/App.tsx', 'w', encoding='utf-8') as f:
            f.writelines(app_lines)
        print("Injected successfully!")
    else:
        print("Could not find end of chapter 2")
