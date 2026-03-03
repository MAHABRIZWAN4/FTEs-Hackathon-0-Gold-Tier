# 🚀 Silver Tier AI Employee - Quick Reference Card

## ⚡ Daily Use Commands

### Test Colorful UI (Recommended First!)
```bash
python test_ui.py
```
**Output:** Beautiful colorful demo of all features

---

### Start Gmail Watcher
```bash
python scripts/watch_gmail.py
```
**What it does:**
- Monitors Gmail every 60 seconds
- Auto-replies to emails
- Saves emails to vault
- Colorful output: ⚡ EXEC, ✅ DONE, 🚫 FAIL

---

### Start Vault Watcher
```bash
python scripts/watch_inbox.py
```
**What it does:**
- Monitors Inbox folder every 15 seconds
- Triggers Task Planner automatically
- Colorful output with panels

---

### Run Task Planner (Manual)
```bash
python scripts/task_planner.py
```
**What it does:**
- Processes all .md files in Inbox
- Creates plans in Needs_Action
- Beautiful statistics table

---

### Run Full System (Scheduler)
```bash
# Single run
python scripts/run_ai_employee.py --once

# Continuous (daemon mode)
python scripts/run_ai_employee.py
```

---

## 📧 Gmail Setup (One-Time)

1. **Get Gmail App Password:**
   - Visit: https://myaccount.google.com/apppasswords
   - Generate password for "Mail"
   - Copy 16-character password

2. **Edit .env file:**
   ```
   EMAIL_ADDRESS=your.email@gmail.com
   EMAIL_PASSWORD=your_16_char_app_password
   ```

3. **Test connection:**
   ```bash
   python scripts/watch_gmail.py
   ```

---

## 🎯 Typical Workflow

### Option 1: Email-to-Task Pipeline
```bash
# Terminal 1: Start Gmail Watcher
python scripts/watch_gmail.py

# Terminal 2: Start Vault Watcher
python scripts/watch_inbox.py

# Now send yourself an email and watch the magic!
```

### Option 2: Manual Task Processing
```bash
# Create task file
echo "# Fix Bug
Priority: high
Description here" > AI_Employee_Vault/Inbox/task.md

# Process it
python scripts/task_planner.py

# Check result
ls AI_Employee_Vault/Needs_Action/
```

---

## 📊 Check Status

### View Logs (Real-time)
```bash
tail -f logs/actions.log
```

### View Logs (Last 50 lines)
```bash
tail -n 50 logs/actions.log
```

### Check Processed Files
```bash
cat logs/processed.json
```

### Check Inbox
```bash
ls AI_Employee_Vault/Inbox/
```

### Check Plans
```bash
ls AI_Employee_Vault/Needs_Action/
```

---

## 🎨 Status Icons Reference

- **⚡ EXEC:** Execution/Info (Cyan)
- **✅ DONE:** Success (Green)
- **🚫 FAIL:** Error (Red)
- **🔍 SCAN:** Warning/Scanning (Yellow)
- **💓 Heartbeat:** Status update (Cyan)

---

## 🛠️ Troubleshooting

### Gmail Not Connecting
```bash
# Check credentials
cat .env | grep EMAIL

# Test connection
python -c "import imaplib; mail = imaplib.IMAP4_SSL('imap.gmail.com'); print('OK')"
```

### No Colorful Output
```bash
# Install rich library
pip install rich
```

### Task Not Processing
```bash
# Check if file is .md
ls AI_Employee_Vault/Inbox/*.md

# Check processed registry
cat logs/processed.json
```

---

## 📁 Important Folders

- **Inbox/** - Drop new tasks here
- **Needs_Action/** - Generated plans appear here
- **Needs_Approval/** - Approval requests
- **Done/** - Completed tasks
- **logs/** - All activity logs

---

## 🔥 Pro Tips

1. **Always test UI first:** `python test_ui.py`
2. **Use 2 terminals:** Gmail Watcher + Vault Watcher
3. **Monitor logs:** `tail -f logs/actions.log`
4. **Check heartbeat:** Look for 💓 messages
5. **Gmail App Password:** Never use regular password

---

## 🎊 Quick Test Sequence

```bash
# 1. Test UI
python test_ui.py

# 2. Create test task
echo "# Test Task" > AI_Employee_Vault/Inbox/test.md

# 3. Process it
python scripts/task_planner.py

# 4. Check result
cat AI_Employee_Vault/Needs_Action/Plan_test.md
```

---

## 📞 Need Help?

- **Documentation:** README.md
- **Testing Guide:** TESTING_GUIDE.md
- **Project Status:** COMPLETE_PROJECT_STATUS.md
- **Logs:** logs/actions.log

---

**🎉 Your Silver Tier AI Employee is ready to work 24/7!**

**Status:** PRODUCTION READY ✅
**Version:** 1.0.0
**Last Updated:** March 3, 2026
