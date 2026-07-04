# -*- coding: utf-8 -*-
import json
import re

log_path = r'C:\Users\HP\.gemini\antigravity-ide\brain\5ea3a05c-58d4-42cc-abf7-6de0cf2584d4\.system_generated\logs\transcript_full.jsonl'
user_inputs = [json.loads(line) for line in open(log_path, encoding='utf-8') if json.loads(line).get('type') == 'USER_INPUT']
pdf_text = user_inputs[-2]['content']

pdf_text = re.sub(r'<USER_REQUEST>|<\/USER_REQUEST>', '', pdf_text)
pdf_text = re.sub(r'==Start of.*?==', '', pdf_text)
pdf_text = re.sub(r'==End of.*?==', '', pdf_text)
pdf_text = re.sub(r'==Screenshot.*?==', '', pdf_text)

questions = []
current_question = None

lines = pdf_text.split('\n')
for line in lines:
    line = line.strip()
    if not line:
        continue
    if "practice questions" in line:
        continue
    
    if line in ['Module intro', 'Create Autonomous Database', 'Serverless Instances - Auto Scaling', 'Serverless Instances - Provision', 'ADB', 'Serverless Instances - Start and', 'Stop ADB', 'Manage users', 'Understand Database', 'Consolidation with Elastic Resource', 'Pools', 'Use Cloning', 'Move Autonomous Database', 'Monitor Autonomous Database', 'instances - events and alarms', 'Manage Autonomous Database', 'Backups and Restores', 'Describe Data gaurd', 'Additional Oracle Exam-Oriented MCQs (Very Likely to Be Asked)', 'Autonomous Database Serverless', '(MCQ Preparation)']:
        continue
    
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
        m_opt = re.match(r'^(?:[^\w\s]?\s*)?([A-E])\.\s+(.*)', line)
        if m_opt:
            current_question["options"].append({"id": m_opt.group(1), "text": m_opt.group(2)})
            continue
        
        m_ans = re.match(r'^Answer:\s+(.*)', line)
        if m_ans:
            current_question["answer"] = m_ans.group(1).replace(" ", "").replace(",", "")
            continue
        
        m_exp = re.match(r'^Explanation:\s+(.*)', line)
        if m_exp:
            current_question["explanation"] = m_exp.group(1)
            continue
            
        if "Explanation:" not in line and current_question.get("explanation"):
            current_question["explanation"] += " " + line
        elif not current_question["options"] and not current_question.get("answer"):
            current_question["text"] += " " + line

if current_question:
    questions.append(current_question)

ts_out = ""
ts_out += '        {\n'
ts_out += '          id: "m1-chapter-2-autonomous-db-serverless",\n'
ts_out += '          title: "Chapter 2: Autonomous Database Serverless",\n'
ts_out += '          description: "Autonomous Database Serverless MCQ Preparation",\n'
ts_out += '          questions: [\n'

for q_idx, q in enumerate(questions):
    opts_str = ", ".join([f'{{ id: "{opt["id"]}", text: "{opt["text"].replace("\"", "\\\"")}" }}' for opt in q["options"]])
    ans = q["answer"]
    ts_out += f'            {{ id: {q_idx+1}, question: "{q["text"].replace("\"", "\\\"")}", options: [{opts_str}], correctAnswer: "{ans}", explanation: "{q["explanation"].replace("\"", "\\\"")}" }}'
    if q_idx < len(questions) - 1:
        ts_out += ",\n"
    else:
        ts_out += "\n"

ts_out += "          ]\n"
ts_out += "        }"

with open("chapter2.ts", "w", encoding="utf-8") as f:
    f.write(ts_out)
print(f"Parsed {len(questions)} questions.")
