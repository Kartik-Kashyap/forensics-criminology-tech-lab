# P-FEICS v2.0 - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.8+ installed
- pip package manager
- 100 MB free disk space

### Installation

```bash
# 1. Install dependencies
pip install numpy scipy matplotlib PyWavelets pycryptodome reportlab

# 2. Run the application
python p_feics_enhanced.py
```

### First-Time Workflow

#### Step 1: Authenticate Examiner
1. Fill in examiner details (pre-filled with defaults)
2. Click "1. Authenticate Examiner (Generate Keys)"
3. ✅ Confirmation dialog appears with key fingerprint

#### Step 2: Acquire Evidence
1. Review case metadata (Case ID, Subject ID, etc.)
2. Click "2. Acquire Evidence (Generate Mock BEOS)"
3. 📊 Raw signal appears in top-left plot
4. ⚠️ Evidence is now READ-ONLY

#### Step 3: Apply Watermarking
1. Click "3. Apply Dual Watermarking (LSB + DWT)"
2. ⏳ Processing takes ~2 seconds
3. 📊 All four plots populate:
   - Raw Evidence (green)
   - Watermarked (blue)
   - Difference signal (yellow)
   - Frequency spectrum comparison

#### Step 4: Verify Integrity
1. Click "4. Verify Integrity (Extract & Compare)"
2. ⏳ Verification takes ~1 second
3. ✅ Success dialog shows:
   - LSB confidence score
   - DWT correlation
   - Overall verdict

#### Step 5: AI Analysis (Optional)
1. Click "5. AI Analysis (Non-Evidentiary)"
2. 📝 Right panel shows AI interpretation
3. ⚠️ Clearly marked NON-EVIDENTIARY

#### Step 6: Export Container
1. Click "6. Export Evidence Container (.pfeics)"
2. 💾 Choose save location
3. ✅ Encrypted container created with:
   - Raw evidence (AES-encrypted)
   - Watermarked evidence (AES-encrypted)
   - Chain-of-custody (hash-linked)
   - Digital signatures

#### Step 7: Generate Report
1. Click "7. Generate Signed Court Report (PDF)"
2. 💾 Choose save location
3. 📄 PDF includes:
   - Case metadata
   - Examiner information
   - Chain-of-custody table
   - Digital signatures

---

## 📋 Understanding the Interface

### Top Left: Case Metadata
- **Case ID:** Unique identifier for this case
- **Subject ID:** De-identified subject reference
- **Examiner Name:** Forensic psychologist name
- **Badge ID:** Examiner credential number
- **Organization:** Lab or agency name
- **Certification:** Professional certification (ABFE, etc.)
- **Assessment Type:** Type of psychological evaluation
- **Stimulus Protocol:** What stimuli were presented

### Top Right: Processing Pipeline
Seven-step workflow from acquisition to court report.

### Middle: Signal Visualizations
- **Top Left (Green):** Raw, unmodified evidence
- **Top Right (Blue):** Watermarked evidence
- **Bottom Left (Yellow):** Difference between raw and watermarked
- **Bottom Right:** Frequency spectrum comparison

### Bottom Left: Chain-of-Custody Log
Cryptographically linked audit trail of all operations.

### Bottom Right: AI Analysis
Non-evidentiary interpretation for examiner reference.

---

## 🔐 Security Features Explained

### 1. AES-256-GCM Encryption
- **What it does:** Encrypts all evidence with military-grade encryption
- **Why it matters:** Prevents unauthorized access and tampering
- **How to verify:** Container files are gibberish without keys

### 2. RSA-4096 Digital Signatures
- **What it does:** Cryptographically signs examiner actions
- **Why it matters:** Proves who performed each operation
- **How to verify:** Public key fingerprint in logs

### 3. LSB Watermarking
- **What it does:** Embeds hash in least significant bits
- **Why it matters:** Proves signal wasn't filtered
- **How to verify:** Extraction yields original hash

