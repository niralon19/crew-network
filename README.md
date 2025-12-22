# noc_crewai — סוכן/צוות תפעול ובקרה עם CrewAI + זיכרון SQLite + פתיחת Jira

## מה הפרויקט עושה
הפרויקט מקבל **Alert מובנה** (למשל מ־Grafana), מנתב אותו לסוכן דומיין מתאים (הרמטיות / צימודים / COATR),
מריץ חקירה בעזרת Tools פנימיים, מסכם למסקנות אופרטיביות (Root Cause + פעולות למניעת הישנות),
ומבצע **Dedup** בעזרת **זיכרון SQLite** כדי שלא יקרה טיפול כפול / פתיחת טיקטים כפולה ב־Jira.

### עקרונות תפעוליים
- Routing/Policy/Dedup הם **דטרמיניסטיים** (ללא LLM).
- ה־LLM משמש רק ל:
  1) החלטה אילו בדיקות להריץ (Tool-calling) בתוך סוכן הדומיין
  2) סינתזה והסקת מסקנות בשכבת Conclusion
- פעולות Side-effect (Jira) מתבצעות רק ע״י קוד רגיל אחרי Policy.

## זרימת עבודה (High-level)
1. `handle_alert(alert)` נקראת עם Alert מובנה.
2. `router.route_alert(alert)` קובעת דומיין (traffic/coupling/coatr).
3. `domain_runner.run_domain_investigation(alert, route)` מפיקה Findings + Evidence.
4. `conclusion.conclude(alert, findings, evidence)` מחזירה JSON מסקנות אחיד.
5. `memory.dedup.process_conclusion_with_memory(...)` בודקת SQLite:
   - אם Duplicate: לא פותחים טיקט חדש, אפשר להוסיף Comment (מוגדר כהרחבה).
   - אם חדש: `jira.publisher.publish_to_jira(...)` פותח Issue, ושומרים Incident בזיכרון.

## מבנה תיקיות
- `noc_crewai/models.py` — סכמות Alert / Findings / Conclusion
- `noc_crewai/router.py` — ניתוב דטרמיניסטי
- `noc_crewai/agents.py` — הגדרת Agents (3 דומיינים + Conclusion)
- `noc_crewai/tasks.py` — Tasks (דומיינים + Conclusion)
- `noc_crewai/domain_runner.py` — הרצה ממוקדת לסוכן הנכון
- `noc_crewai/conclusion.py` — שכבת סיכום (LLM) → JSON אחיד
- `noc_crewai/policy.py` — Guardrails לפתיחת Jira
- `noc_crewai/jira/*` — Client + Formatter + Publisher
- `noc_crewai/memory/*` — SQLite incident memory + TTL + fingerprint + dedup
- `noc_crewai/tools/*` — Tools פנימיים (stubs; מחליפים ל־real impl אצלך)
- `tests/` — Pytest לכל ה-flow (מוקים ל-LLM/Jira/Tools)

## התקנה והרצה
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ערוך .env
python -m noc_crewai.main
```

### הרצה עם Alert לדוגמה
`noc_crewai/main.py` כולל דוגמה — בפרודקשן תחליף את `sample_alert()` בקליטה אמיתית מ־Grafana.

## בדיקות
```bash
pytest -q
```

## נקודות פרודקשן שחייבים להכיר
- SQLite הוא קובץ: אם אתה מריץ ReplicaSet עם כמה פודים — תצטרך Shared PVC או לעבור ל-Redis/Postgres.
- Dedup עובד לפי fingerprint = (service, alert_type, normalized_root_cause). לכן normalization חייב להיות עקבי.
- Jira Token/Email: מומלץ להשתמש ב-Secret Manager ולא .env.

## הרחבות מומלצות (לא חובה)
- Comment אוטומטי ל-Jira במצב Duplicate
- Correlation בין שירותים (multi-service incidents)
- Auto-close incident אחרי X שעות שקט + TTL cleanup
