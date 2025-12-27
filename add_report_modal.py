import os

file_path = r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Marker for Verification Modal
modal_marker = '<div id="verification-modal"'
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

if modal_marker in content:
    # Check if we already added it (to avoid duplicates if re-running)
    if 'id="report-modal"' not in content:
        content = content.replace(modal_marker, report_modal_html + '\n    ' + modal_marker)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully added Report Modal HTML")
    else:
        print("Report Modal already exists")
else:
    print("Could not find verification-modal marker")
