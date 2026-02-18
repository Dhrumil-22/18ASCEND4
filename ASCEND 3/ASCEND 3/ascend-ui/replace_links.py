import os

root_dir = r"c:\Users\91940\Downloads\@ COLLAGE\LJIET\python prop\SCEND 4\ASCEND 3\ASCEND 3\ascend-ui"

replacements = {
    'mentor-discussion.html': 'discussion.html',
    'profile.htm"': 'profile.html"'
}

count = 0

try:
    for filename in os.listdir(root_dir):
        if filename.endswith(".html") or filename.endswith(".js"):
            filepath = os.path.join(root_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                for old, new in replacements.items():
                    new_content = new_content.replace(old, new)
                    
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filename}")
                    count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Total files updated: {count}")
except Exception as e:
    print(f"Fatal error: {e}")
