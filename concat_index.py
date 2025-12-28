import os

def concat():
    try:
        with open(r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index_part1.html', 'r', encoding='utf-8') as f1:
            part1 = f1.read()
        
        with open(r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index_part2.html', 'r', encoding='utf-8') as f2:
            part2 = f2.read()
            
        with open(r'c:\Users\Churchill\Desktop\NutrifyKE\templates\index.html', 'w', encoding='utf-8') as out:
            out.write(part1)
            out.write(part2)
            
        print("Successfully concatenated index.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    concat()