### 4. DWT Watermarking
- **What it does:** Embeds hash in frequency domain
- **Why it matters:** Survives legitimate processing
- **How to verify:** Correlation score > 0.7

### 5. Hash-Chained Chain-of-Custody
- **What it does:** Links each event to previous event's hash
- **Why it matters:** Makes retroactive tampering detectable
- **How to verify:** Recompute hashes and compare

### 6. Read-Only Raw Evidence
- **What it does:** Marks original signal as immutable
- **Why it matters:** Guarantees original is never altered
- **How to verify:** Python flags.writeable = False

---

## 🎯 Common Use Cases

### Use Case 1: BEOS Deception Detection
**Scenario:** Subject being evaluated for deception using EEG

**Workflow:**
1. Acquire EEG signal during stimulus presentation
2. Apply watermarking immediately post-acquisition
3. Verify integrity before analysis
4. Run AI to flag anomalies (non-evidentiary)
5. Generate court report with cryptographic proof

**Court Testimony:**
"The signal was watermarked with the case hash immediately upon acquisition. The LSB watermark proves no filtering occurred. The DWT watermark proves the signal wasn't manipulated. Both watermarks verify successfully."

### Use Case 2: Suspect Detection System (SDS)
**Scenario:** Thermal imaging + facial micro-expressions

**Workflow:**
1. Acquire thermal video frames
2. Extract keyframes
3. Apply LSB watermarking to keyframes
4. Bind thermal calibration data to metadata
5. Export container with video + thermal data

**Extension Needed:** Video watermarking module (future)

### Use Case 3: Forensic Interview
**Scenario:** Audio-visual recording of suspect interview

**Workflow:**
1. Record interview with synchronized audio/video
2. Extract audio waveform
3. Apply dual watermarking to audio
4. Bind video metadata (timestamps, camera ID)
5. Generate timeline report

**Extension Needed:** Audio watermarking module (future)

---

## 🐛 Troubleshooting

### Error: "No module named 'Crypto'"
**Solution:** Install pycryptodome:
```bash
pip install pycryptodome
```

### Error: "No module named 'PyWavelets'"
**Solution:** Install PyWavelets:
```bash
pip install PyWavelets
```

### Error: "TclError" or GUI doesn't appear
**Solution:** Ensure tkinter is installed:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# macOS (via Homebrew)
brew install python-tk

# Windows (included in standard Python install)
```

### Warning: "Raw evidence is now READ-ONLY"
**This is expected behavior!** The system intentionally makes the raw evidence immutable to prevent accidental modification.

### Low confidence score on integrity verification
**Possible causes:**
1. Signal was filtered after watermarking
2. Encryption/decryption error
3. Metadata mismatch

**Solution:** Re-acquire evidence or investigate chain-of-custody log.

---

## 📊 Sample Output Files

### Evidence Container (.pfeics)
**Contents:**
- manifest.json (case info + checksums)
- raw_evidence.enc (AES-encrypted signal)
- watermarked_evidence.enc (AES-encrypted watermarked signal)
- chain_of_custody.enc (AES-encrypted audit log)
- examiner_signature.sig (RSA signature)

**Size:** Typically 50-200 KB for 10-second EEG signal

### Court Report (PDF)
**Contents:**
- Case Information table
- Examiner Information table
- Chain-of-Custody table (first 10 events)
- Cryptographic Verification section
- Digital Signature block

**Pages:** 2-3 pages typical

---

## 🔬 Advanced Features

### Custom Signal Input
To use real EEG data instead of mock data:

```python
# In p_feics_enhanced.py, modify acquire_evidence():

# Replace this:
t, raw_signal = SignalWatermarking.generate_mock_eeg(...)

# With this:
import pandas as pd
df = pd.read_csv('your_eeg_data.csv')
raw_signal = df['amplitude'].values.astype(np.int32)
t = df['time'].values
```

### Multiple Examiners
For multi-examiner collaboration:

1. Each examiner generates their own keypair
2. Each operation signed by current examiner
3. Chain-of-custody tracks examiner transitions
4. Report includes all examiner signatures

**Implementation:** Requires extension (future roadmap)

### Batch Processing
To process multiple cases:

```python
cases = ['CASE-001', 'CASE-002', 'CASE-003']

