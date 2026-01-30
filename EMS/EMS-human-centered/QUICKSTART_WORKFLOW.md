# Quick Start Guide

## Getting Your Forensic Evidence Management System Running in 5 Minutes

---

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] pip package manager (`pip --version`)
- [ ] 2GB free disk space
- [ ] Terminal/command line access

---

## Step-by-Step Setup

### 1. Install Python Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

You should see:
```
Successfully installed streamlit-1.31.0 pandas-2.2.0 plotly-5.18.0 requests-2.31.0
```

### 2. Install Ollama for Local LLM (2 minutes)

**On macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**On Windows:**
1. Download installer from: https://ollama.ai/download
2. Run the installer
3. Open new terminal after installation

**Pull the Llama 3.2 model:**
```bash
ollama pull llama3.2
```

This will download ~2GB. Wait for completion.

### 3. Start Ollama Service (30 seconds)

**In a SEPARATE terminal window**, run:
```bash
ollama serve
```

Keep this terminal open! You should see:
```
Listening on 127.0.0.1:11434
```

### 4. Launch the Application (30 seconds)

**In your ORIGINAL terminal**, run:
```bash
streamlit run app.py
```

The browser will automatically open to: `http://localhost:8501`

---

## First Login

### Choose a Role to Explore

**For Evidence Management:**
- User: `custodian001`
- Password: `demo123`
- Role: Evidence Custodian
- Can: Intake evidence, manage custody chain

**For Investigation:**
- User: `analyst001`  
- Password: `demo123`
- Role: Forensic Analyst
- Can: Analyze evidence, create reports

**For Oversight:**
- User: `sup001`
- Password: `demo123`
- Role: Case Supervisor
- Can: View analytics, review bias indicators

**For Research:**
- User: `research001`
- Password: `demo123`
- Role: Academic Researcher
- Can: Access behavioral analytics

---

## Quick Demo Workflow

### Scenario: Processing Digital Evidence from a Case

**1. Login as Evidence Custodian** (`custodian001`)

**2. Intake Evidence**
   - Go to "Evidence Intake" tab
   - Enter Case ID: `CASE-2026-001`
   - Description: `Suspect's laptop hard drive image`
   - Source: `Search warrant execution - 123 Main St`
   - Upload a file (any image/PDF for demo)
   - Click "Intake Evidence"
   - ✅ Evidence now in system with cryptographic hash

**3. Logout and Login as Forensic Analyst** (`analyst001`)

**4. Examine Evidence**
   - Go to "Evidence Management" tab
   - Select the evidence you just created
   - Click "Create Working Copy"
   - Note: Original remains untouched!

**5. Access the Evidence Multiple Times**
   - View the evidence 6-7 times (simulating repeated examination)
   - This will trigger the confirmation bias indicator

**6. Logout and Login as Supervisor** (`sup001`)

**7. View Behavioral Analytics**
   - Go to "Cognitive Bias Analytics" tab
   - See the "Repeated Access Pattern" alert
   - Notice it's framed as "procedural risk indicator" not "bias accusation"

**8. Generate AI Explanation**
   - Go to "AI Explanations" tab
   - Select "Risk Indicator Explanation"
   - Choose the repeated access alert
   - Click "Explain Indicator"
   - Read the plain-language explanation of what this pattern might mean

**9. View Chain of Custody**
   - Go to "Chain of Custody" tab
   - See complete audit trail of all evidence interactions
   - Click "Generate Court Report" to see AI-generated summary
   - Verify chain integrity shows ✅ Valid

---

## Exploring Different Features

### Evidence Intake (Custodian Only)
- Upload various file types: JPG, PNG, PDF, MP4
- Each gets unique evidence ID
- SHA-256 hash computed automatically
- Original stored immutably

### Chain of Custody (All Roles Can View)
- Every interaction logged
- Cryptographic hash chaining
- Tamper detection
- Court-readable summaries

### Bias Analytics (Supervisor & Researcher)
- Repeated access patterns
- Early export detection
- Role-action mismatches
- Temporal analysis

### AI Explanations (All Roles)
- Chain of custody summaries
- Risk indicator explanations
- Procedural clarifications
- Research-backed insights

---

## Understanding the Roles

### 🔍 Field Investigator
**What they do**: Collect evidence, take notes
**What they can't do**: Manage custody, export evidence
**Why**: Prevents conflicts of interest

### 🧪 Forensic Analyst
**What they do**: Detailed analysis, create reports
**What they can't do**: Intake evidence, manage custody
**Why**: Maintains objectivity and independence

### 📦 Evidence Custodian
**What they do**: Intake, storage, custody management
**What they can't do**: Analyze evidence, investigate
**Why**: Ensures neutral handling

