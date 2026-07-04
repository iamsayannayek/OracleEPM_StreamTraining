import json
import re

with open('ch4_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

questions = []
current_question = None

lines = text.split('\n')
for line in lines:
    line = line.strip()
    if not line:
        continue
        
    # ignore headers
    if "Oracle Autonomous Database" in line and "MCQ Question Bank" in line:
        continue
    if "77 Multiple Choice Questions" in line or "Managing and Monitoring" in line:
        continue
    if line in ["Scheduled Maintenance and Patching", "Authentication and Connectivity (mTLS / TLS)", "OCI REST API and CLI", "Network Security (ACL, Private Endpoint, NSG)", "Encryption", "Performance Monitoring", "Oracle Data Safe", "Limits, Quotas, and Compartments", "Predefined Database Services and Wallets", "Wallet Basics and Secure Connectivity", "Autonomous Data Guard", "Managing and Monitoring Autonomous Database (Auto Indexing)"]:
        continue
    if line == "checked":
        continue

    # 1. Question
    m_q = re.match(r'^(\d+)\.\s+(.*)', line)
    if m_q:
        if current_question:
            questions.append(current_question)
        current_question = {
            "text": m_q.group(2),
            "options": [],
            "answer": "",
            "explanation": ""
        }
        continue
        
    if current_question:
        # Option A. Text
        m_opt = re.match(r'^([A-E])\.\s+(.*)', line)
        if m_opt and not current_question.get("answer"):
            expected_opt = chr(ord('A') + len(current_question["options"]))
            if m_opt.group(1) == expected_opt:
                current_question["options"].append({"id": m_opt.group(1), "text": m_opt.group(2)})
                continue
                
        m_ans = re.match(r'^Answer:\s+([A-E])\.', line)
        if not m_ans:
            m_ans = re.match(r'^Answer:\s+([A-E])', line) # fallback
        if m_ans:
            current_question["answer"] = m_ans.group(1)
            continue
            
        m_exp = re.match(r'^Explanation:\s+(.*)', line)
        if m_exp:
            current_question["explanation"] = m_exp.group(1)
            continue
            
        if "Explanation:" not in line and current_question.get("explanation"):
            current_question["explanation"] += " " + line
        elif not current_question["options"]:
            current_question["text"] += " " + line
        elif current_question["options"] and not current_question.get("answer"):
            current_question["options"][-1]["text"] += " " + line

if current_question:
    questions.append(current_question)

valid_questions = [q for q in questions if len(q["options"]) > 0 and q["answer"]]

ts_out = ""
ts_out += '        {\n'
ts_out += '          id: "m1-chapter-4-managing-monitoring",\n'
ts_out += '          title: "Chapter 4: Managing and Monitoring Autonomous Database",\n'
ts_out += '          description: "Managing and Monitoring Autonomous Database MCQ Question Bank",\n'
ts_out += '          questions: [\n'

for q_idx, q in enumerate(valid_questions):
    opts_str = ", ".join([f'{{ id: "{opt["id"]}", text: "{opt["text"].replace("\"", "\\\"")}" }}' for opt in q["options"]])
    ans = q["answer"]
    ts_out += f'            {{ id: {q_idx+1}, question: "{q["text"].replace("\"", "\\\"")}", options: [{opts_str}], correctAnswer: "{ans}", explanation: "{q["explanation"].replace("\"", "\\\"")}" }}'
    if q_idx < len(valid_questions) - 1:
        ts_out += ",\n"
    else:
        ts_out += "\n"

ts_out += "          ]\n"
ts_out += "        }"

with open("chapter4.ts", "w", encoding="utf-8") as f:
    f.write(ts_out)

print(f"Parsed {len(valid_questions)} valid questions out of {len(questions)} total.")
