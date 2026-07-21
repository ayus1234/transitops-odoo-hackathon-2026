import os
import re

dir_path = r'c:\Users\hp\Downloads\New folder (6)\transitops-odoo-hackathon-2026\frontend\src'

replacements = [
    # Literal $ inside template strings or JSX strings
    (r"`\$\$\{", r"`₹${"), 
    (r">\$\{", r">₹{"),
    (r"\(\$\)", "(₹)"),
    (r"\(k\$\)", "(k₹)"),
    (r": \$\{", r": ₹{"),
    
    # Specific known hardcoded strings
    (r"\$18,290\.00", r"₹18,290.00"),
    (r"\$18\.3k", r"₹18.3k"),
    (r"\$42\.1k", r"₹42.1k"),
    (r"'\$0\.00'", "'₹0.00'"),
    (r"MPG", "KMPL"),
    (r"mpg", "kmpl"),
]

for root, _, files in os.walk(dir_path):
    for f in files:
        if f.endswith('.jsx') or f.endswith('.js'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            orig_content = content
            
            for old, new in replacements:
                content = re.sub(old, new, content)
                
            # Direct text replacements for table cells
            content = content.replace(">${parseFloat(record.total_cost).toFixed(2)}", ">₹{parseFloat(record.total_cost).toFixed(2)}")
            content = content.replace(">${parseFloat(record.amount).toFixed(2)}", ">₹{parseFloat(record.amount).toFixed(2)}")
            content = content.replace(">{p.date}: ${p.cost.toFixed(2)}<", ">{p.date}: ₹{p.cost.toFixed(2)}<")
            content = content.replace(">\n                      ${parseFloat(record.total_cost).toFixed(2)}\n", ">\n                      ₹{parseFloat(record.total_cost).toFixed(2)}\n")
            content = content.replace(">\n                      ${parseFloat(record.amount).toFixed(2)}\n", ">\n                      ₹{parseFloat(record.amount).toFixed(2)}\n")

            if content != orig_content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Updated {f}")