### 👔 Case Supervisor  
**What they do**: Oversight, review alerts, approve exports
**What they can't do**: Direct analysis, handle evidence
**Why**: Independent quality control

### 📊 Academic Researcher
**What they do**: View analytics, study patterns
**What they can't do**: Access individual evidence
**Why**: Privacy protection, research independence

---

## Common Tasks

### How to Intake Evidence
1. Login as `custodian001`
2. Evidence Intake tab
3. Fill all fields
4. Upload file
5. Click "Intake Evidence"

### How to Create Working Copy
1. Login as analyst or investigator
2. Evidence Management tab
3. Select evidence
4. Click "Create Working Copy"

### How to View Bias Indicators
1. Login as supervisor
2. Cognitive Bias Analytics tab
3. View summary metrics
4. Expand individual indicators

### How to Generate Court Report
1. Go to Chain of Custody tab
2. Select specific evidence
3. Click "Generate Court Report"
4. Wait for AI summary

### How to Export Evidence
1. Login as custodian
2. Evidence Management tab
3. Select evidence
4. Click "Export"
5. (Demo shows placeholder)

---

## Troubleshooting

### "LLM unavailable" Error
**Problem**: Ollama not running
**Solution**: 
```bash
# In separate terminal
ollama serve
```

### "Access Denied" Messages
**Problem**: Current role lacks permission
**Solution**: This is intentional! Shows RBAC working. Try different role.

### Evidence Upload Fails
**Problem**: File type not supported
**Solution**: Use JPG, PNG, PDF, MP4, WAV, DD, or IMG files

### Port Already in Use
**Problem**: Another app using port 8501
**Solution**:
```bash
streamlit run app.py --server.port 8502
```

### Cannot See Evidence Files
**Problem**: Looking in wrong directory
**Solution**: Evidence in `/home/claude/forensic_ems/evidence_vault/`

---

## System Architecture Quick Reference

```
Evidence Flow:
1. Upload (Custodian) → Original Storage (read-only)
2. Hash Computation → SHA-256 recorded
3. Custody Chain Entry → Cryptographically linked
4. Working Copy Created (Analyst) → Separate file
5. Analysis Performed → Working copy only
6. Export (Custodian + Supervisor approval) → Court copy

Access Control Flow:
User → Role → Permissions → Action
        ↓
     Logged (if allowed)
     Denied (if not allowed)
        ↓
     Analytics
```

---

## What to Explore

### For Forensic Science Students
- How chain of custody works
- Evidence integrity preservation
- Proper handling procedures

### For Psychology Students  
- Cognitive bias detection mechanisms
- Behavioral pattern analysis
- Non-accusatory feedback design

### For Computer Science Students
- Cryptographic hashing
- RBAC implementation
- LLM integration
- Data structures

### For Criminal Justice Students
- Procedural justice principles
- Separation of duties
- Legal admissibility requirements

### For Researchers
- Behavioral analytics
- Research design possibilities
- Ethical AI integration

---

## Next Steps

After trying the basic workflow:

1. **Read [DESIGN_RATIONALE.md](DESIGN_RATIONALE.md)** to understand the psychology
2. **Experiment with different roles** to see RBAC in action
3. **Try to trigger different bias indicators** 
4. **Generate AI explanations** for various scenarios
5. **Review the code** with inline comments explaining research basis

---

## Getting Help

### In the Application
- Click on "System Information" tab for overview
- Each tab has info boxes explaining features
- Alerts include explanations and recommendations

### In Documentation
- `README.md` - Complete system overview
- `DESIGN_RATIONALE.md` - Psychological principles
- `app.py` - Heavily commented code

### Common Questions

**Q: Can I use real case data?**  
A: NO! This is a research prototype only. Use dummy data.

**Q: Is this suitable for actual investigations?**  
A: NO! Academic research only, not production-ready.

**Q: Can I modify the code?**  
A: Yes! All code is provided for educational purposes.

**Q: Where is evidence stored?**  
A: `evidence_vault/`

**Q: How do I reset the system?**  
A: Stop the app, delete `evidence_vault/`, restart.

---

## Quick Reference Card

| Task | User | Tab | Action |
|------|------|-----|--------|
| Add evidence | custodian001 | Evidence Intake | Upload file |
| Analyze evidence | analyst001 | Evidence Management | Create working copy |
| View patterns | sup001 | Cognitive Bias Analytics | Review indicators |
| See chain | Any user | Chain of Custody | Select evidence |
| Get explanation | Any user | AI Explanations | Choose type |

---

**You're ready to go! Login and explore the system.**

**Remember**: This is for research and education, not real investigations.

---

Last Updated: January 2026
