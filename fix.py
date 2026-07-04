import re

with open('src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of Chapter 5
start_ch5 = content.find('{\n          id: "m1-chapter-5-autonomous-db-tools",')
if start_ch5 == -1:
    print("Could not find Chapter 5")
    exit(1)

# Find the end of Chapter 5
# It ends with           ]\n        }
end_ch5 = content.find('          ]\n        }', start_ch5) + len('          ]\n        }')
if content[end_ch5:end_ch5+1] == ',':
    end_ch5 += 1

ch5_content = content[start_ch5:end_ch5]
# Remove from original
if content[end_ch5:end_ch5+1] == '\n':
    content = content[:start_ch5] + content[end_ch5+1:]
else:
    content = content[:start_ch5] + content[end_ch5:]

# Now we need to insert it into Module 1, after Chapter 4.
start_ch4 = content.find('id: "m1-chapter-4-managing-monitoring",')
# find end of chapter 4
end_ch4 = content.find('          ]\n        }', start_ch4) + len('          ]\n        }')

# Ensure it ends with ,
if content[end_ch4:end_ch4+1] == ',':
    insert_pos = end_ch4 + 1
else:
    content = content[:end_ch4] + ',' + content[end_ch4:]
    insert_pos = end_ch4 + 1

if content[insert_pos] == '\n':
    insert_pos += 1

# make sure ch5_content ends with , because Chapter 7 follows
if ch5_content.endswith(','):
    pass
else:
    ch5_content += ','

content = content[:insert_pos] + '\n        ' + ch5_content.strip() + '\n' + content[insert_pos:]

with open('src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed successfully!")
