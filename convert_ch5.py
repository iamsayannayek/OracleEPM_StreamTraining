import json
import re

with open('chapter5_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

questions = []
current_question = None

lines = text.split('\n')
for line in lines:
    line = line.strip()
    if not line:
        continue

    # Question start
    m_q = re.match(r'^(?:Question|Q)(\d+)[:.]\s+(.*)', line)
    if not m_q:
        m_q = re.match(r'^(?:Question|Q)\s*(\d+)[:.]\s+(.*)', line)
    
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
        m_opt = re.match(r'^([A-E])\)\s+(.*)', line)
        if m_opt and not current_question.get("answer"):
            expected_opt = chr(ord('A') + len(current_question["options"]))
            if m_opt.group(1) == expected_opt:
                current_question["options"].append({"id": m_opt.group(1), "text": m_opt.group(2)})
                continue
                
        m_ans = re.match(r'^Correct Answer:\s+([A-E])', line)
        if m_ans:
            current_question["answer"] = m_ans.group(1)
            continue
            
        m_exp = re.match(r'^Explanation:\s+(.*)', line)
        if m_exp:
            current_question["explanation"] = m_exp.group(1)
            continue
            
        if "Explanation:" not in line and current_question.get("explanation"):
            current_question["explanation"] += " " + line
        elif not current_question["options"] and not m_ans and not current_question.get("answer"):
            current_question["text"] += "\n" + line
        elif current_question["options"] and not current_question.get("answer") and not m_ans:
            current_question["options"][-1]["text"] += " " + line

if current_question:
    questions.append(current_question)

valid_questions = [q for q in questions if len(q["options"]) > 0 and q["answer"]]

ts_out = ""
ts_out += '        {\n'
ts_out += '          id: "m1-chapter-5-autonomous-db-tools",\n'
ts_out += '          title: "Chapter 5: Autonomous Database Tools",\n'
ts_out += '          description: "Use Autonomous Database with Oracle APEX and Machine Learning",\n'
ts_out += '          questions: [\n'

for q_idx, q in enumerate(valid_questions):
    opts_str = ", ".join([f'{{ id: "{opt["id"]}", text: "{opt["text"].replace("\"", "\\\"").replace("\n", " ")}" }}' for opt in q["options"]])
    ans = q["answer"]
    q_text = q["text"].replace("\"", "\\\"").replace("\n", " ")
    q_exp = q["explanation"].replace("\"", "\\\"").replace("\n", " ")
    ts_out += f'            {{ id: {q_idx+1}, question: "{q_text}", options: [{opts_str}], correctAnswer: "{ans}", explanation: "{q_exp}" }}'
    if q_idx < len(valid_questions) - 1:
        ts_out += ",\n"
    else:
        ts_out += "\n"

ts_out += "          ]\n"
ts_out += "        }"

with open("chapter5.ts", "w", encoding="utf-8") as f:
    f.write(ts_out)

print(f"Parsed {len(valid_questions)} valid questions out of {len(questions)} total.")
