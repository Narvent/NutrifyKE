import os

file_path = r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove Dashboard Button
# We look for the dashboard header with the button we added
dashboard_header_with_button = r'''        <div class="bg-white rounded-xl shadow-md p-6 mb-8 border border-gray-100">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-semibold text-gray-700 flex items-center">
                    <svg class="w-6 h-6 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z">
                        </path>
                    </svg>
                    Daily Dashboard
                </h2>
                <button onclick="showReportModal()" class="text-xs bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-1.5 rounded-full transition flex items-center font-medium">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    Report Missing Food
                </button>
            </div>'''

original_dashboard_header = r'''        <div class="bg-white rounded-xl shadow-md p-6 mb-8 border border-gray-100">
            <h2 class="text-xl font-semibold mb-4 text-gray-700 flex items-center">
                <svg class="w-6 h-6 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z">
                    </path>
                </svg>
                Daily Dashboard
            </h2>'''

if dashboard_header_with_button in content:
    content = content.replace(dashboard_header_with_button, original_dashboard_header)
    print("Removed Dashboard Button")
else:
    print("Could not find Dashboard Button block")

# 2. Remove Modal Header Button
# We look for the modal header with the button
modal_header_with_button = r'''            <!-- Header -->
            <div class="bg-primary p-4 text-white shrink-0 flex justify-between items-center">
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

original_modal_header = r'''            <!-- Header -->
            <div class="bg-primary p-4 text-white shrink-0">
                <h3 class="text-lg font-bold flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Confirm Details
                </h3>
            </div>'''

if modal_header_with_button in content:
    content = content.replace(modal_header_with_button, original_modal_header)
    print("Removed Modal Header Button")
else:
    print("Could not find Modal Header Button block")

# 3. Remove Report Modal HTML
# We look for the report modal block
report_modal_html = r'''
    <!-- Report Unknown Food Modal -->
    <div id="report-modal" class="fixed inset-0 bg-black/80 z-[80] hidden flex items-center justify-center backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-fade-in">
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

if report_modal_html in content:
    content = content.replace(report_modal_html, '')
    print("Removed Report Modal HTML")
else:
    # Try finding it without the leading newline if above failed
    report_modal_html_stripped = report_modal_html.strip()
    if report_modal_html_stripped in content:
        content = content.replace(report_modal_html_stripped, '')
        print("Removed Report Modal HTML (stripped)")
    else:
        print("Could not find Report Modal HTML")

# 4. Remove Report Link (if it exists)
report_link = r'''            // Add "Report Missing Food" Link
            const reportLink = document.createElement('div');
            reportLink.className = "text-center mt-4";
            reportLink.innerHTML = `
                <button onclick="showReportModal()" class="text-xs text-gray-400 underline hover:text-primary transition">
                    AI missed something? Report unknown food
                </button>
            `;
            container.appendChild(reportLink);'''

if report_link in content:
    content = content.replace(report_link, '')
    print("Removed Report Link")

# 5. Remove JS Functions
# We'll look for the block of JS we added
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
                // Use the globally stored image file if available
                const formData = new FormData();
                if (currentImageFile) {
                    formData.append('image', currentImageFile);
                }
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

if report_js in content:
    content = content.replace(report_js, '')
    print("Removed Report JS")
else:
    # Try finding parts if full block fails due to edits
    pass

# 6. Remove currentImageFile global
if 'let currentImageFile = null;' in content:
    content = content.replace('let currentImageFile = null;', '')
    print("Removed global variable")

# 7. Revert handleImageUpload
handle_upload_new = 'async function handleImageUpload(event) {\n            const file = event.target.files[0];\n            if (file) currentImageFile = file;'
handle_upload_old = 'async function handleImageUpload(event) {'

if handle_upload_new in content:
    content = content.replace(handle_upload_new, handle_upload_old)
    print("Reverted handleImageUpload")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
