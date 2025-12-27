import os

file_path = r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update submitReport to make image optional
old_submit_logic = r'''                // Use the globally stored image file
                if (!currentImageFile) {
                    alert("No image found to report. Please try scanning again.");
                    return;
                }

                const formData = new FormData();
                formData.append('image', currentImageFile);'''

new_submit_logic = r'''                // Use the globally stored image file if available
                const formData = new FormData();
                if (currentImageFile) {
                    formData.append('image', currentImageFile);
                }'''

if old_submit_logic in content:
    content = content.replace(old_submit_logic, new_submit_logic)
    print("Updated submitReport logic")
else:
    # Try the previous version if the last script failed or was different
    old_submit_logic_v1 = r'''                // We need the image file. It's in the file input 'camera-input'
                const fileInput = document.getElementById('camera-input');
                if (!fileInput.files || fileInput.files.length === 0) {
                    alert("No image found to report.");
                    return;
                }

                const formData = new FormData();
                formData.append('image', fileInput.files[0]);'''
    
    if old_submit_logic_v1 in content:
        content = content.replace(old_submit_logic_v1, new_submit_logic)
        print("Updated submitReport logic (from v1)")
    else:
        print("Could not find submitReport logic to update")

# 2. Add Prominent Icon to Header
# The user wants it "outstanding visible like the camera icon".
# We'll put it in the header, right aligned, with a distinct color (e.g., Yellow/Orange).

# Find the header block. 
# Current header might be the original one if previous script failed, or the new one.
# Let's look for the "Confirm Details" text and the surrounding div.

# We will try to replace the entire header div content.
header_start_marker = '<div class="bg-primary p-4 text-white shrink-0'
header_end_marker = 'Confirm Details\n                </h3>\n            </div>'
# This is tricky because of potential flex classes added previously.

# Let's try to find the specific H3 and inject the button after it if it's not there.
h3_content = 'Confirm Details\n                </h3>'

if h3_content in content:
    # Check if button already exists
    if 'onclick="showReportModal()"' not in content[content.find(h3_content)-200:content.find(h3_content)+200]:
        # It's not there. We need to replace the parent div to be flex.
        # Let's find the parent div start.
        div_start = content.rfind('<div class="bg-primary', 0, content.find(h3_content))
        if div_start != -1:
            div_end = content.find('</div>', content.find(h3_content)) + 6
            
            old_header = content[div_start:div_end]
            
            # New header with flex and button
            new_header = r'''<div class="bg-primary p-4 text-white shrink-0 flex justify-between items-center">
                <h3 class="text-lg font-bold flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Confirm Details
                </h3>
                <button onclick="showReportModal()" class="bg-white text-primary hover:bg-yellow-100 font-bold py-1 px-3 rounded-full text-xs shadow-md transition flex items-center animate-pulse">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    Report Issue
                </button>
            </div>'''
            
            content = content.replace(old_header, new_header)
            print("Updated Header with Prominent Button")
        else:
            print("Could not find header div start")
    else:
        print("Report button seems to already exist in header")
else:
    print("Could not find H3 content")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
