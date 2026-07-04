# -*- coding: utf-8 -*-
import json
import re

log_path = r'C:\Users\HP\.gemini\antigravity-ide\brain\5ea3a05c-58d4-42cc-abf7-6de0cf2584d4\.system_generated\logs\transcript_full.jsonl'
lines = [json.loads(line) for line in open(log_path, encoding='utf-8') if '==Start of PDF==' in line]
pdf_text = lines[-1]['content']

pdf_text = re.sub(r'<USER_REQUEST>|<\/USER_REQUEST>', '', pdf_text)
pdf_text = re.sub(r'<ADDITIONAL_METADATA>.*?<\/ADDITIONAL_METADATA>', '', pdf_text, flags=re.DOTALL)
pdf_text = re.sub(r'==Start of.*?==', '', pdf_text)
pdf_text = re.sub(r'==End of.*?==', '', pdf_text)
pdf_text = re.sub(r'==Screenshot.*?==', '', pdf_text)

questions = []
current_question = None

lines_text = pdf_text.split('\n')
for line in lines_text:
    line = line.strip()
    if not line:
        continue
    
    if "Oracle Autonomous Database Dedicated" in line and "Practice Questions" in line:
        continue
    if "file:///" in line or "7/3/26" in line:
        continue
    if "Table of Contents" in line or "Six comprehensive topic areas" in line:
        continue
    if line.endswith("Qs") and bool(re.search(r'\d+', line)):
        continue
    
    if line.startswith("TO P I C") or line.startswith("Basic Level") or line.startswith("Intermediate Level") or line.startswith("Certification / Scenario Level"):
        continue
        
    if "Questions " in line:
        continue
        
    if line.startswith("ADB Dedicated") or line.startswith("Workflows & Functionality"):
        continue
    
    m_q = re.match(r'^(\d+)\s+(.*)', line)
    if m_q and len(m_q.group(2)) > 5 and not "Topics " in line:
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
        m_opt = re.match(r'^([A-E])\s+(.*)', line)
        if m_opt and len(line) > 2 and not current_question.get("explanation"):
            opt_text = m_opt.group(2)
            is_correct = False
            if '\u2713' in opt_text:
                opt_text = opt_text.replace('\u2713', '').strip()
                is_correct = True
            
            expected_opt = chr(ord('A') + len(current_question["options"]))
            if m_opt.group(1) == expected_opt:
                current_question["options"].append({"id": m_opt.group(1), "text": opt_text})
                if is_correct:
                    current_question["answer"] = m_opt.group(1)
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
ts_out += '          id: "m1-chapter-3-autonomous-db-dedicated",\n'
ts_out += '          title: "Chapter 3: Oracle Autonomous Database Dedicated",\n'
ts_out += '          description: "Comprehensive Practice Questions & Answers",\n'
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

with open("chapter3.ts", "w", encoding="utf-8") as f:
    f.write(ts_out)
print(f"Parsed {len(valid_questions)} valid questions out of {len(questions)} total.")
