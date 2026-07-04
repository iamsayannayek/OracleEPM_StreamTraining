# -*- coding: utf-8 -*-
import json
import re

log_path = r'C:\Users\HP\.gemini\antigravity-ide\brain\5ea3a05c-58d4-42cc-abf7-6de0cf2584d4\.system_generated\logs\transcript_full.jsonl'
user_inputs = [json.loads(line) for line in open(log_path, encoding='utf-8') if json.loads(line).get('type') == 'USER_INPUT']
last_input = user_inputs[-1]['content']

last_input = re.sub(r'<USER_REQUEST>|<\/USER_REQUEST>', '', last_input).strip()

chapters = []
current_chapter = None
current_question = None

lines = last_input.split('\n')
for i, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue
    
    if re.match(r'^Module 1', line):
        continue
    if re.match(r'^(Chapter 2: |Understand |Use |Move |Monitor |Manage |Describe ).*', line):
        title = line
        if title.startswith("Chapter 2: "):
            title = title
        elif not title.startswith("Chapter "):
            title = "Chapter: " + title
        
        current_chapter = {
            "title": title,
            "questions": []
        }
        chapters.append(current_chapter)
        current_question = None
        continue
    
    m_q = re.match(r'^(\d+)\.\s+(.*)', line)
    if m_q and current_chapter is not None:
        if current_question:
            current_chapter["questions"].append(current_question)
        current_question = {
            "text": m_q.group(2),
            "options": [],
            "answer": "",
            "explanation": ""
        }
        continue
    
    if current_question:
        m_chk = re.match(r'^?\s*([A-E])\.\s+(.*)', line)
        if m_chk:
            current_question["options"].append({"id": m_chk.group(1), "text": m_chk.group(2)})
            continue
        
        m_opt = re.match(r'^([A-E])\.\s+(.*)', line)
        if m_opt:
            current_question["options"].append({"id": m_opt.group(1), "text": m_opt.group(2)})
            continue
        
        m_ans = re.match(r'^Answer:\s+(.*)', line)
        if m_ans:
            current_question["answer"] = m_ans.group(1).replace(" ", "")
            continue
        
        m_exp = re.match(r'^Explanation:\s+(.*)', line)
        if m_exp:
            current_question["explanation"] = m_exp.group(1)
            continue
        
        if "Explanation:" not in line and current_question["explanation"]:
            if "practice questions" not in line and "----" not in line and not line.startswith("Additional Oracle") and "This is the whole pdf" not in line:
                current_question["explanation"] += " " + line
        elif not current_question["options"] and not current_question["answer"]:
            if "practice questions" not in line and "----" not in line and not line.startswith("Additional Oracle") and "This is the whole pdf" not in line:
                current_question["text"] += " " + line
        
if current_question and current_chapter:
    current_chapter["questions"].append(current_question)

ts_out = ""
for i, ch in enumerate(chapters):
    ch_id = f"m1-chapter-{2+i}-" + re.sub(r'[^a-z0-9]', '-', ch['title'].lower()[:20]).strip('-')
    ts_out += "        {\n"
    ts_out += f'          id: "{ch_id}",\n'
    ts_out += f'          title: "{ch["title"].replace("Chapter: Chapter 2: ", "Chapter 2: ")}",\n'
    ts_out += f'          description: "{ch["title"].replace("Chapter: Chapter 2: ", "Chapter 2: ")}",\n'
    ts_out += '          questions: [\n'
    
    for q_idx, q in enumerate(ch["questions"]):
        opts_str = ", ".join([f'{{ id: "{opt["id"]}", text: "{opt["text"].replace("\"", "\\\"")}" }}' for opt in q["options"]])
        ans = q["answer"]
        ts_out += f'            {{ id: {q_idx+1}, question: "{q["text"].replace("\"", "\\\"")}", options: [{opts_str}], correctAnswer: "{ans}", explanation: "{q["explanation"].replace("\"", "\\\"")}" }}'
        if q_idx < len(ch["questions"]) - 1:
            ts_out += ",\n"
        else:
            ts_out += "\n"
    
    ts_out += "          ]\n"
    ts_out += "        }"
    if i < len(chapters) - 1:
        ts_out += ",\n"

with open("new_chapters.ts", "w", encoding="utf-8") as f:
    f.write(ts_out)
print(f"Generated {len(chapters)} chapters with {sum(len(c['questions']) for c in chapters)} questions.")
