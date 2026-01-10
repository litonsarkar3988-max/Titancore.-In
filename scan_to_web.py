import ast
import os

def get_scan_data():
    # নিজের ফাইল বাদে বাকি সব .py ফাইল স্ক্যান করবে
    files = [f for f in os.listdir('.') if f.endswith('.py') and f not in ['scan_to_web.py', 'main.py']]
    findings = []
    
    for file in files:
        try:
            with open(file, 'r') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                # লাইব্রেরি ইমপোর্ট চেক
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    libs = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module]
                    for lib in libs:
                        if lib in ['os', 'subprocess', 'requests', 'sys', 'socket']:
                            findings.append(f"<tr><td style='padding:8px; border-bottom:1px solid #eee;'>{file}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{node.lineno}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{lib}</td><td style='padding:8px; border-bottom:1px solid #eee; color:#ff3b30; font-weight:bold;'>🚩 DANGER</td></tr>")
                
                # বিপজ্জনক ফাংশন চেক
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        findings.append(f"<tr><td style='padding:8px; border-bottom:1px solid #eee;'>{file}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{node.lineno}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{node.func.id}()</td><td style='padding:8px; border-bottom:1px solid #eee; color:#8b0000; font-weight:bold;'>💀 EXTREME</td></tr>")
        except: pass
    return findings

def update_html(data):
    # HTML টেবিল ডিজাইন
    table = "<div style='overflow-x:auto; margin-top:10px;'><table style='width:100%; border-collapse:collapse; font-size:11px; text-align:left; border:1px solid #eee;'>"
    table += "<tr style='background:#f9f9fb;'> <th style='padding:10px;'>File</th> <th style='padding:10px;'>Line</th> <th style='padding:10px;'>Issue</th> <th style='padding:10px;'>Status</th> </tr>"
    table += "\n".join(data) if data else "<tr><td colspan='4' style='padding:20px; text-align:center;'>✅ All local assets are secured.</td></tr>"
    table += "</table></div>"

    if os.path.exists("index.html"):
        with open("index.html", "r") as f:
            content = f.read()

        # রাহুল, তোমার দেওয়া সেই মার্কারগুলো এখানে সেট করা হয়েছে
        start_marker = '<div id="audit-data">'
        end_marker = '</div>'

        if start_marker in content and end_marker in content:
            # ফাইলটিকে দুই ভাগে ভাগ করা হচ্ছে
            parts = content.split(start_marker)
            # দ্বিতীয় ভাগটিকে প্রথম </div> দিয়ে ভাগ করা হচ্ছে যাতে ডিজাইন নষ্ট না হয়
            after_start = parts[1].split(end_marker, 1)
            
            # নতুন HTML তৈরি
            new_html = parts[0] + start_marker + "\n" + table + "\n" + end_marker + after_start[1]
            
            with open("index.html", "w") as f:
                f.write(new_html)
            
            print("✅ [Titancore] Local report updated in index.html")
            
            # গিটহাবে পুশ করার অটোমেশন
            print("📤 Syncing with GitHub...")
            os.system("git add index.html && git commit -m 'Auto Audit Sync' && git push origin main")
            print("🚀 Process Complete! Check your website.")
        else:
            print(f"❌ Error: index.html-এ '{start_marker}' খুঁজে পাওয়া যায়নি।")
    else:
        print("❌ Error: index.html ফাইলটি ডিরেক্টরিতে নেই।")

if __name__ == "__main__":
    update_html(get_scan_data())
