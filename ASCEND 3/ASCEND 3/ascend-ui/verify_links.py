import os
import re

root_dir = r"c:\Users\91940\Downloads\@ COLLAGE\LJIET\python prop\SCEND 4\ASCEND 3\ASCEND 3\ascend-ui"

# Regex patterns
html_href_pattern = re.compile(r'href=["\']([^"\']+)["\']')
js_location_pattern = re.compile(r'window\.location\.href\s*=\s*["\']([^"\']+)["\']')
js_setAttribute_pattern = re.compile(r'.setAttribute\(["\']href["\']\s*,\s*["\']([^"\']+)["\']\)')

# Files to ignore (external links, anchors, mailto, etc.)
def is_valid_link(link):
    if link.startswith('http') or link.startswith('https') or link.startswith('mailto:') or link.startswith('#') or link.startswith('javascript:'):
        return True # External or special links are "valid" in the sense that we don't check filesystem
    return False

# Get all files in directory
all_files = set()
for f in os.listdir(root_dir):
    all_files.add(f)

broken_links = []

for filename in os.listdir(root_dir):
    filepath = os.path.join(root_dir, filename)
    
    if filename.endswith(".html"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        links = html_href_pattern.findall(content)
        # Check for onclick redirects too if simple
        onclick_links = re.findall(r'window\.location\.href=[\'"]([^\'"]+)[\'"]', content)
        links.extend(onclick_links)

        for link in links:
            # Handle query params
            clean_link = link.split('?')[0]
            
            if is_valid_link(clean_link):
                continue
                
            # Handle prefix logic if any (assuming flat for now)
            # If link depends on JS variables like ${q.id}, we check the base
            if '${' in clean_link:
                continue # Dynamic template string, skip or partial check logic needed?
                
            if clean_link not in all_files:
                # Check if it exists in subfolders?
                if '/' in clean_link:
                    # check subfolder existence
                    if not os.path.exists(os.path.join(root_dir, clean_link)):
                        broken_links.append(f"{filename}: {link} -> File not found")
                elif clean_link == "": 
                    continue
                else:
                    broken_links.append(f"{filename}: {link} -> File not found")

    elif filename.endswith(".js"):
         with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check JS patterns look for string literals
            # This is harder because of variables, but we can check explicit strings
            matches = js_location_pattern.findall(content)
            matches.extend(js_setAttribute_pattern.findall(content))
            
            for link in matches:
                clean_link = link.split('?')[0]
                if is_valid_link(clean_link): continue
                if '${' in clean_link: continue
                
                if clean_link not in all_files and '/' not in clean_link:
                     broken_links.append(f"{filename}: {link} -> File not found")

if broken_links:
    print("Broken Links Found:")
    for b in broken_links:
        print(b)
else:
    print("No broken links found!")
