import os

file_path = r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Button to showVerificationModal
old_button_code = r'''            // Add "Add Item" Button
            const addButton = document.createElement('button');
            addButton.onclick = addVerificationItem;
            addButton.className = "w-full py-2 mt-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-primary hover:text-primary font-semibold text-sm transition flex items-center justify-center";
            addButton.innerHTML = `
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Add Another Item
            `;
            container.appendChild(addButton);

            modal.classList.remove('hidden');
        }'''

new_button_code = r'''            // Add "Add Item" Button
            const addButton = document.createElement('button');
            addButton.onclick = addVerificationItem;
            addButton.className = "w-full py-2 mt-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-primary hover:text-primary font-semibold text-sm transition flex items-center justify-center";
            addButton.innerHTML = `
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Add Another Item
            `;
            container.appendChild(addButton);

            // Add "Report Missing Food" Link
            const reportLink = document.createElement('div');
            reportLink.className = "text-center mt-4";
            reportLink.innerHTML = `
                <button onclick="showReportModal()" class="text-xs text-gray-400 underline hover:text-primary transition">
                    AI missed something? Report unknown food
                </button>
            `;
            container.appendChild(reportLink);

            modal.classList.remove('hidden');
        }'''

if old_button_code in content:
    content = content.replace(old_button_code, new_button_code)
    print("Added Report button")
else:
    print("Could not find location for Report button")

# 2. Add Report Modal HTML
# We'll append it after the verification-modal
modal_marker = '<div id="verification-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-50 p-4">'
report_modal_html = r'''
    <!-- Report Unknown Food Modal -->
    <div id="report-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-60 p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
            <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                <h3 class="font-bold text-gray-800">Report Unknown Food</h3>
                <button onclick="closeReportModal()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
            <div class="p-6 space-y-4">
                <p class="text-sm text-gray-600">Help us improve! If the AI missed a food or identified it incorrectly, please tell us what it is.</p>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Food Name / Description</label>
                    <input type="text" id="report-description" placeholder="e.g. Matoke, Githeri, etc." 
                        class="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-primary outline-none transition">
                </div>

                <button onclick="submitReport()" id="btn-submit-report" class="w-full bg-primary text-white font-bold py-3 rounded-xl shadow-lg hover:bg-green-600 transition transform active:scale-95">
                    Submit Report
                </button>
            </div>
        </div>
    </div>
'''

if modal_marker in content:
    # Insert before the verification modal (or after, doesn't matter much, but let's do before to keep modals together)
    content = content.replace(modal_marker, report_modal_html + '\n    ' + modal_marker)
    print("Added Report Modal HTML")
else:
    print("Could not find verification-modal to insert report-modal")

# 3. Add JS Functions
# We'll append these to the end of the script block, before the closing </script>
js_marker = '    </script>'
report_js = r'''
        // --- REPORTING LOGIC ---
        function showReportModal() {
            document.getElementById('report-modal').classList.remove('hidden');
        }

        function closeReportModal() {
            document.getElementById('report-modal').classList.add('hidden');
            document.getElementById('report-description').value = '';
        }

        async function submitReport() {
            const description = document.getElementById('report-description').value;
            if (!description) {
                alert("Please enter a description.");
                return;
            }

            const btn = document.getElementById('btn-submit-report');
            const originalText = btn.innerText;
            btn.innerText = "Submitting...";
            btn.disabled = true;

            try {
                // We need the image file. It's in the file input 'camera-input'
                const fileInput = document.getElementById('camera-input');
                if (!fileInput.files || fileInput.files.length === 0) {
                    alert("No image found to report.");
                    return;
                }

                const formData = new FormData();
                formData.append('image', fileInput.files[0]);
                formData.append('description', description);

                const response = await fetch('/api/report-unknown', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                if (response.ok) {
                    alert("Thank you! Your report has been submitted.");
                    closeReportModal();
                } else {
                    alert("Error submitting report: " + result.error);
                }
            } catch (error) {
                console.error("Error reporting:", error);
                alert("An error occurred.");
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        }
'''

if js_marker in content:
    # Find the LAST occurrence of </script>
    last_script_idx = content.rfind(js_marker)
    if last_script_idx != -1:
        content = content[:last_script_idx] + report_js + content[last_script_idx:]
        print("Added Report JS")
    else:
        print("Could not find closing script tag")
else:
    print("Could not find closing script tag marker")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
