with open('temp_figma_extract/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Length of file:", len(text))
tabs = re.findall(r'onclick="switchTab\(\'([^\']+)\'\)"', text)
print("Tabs:", tabs)

# Look for footer area
footer_idx = text.find('<footer')
print("Footer index:", footer_idx)
print("Footer content:\n", text[footer_idx:footer_idx+800])
