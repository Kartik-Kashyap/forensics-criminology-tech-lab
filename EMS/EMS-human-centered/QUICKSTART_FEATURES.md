# Forensic Evidence Management System - Quick Start

## 🚀 Installation (Windows)

```cmd
install.bat
```

## 🚀 Installation (Linux/Mac)

```bash
chmod +x install.sh
./install.sh
```

## 🚀 Manual Installation

```bash
pip install streamlit pandas plotly requests cryptography qrcode pillow
```

## ▶️ Run the Application

```bash
streamlit run app.py
```

Browser will open at: http://localhost:8501

## 👤 Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| custodian001 | demo123 | Evidence Custodian (intake, export) |
| analyst001 | demo123 | Forensic Analyst (analysis) |
| sup001 | demo123 | Supervisor (analytics, alerts) |
| inv001 | demo123 | Investigator (basic access) |
| research001 | demo123 | Researcher (analytics only) |

## ✨ Cool Features

### 🔐 Encryption
- AES-256 encryption for any evidence type
- Auto-generated secure passwords
- Bulk encryption support

### 📦 Evidence Packages
- Create password-protected ZIP files
- Include chain of custody automatically
- Download or email directly

### 📧 Email Export
- Send evidence packages via SMTP
- Works with Gmail (use App Password)
- Automatic secure transmission

### 📱 QR Codes
- Generate QR codes for evidence
- Quick access to chain of custody
- Bulk generation available

### 🎯 Timeline Builder
- Create chronological investigation timeline
- Link events to evidence
- Visual timeline graphs

### 🔗 Evidence Relationships
- Map connections between evidence items
- Track references, corroborations, contradictions
- Network visualization

### 💧 Watermarking
- Add forensic watermarks to images
- Timestamp and evidence ID embedded
- Prevents unauthorized distribution

## 🎓 Quick Demo

1. **Login** as `custodian001` / `demo123`
2. **Upload Evidence**: Go to "Evidence Intake" tab
3. **Encrypt**: Go to "Evidence Management" → Click "🔐 Encrypt Evidence"
4. **Timeline**: Go to "Timeline & Relationships" → Build timeline
5. **Bulk Package**: Go to "Bulk Operations" → Select multiple items → Create package
6. **Download**: Click download button to get your encrypted ZIP

## 📧 Gmail Setup (for email features)

1. Enable 2-Step Verification in Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Create App Password for "Mail"
4. Use that password (not your regular password) in the app

## 🐛 Troubleshooting

### Import Error: cryptography
```bash
pip install cryptography
```

### Import Error: qrcode/PIL
```bash
pip install qrcode pillow
```

### Email fails
- Use Gmail App Password, not regular password
- Check SMTP server: smtp.gmail.com
- Port: 587
- Enable less secure app access if needed

### LLM unavailable
Optional feature. Install Ollama for AI explanations:
```bash
# Visit https://ollama.ai/download
ollama pull llama3.2
ollama serve
```

## 🎉 Features Status

When you run the app, check the sidebar for:
- ✅ Green = Feature enabled
- ❌ Red = Missing library (with installation instructions)

## 📚 Documentation

See full documentation in the System Information tab within the app.

## ⚖️ Important

This is an **academic research prototype**. Not for production law enforcement use.

---

**Have fun exploring the forensic evidence management system!** 🔬
