import os

file_path = r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old function block to replace
old_function = r'''        function updateProgressBar() {
            const progressBar = document.getElementById('progress-bar');
            if (progressBar) {
                const goalInput = document.getElementById('calorie-goal');
                const goal = goalInput ? (parseInt(goalInput.value) || 2500) : 2500;
                const percentage = Math.min((totalCalories / goal) * 100, 100);

                progressBar.style.width = percentage + '%';

                const remaining = Math.max(goal - totalCalories, 0);
                const elRemaining = document.getElementById('calories-remaining');
                if (elRemaining) elRemaining.textContent = Math.round(remaining) + ' kcal remaining';

                const elText = document.getElementById('progress-text');
                if (elText) elText.textContent = Math.round(totalCalories) + ' / ' + goal + ' kcal';

                const elPercent = document.getElementById('progress-percentage');
                if (elPercent) elPercent.textContent = Math.round((totalCalories / goal) * 100) + '% of daily goal';
            }
        }'''

# Define the new function block
new_function = r'''        function updateProgressBar() {
            const progressBar = document.getElementById('progress-bar');
            if (progressBar) {
                const goalInput = document.getElementById('calorie-goal');
                const goal = goalInput ? (parseInt(goalInput.value) || 2500) : 2500;
                
                // Calculate percentage (can go over 100%)
                const rawPercentage = (totalCalories / goal) * 100;
                const displayPercentage = Math.min(rawPercentage, 100); // Bar doesn't grow past 100% width

                progressBar.style.width = displayPercentage + '%';

                const elRemaining = document.getElementById('calories-remaining');
                const elText = document.getElementById('progress-text');
                const elPercent = document.getElementById('progress-percentage');

                if (totalCalories > goal) {
                    // Over Limit State
                    const overBy = Math.round(totalCalories - goal);
                    
                    progressBar.classList.remove('from-green-400', 'to-primary');
                    progressBar.classList.add('from-red-500', 'to-red-600');
                    
                    if (elRemaining) {
                        elRemaining.textContent = `Over limit by ${overBy} kcal`;
                        elRemaining.classList.remove('text-green-600');
                        elRemaining.classList.add('text-red-600', 'animate-pulse');
                    }
                } else {
                    // Under Limit State
                    const remaining = Math.round(goal - totalCalories);
                    
                    progressBar.classList.remove('from-red-500', 'to-red-600');
                    progressBar.classList.add('from-green-400', 'to-primary');
                    
                    if (elRemaining) {
                        elRemaining.textContent = `${remaining} kcal remaining`;
                        elRemaining.classList.remove('text-red-600', 'animate-pulse');
                        elRemaining.classList.add('text-green-600');
                    }
                }

                if (elText) elText.textContent = Math.round(totalCalories) + ' / ' + goal + ' kcal';
                if (elPercent) elPercent.textContent = Math.round(rawPercentage) + '% of daily goal';
            }
        }'''

if old_function in content:
    content = content.replace(old_function, new_function)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated updateProgressBar")
else:
    print("Could not find exact match for updateProgressBar. Checking for partial match...")
    # Fallback: Find by start and end lines if exact match fails due to whitespace
    start_marker = 'function updateProgressBar() {'
    end_marker = 'if (elPercent) elPercent.textContent = Math.round((totalCalories / goal) * 100) + \'% of daily goal\';'
    
    start_idx = content.find(start_marker)
    if start_idx != -1:
        # Find the closing brace of the function (approximate)
        # We know the structure, so we can try to find the end of the block
        # Or just use the known end marker + closing braces
        
        # Let's try to find the block by indentation
        pass
    print("Exact match failed.")