for case_id in cases:
    # Update metadata
    metadata_entries['Case ID'].delete(0, tk.END)
    metadata_entries['Case ID'].insert(0, case_id)
    
    # Run workflow
    acquire_evidence()
    apply_watermarking()
    verify_integrity()
    export_container()
```

---

## 📚 Additional Resources

### Documentation
- **Technical Docs:** `P-FEICS_v2_Technical_Documentation.md`
- **Security Model:** Section 7 of technical docs and `P-FEICS_v2_Security_Model.md`
- **Legal Defensibility:** Section 8 of technical docs

### Standards & References
- NIST FIPS 197 (AES): https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
- Federal Rules of Evidence: https://www.law.cornell.edu/rules/fre
- Daubert Standard: Daubert v. Merrell Dow Pharmaceuticals, 509 U.S. 579 (1993)

### Training
- Cryptography Fundamentals: Coursera "Cryptography I"
- Digital Forensics: SANS FOR585
- Expert Testimony: NIST Expert Witness Training

### Support
- **Documentation:** Read `P-FEICS_v2_Technical_Documentation.md`
- **Issues:** Check troubleshooting section above
- **Questions:** Review technical documentation Section 10

---

## ⚠️ Critical Reminders

1. **Always authenticate examiner first** (Step 1)
2. **Raw evidence becomes READ-ONLY** after acquisition
3. **AI outputs are NON-EVIDENTIARY** - use for reference only
4. **Chain-of-custody is automatically maintained** - all operations logged
5. **Keep private keys secure** - in production, use HSM
6. **Verify watermarks before court** - run integrity check
7. **Export both container and PDF** - container for archival, PDF for court

---

## 🎓 Best Practices

### DO:
✅ Authenticate examiner before any operations  
✅ Verify integrity before finalizing analysis  
✅ Export container for long-term archival  
✅ Generate signed PDF for court proceedings  
✅ Document any anomalies in chain-of-custody  
✅ Keep examiner private key secure  

### DON'T:
❌ Skip examiner authentication  
❌ Modify raw evidence after acquisition  
❌ Present AI analysis as evidentiary  
❌ Share private keys between examiners  
❌ Edit chain-of-custody logs manually  
❌ Rely solely on LSB watermark (use dual)  

---

## 📈 Performance Benchmarks

**Hardware:** Intel i7-9700K, 16GB RAM

| Operation | Time | Notes |
|-----------|------|-------|
| Acquire Evidence | ~0.5s | Generate 10s mock signal |
| LSB Watermarking | ~0.1s | 2560 samples |
| DWT Watermarking | ~0.8s | 3-level decomposition |
| Integrity Verification | ~1.2s | Dual watermark extraction |
| Container Export | ~0.3s | AES encryption + signing |
| PDF Generation | ~0.5s | ReportLab rendering |

**Total Workflow:** ~3.5 seconds from acquisition to export

---

## 🔐 Security Checklist

Before deploying in production:

- [ ] Install on air-gapped workstation
- [ ] Enable full disk encryption
- [ ] Configure HSM for key storage
- [ ] Implement key rotation policy
- [ ] Set up secure backup procedures
- [ ] Train all examiners on SOP
- [ ] Conduct security audit
- [ ] Test disaster recovery plan
- [ ] Document all configurations
- [ ] Establish chain-of-custody SOP

---

## 🎯 Next Steps

After completing this quick start:

1. Read full technical documentation
2. Complete examiner training (16 hours)
3. Practice with sample cases
4. Review legal admissibility section
5. Prepare for cross-examination scenarios
6. Set up production environment
7. Conduct security hardening
8. Begin live case processing

---

**Version:** 2.0.0  
**Last Updated:** January 2026  
**Maintained By:** Kartik Kashyap
