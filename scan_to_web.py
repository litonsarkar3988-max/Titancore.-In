import os
import datetime

# --- ১. কনফিগারেশন এবং স্ক্যানিং লজিক ---
scanned_files = 0
high_risks = 0
audit_results = ""

# বিপজ্জনক কি-ওয়ার্ড (Titancore সুরক্ষা দেবা)
DANGER_KEYWORDS = ["os.system", "subprocess", "eval", "base64.b64decode", "exec("]

# বর্তমান ফোল্ডারের সব .py ফাইল স্ক্যান করা
for file in os.listdir("."):
    if file.endswith(".py") and file != "scan_to_web.py":
        scanned_files += 1
        risk_found = False
        
        try:
            with open(file, "r", errors="ignore") as f:
                code = f.read()
                for word in DANGER_KEYWORDS:
                    if word in code:
                        risk_found = True
                        high_risks += 1
                        break
            
            status = "<span style='color: #ff3b30; font-weight:bold;'>🚩 DANGER</span>" if risk_found else "<span style='color: #28cd41;'>✅ SECURE</span>"
            audit_results += f"<tr><td style='padding:10px; border-bottom:1px solid #eee;'>{file}</td><td style='padding:10px; border-bottom:1px solid #eee;'>{status}</td></tr>"
        except:
            continue

# --- ২. ড্যাশবোর্ড তৈরি (Apple Style) ---
now = datetime.datetime.now().strftime("%d %b, %y | %I:%M %p")
risk_color = "#ff3b30" if high_risks > 0 else "#28cd41"

dashboard_html = f"""
<div style="background: #fdfdfd; padding: 15px; border-radius: 20px; margin: 20px 0; border: 1px solid #eee; display: flex; justify-content: space-around; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
    <div style="text-align: center;">
        <p style="color: #86868b; font-size: 11px; margin: 0; font-weight: 600; text-transform: uppercase;">Scanned</p>
        <h2 style="color: #1d1d1f; margin: 5px 0; font-size: 20px;">{scanned_files}</h2>
    </div>
    <div style="text-align: center; border-left: 1px solid #eee; border-right: 1px solid #eee; padding: 0 20px;">
        <p style="color: #86868b; font-size: 11px; margin: 0; font-weight: 600; text-transform: uppercase;">High Risk</p>
        <h2 style="color: {risk_color}; margin: 5px 0; font-size: 20px; font-weight: 800; text-shadow: 0 0 10px {risk_color}44;">{high_risks}</h2>
    </div>
    <div style="text-align: center;">
        <p style="color: #86868b; font-size: 11px; margin: 0; font-weight: 600; text-transform: uppercase;">Last Scan</p>
        <h2 style="color: #0071e3; margin: 5px 0; font-size: 11px; line-height: 20px;">{now}</h2>
    </div>
</div>
"""

# --- ৩. index.html আপডেট করা ---
try:
    with open("index.html", "r") as f:
        content = f.read()

    # ১. ড্যাশবোর্ড মার্কার আপডেট (Apple Style Dashboard)
    # চ্যাট সিস্টেমে অদৃশ্য হওয়া ঠেকাতে এই বিশেষ ফরম্যাট ব্যবহার করা হয়েছে
    d_start_tag = f"<{''}-- DASHBOARD_START --{''}>"
    d_end_tag = f"<{''}-- DASHBOARD_END --{''}>"

    if d_start_tag in content:
        parts = content.split(d_start_tag)
        start_part = parts[0]
        end_part = parts[1].split(d_end_tag)[1]
        
        # নতুন ড্যাশবোর্ড বসানো
        content = start_part + d_start_tag + dashboard_html + d_end_tag + end_part

    # ২. অডিট টেবিল আপডেট (Termux Audit Report)
    t_marker = '<div id="audit-data">'
    if t_marker in content:
        t_parts = content.split(t_marker)
        before_table = t_parts[0]
        after_table = t_parts[1].split('</div>', 1)[1]
        
        table_html = f"<table style='width:100%; border-collapse: collapse; font-size:12px;'>{audit_results}</table>"
        content = before_table + t_marker + table_html + '</div>' + after_table

    with open("index.html", "w") as f:
        f.write(content)
    print("✅ [Titancore] Local update successful.")

    # --- ৪. অটোমেটিক গিট পুশ (সুরক্ষা দেবা) ---
    print("📤 Syncing with GitHub...")
    os.system("git add .")
    os.system(f'git commit -m "Security Audit Sync: {high_risks} risks found"')
    os.system("git push origin main")
    print("🚀 MISSION ACCOMPLISHED! Check your website.")

except Exception as e:
    print(f"❌ Error: {str(e)}")
