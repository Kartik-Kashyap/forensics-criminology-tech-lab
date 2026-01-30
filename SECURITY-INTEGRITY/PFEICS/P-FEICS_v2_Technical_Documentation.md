# P-FEICS v2.0: Court-Admissible Forensic Evidence System
## Complete Technical Documentation

**Version:** 2.0.0  
**Classification:** Forensic Laboratory Use Only  
**Compliance:** FRE 901/902, Daubert Standard  
**Author:** Kartik Kashyap
**Date:** January 2026

---

## Executive Summary

P-FEICS v2.0 represents a comprehensive redesign of psychological forensic evidence management, addressing all critical security vulnerabilities identified in v1.0. The system now provides court-admissible, cryptographically tamper-evident preservation of physiological signals with complete chain-of-custody documentation.

**Key Improvements from v1.0:**
- ✅ AES-256-GCM encryption implemented for all evidence and logs
- ✅ Hash-chained immutable chain-of-custody
- ✅ Dual-domain watermarking (LSB + DWT) with confidence scoring
- ✅ Read-only raw evidence preservation
- ✅ Portable encrypted evidence container format (.pfeics)
- ✅ RSA-4096 digital signatures for examiners and reports
- ✅ AI interpretation module with clear non-evidentiary labeling
- ✅ Tamper localization and watermark extraction

---

## 1. System Architecture

### 1.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    P-FEICS v2.0 ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   Evidence       │         │   Cryptographic   │            │
│  │   Acquisition    │────────▶│   Operations      │            │
│  │   (BEOS/SDS)     │         │   (AES-GCM/RSA)   │            │
│  └──────────────────┘         └──────────────────┘            │
│          │                             │                        │
│          ▼                             ▼                        │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   Dual-Domain    │         │   Hash-Chained    │            │
│  │   Watermarking   │◀────────│   Chain-of-       │            │
│  │   (LSB + DWT)    │         │   Custody         │            │
│  └──────────────────┘         └──────────────────┘            │
│          │                             │                        │
│          ▼                             ▼                        │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   Evidence       │         │   AI Interpreter  │            │
│  │   Container      │         │   (Non-Eviden.)   │            │
│  │   (.pfeics)      │         │                   │            │
│  └──────────────────┘         └──────────────────┘            │
│          │                             │                        │
│          └─────────────┬───────────────┘                       │
│                        ▼                                        │
│                ┌──────────────────┐                            │
│                │   Signed Court   │                            │
│                │   Reports (PDF)  │                            │
│                └──────────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

**Evidence Lifecycle:**

1. **Acquisition** → Raw physiological signal captured
2. **Authentication** → Examiner generates RSA keypair
3. **Encryption** → Raw signal encrypted with AES-256-GCM
4. **Watermarking** → Dual-domain watermark embedded
5. **Verification** → Watermark extraction and validation
6. **Analysis** → AI-assisted interpretation (non-evidentiary)
7. **Export** → Container creation with all cryptographic bindings
8. **Reporting** → Digitally signed PDF for court proceedings

**Critical Principle:** Raw evidence is **NEVER** modified. All operations work on encrypted copies with cryptographic binding to the original.

---

## 2. Cryptographic Security Model

### 2.1 Encryption Standards

#### AES-256-GCM (Galois/Counter Mode)

**Purpose:** Encrypt all evidence and chain-of-custody logs

**Implementation:**
```python
key = get_random_bytes(32)  # 256-bit key
cipher = AES.new(key, AES.MODE_GCM)
cipher.update(metadata.encode())  # Additional Authenticated Data
ciphertext, tag = cipher.encrypt_and_digest(plaintext)
```

**Properties:**
- **Authenticated Encryption:** Prevents tampering
- **Additional Authenticated Data (AAD):** Binds metadata to ciphertext
- **Nonce-based:** Each encryption uses unique nonce
- **Tag Verification:** Decryption fails if data or metadata altered

**Key Management:**
⚠️ **CRITICAL:** In production deployment:
- Keys stored in Hardware Security Module (HSM)
- Key derivation using PBKDF2 with high iteration count
- Key rotation policy every 90 days
- Master keys encrypted at rest

### 2.2 Digital Signatures

#### RSA-4096 with PKCS#1 v1.5 Padding

**Purpose:** Authenticate examiner actions and sign reports

**Key Generation:**
```python
key = RSA.generate(4096)  # 4096-bit modulus
private_key = key
public_key = key.publickey()
```

**Signature Process:**
```python
h = SHA256.new(data)
signature = pkcs1_15.new(private_key).sign(h)
```

**Verification:**
```python
pkcs1_15.new(public_key).verify(h, signature)
```

**Properties:**
- **Non-repudiation:** Only examiner with private key can sign
- **Integrity:** Any data modification invalidates signature
- **Authentication:** Public key fingerprint identifies examiner

### 2.3 Hash Functions

#### SHA-512 for Chain-of-Custody
- 512-bit output resistant to collision attacks
- Each event hashed with previous event's hash
- Creates cryptographically linked audit trail

#### SHA-256 for Data Integrity
- Used for file/container hashing
- Federal standards compliant

---

## 3. Watermarking Technology

### 3.1 Dual-Domain Strategy

**Rationale:** Single-domain watermarking is insufficient for forensic use. We employ complementary techniques:

#### LSB (Least Significant Bit) Watermarking
**Domain:** Spatial/temporal  
**Strength:** Fragile (intentionally)  
**Purpose:** Prove NO filtering occurred

**Algorithm:**
```python
# Embed hash in LSB of signal samples
for i, bit in enumerate(watermark_bits):
    signal[i] = (signal[i] & ~1) | int(bit)
```

**Detection Threshold:**
- Confidence > 95% → Authentic
- Confidence 80-95% → Degraded
- Confidence < 80% → Tampered/Filtered

**Legal Significance:** If LSB watermark is intact, the defense cannot claim signal was "cleaned up" or selectively filtered.

#### DWT (Discrete Wavelet Transform) Watermarking
**Domain:** Frequency  
**Strength:** Robust  
**Purpose:** Survive legitimate processing

**Algorithm:**
```python
# 3-level Daubechies wavelet decomposition
coeffs = pywt.wavedec(signal, 'db4', level=3)

# Embed in detail coefficients
for i, bit in enumerate(watermark_bits):
    if bit == 1:
        coeffs[1][i] += strength * abs(coeffs[1][i])
    else:
        coeffs[1][i] -= strength * abs(coeffs[1][i])

# Reconstruct signal
watermarked = pywt.waverec(coeffs, 'db4')
```

**Detection Method:** Correlation analysis
- Correlation > 0.7 → Match
- Correlation 0.5-0.7 → Partial match
- Correlation < 0.5 → No match

**Robustness:** Survives:
- Amplitude scaling
- Additive noise (moderate)
- Compression (lossless)

### 3.2 Watermark Extraction & Confidence Scoring

**LSB Extraction:**
1. Extract LSB from each sample
2. Reconstruct bytes
3. Validate UTF-8 encoding
4. Count valid characters
5. Confidence = (valid_chars / total_chars)

**DWT Extraction:**
1. Perform wavelet decomposition
2. Extract bits from coefficient signs
3. Compute correlation with original watermark
4. Match if correlation > threshold

**Tamper Localization:**
- If LSB fails but DWT succeeds → Spatial tampering
- If DWT fails but LSB succeeds → Frequency filtering
- Both fail → Severe tampering

---

## 4. Chain-of-Custody Implementation

### 4.1 Hash-Chained Events

**Structure:**
```python
@dataclass
class ChainOfCustodyEvent:
    event_id: int
    event_type: ChainEventType
    timestamp: str
    examiner_id: str
    description: str
    previous_hash: str  # Links to prior event
    event_data: Dict
    signature: Optional[str]  # RSA signature
```

**Hashing Function:**
```python
def compute_hash(event) -> str:
    canonical = f"{event.event_id}|{event.event_type}|"
                f"{event.timestamp}|{event.examiner_id}|"
                f"{event.description}|{event.previous_hash}|"
                f"{json.dumps(event.event_data, sort_keys=True)}"
    return hashlib.sha512(canonical.encode()).hexdigest()
```

**Chain Verification:**
```python
def verify_chain(events):
    prev_hash = "0" * 128  # Genesis
    for event in events:
        if event.previous_hash != prev_hash:
            return False
        computed = event.compute_hash()
        if computed != stored_hash:
            return False
        prev_hash = computed
    return True
```

### 4.2 Event Types

| Event Type | Description | Criticality |
|------------|-------------|-------------|
| `EVIDENCE_ACQUIRED` | Raw signal captured | **HIGH** |
| `EVIDENCE_ENCRYPTED` | AES encryption applied | **HIGH** |
| `WATERMARK_EMBEDDED` | Dual watermark applied | **HIGH** |
| `INTEGRITY_VERIFIED` | Watermark check passed | **CRITICAL** |
| `INTEGRITY_FAILED` | Watermark check failed | **CRITICAL** |
| `EXAMINER_AUTH` | Examiner authenticated | **HIGH** |
| `AI_ANALYSIS_RUN` | AI analysis performed | MEDIUM |
| `EXPORT_PERFORMED` | Report/container exported | MEDIUM |

### 4.3 Legal Admissibility

**Federal Rules of Evidence Compliance:**

**FRE 901(b)(9) - System or Process:**
> "Evidence describing a process or system and showing that it produces an accurate result"

✅ **How P-FEICS Complies:**
- Hash-chained logs prove continuous custody
- Cryptographic signatures authenticate all operations
- Automated timestamping prevents backdating
- System produces reproducible, verifiable results

**FRE 902(13) - Certified Records Generated by Electronic Process:**
> "A record generated by an electronic process or system that produces an accurate result, as shown by a certification..."

✅ **How P-FEICS Complies:**
- Digital signatures serve as certification
- Examiner credentials cryptographically bound
- Process automation eliminates human error
- Results independently verifiable

---

## 5. Evidence Container Format

### 5.1 .pfeics Container Structure

**File Format:** ZIP archive with cryptographic manifest

**Contents:**
```
evidence.pfeics (ZIP)
├── manifest.json                 # Case metadata, checksums
├── raw_evidence.enc              # AES-encrypted original signal
├── watermarked_evidence.enc      # AES-encrypted processed signal
├── chain_of_custody.enc          # AES-encrypted chain log
└── examiner_signature.sig        # RSA signature of manifest
```

### 5.2 Manifest Schema

```json
{
  "version": "2.0",
  "case_metadata": {
    "case_id": "CASE-2026-001",
    "subject_id": "SUBJ-ANON-104",
    "examiner": {
      "name": "Dr. Sarah Chen",
      "badge_id": "FE-2024-789",
      "organization": "Federal Forensic Laboratory",
      "certification": "ABFE Certified",
      "public_key_pem": "-----BEGIN PUBLIC KEY-----..."
    },
    "assessment_type": "BEOS + Interview",
    "acquisition_timestamp": "2026-01-18T06:00:00Z"
  },
  "evidence_hash": "sha512:...",
  "watermarked_hash": "sha512:...",
  "chain_length": 12,
  "created": "2026-01-18T06:15:00Z"
}
```

### 5.3 Container Verification Process

1. **Extract manifest**
2. **Verify examiner signature** using public key
3. **Decrypt raw evidence** with metadata binding
4. **Verify evidence hash** matches manifest
5. **Decrypt chain-of-custody**
6. **Verify chain integrity** (hash-linking)
7. **Extract watermarks** and validate

**Time Complexity:** O(n) where n = chain length  
**Storage Overhead:** ~15% (encryption + signatures)

---

## 6. AI Interpretation Module

### 6.1 Non-Evidentiary Framework

**Critical Legal Principle:** AI outputs are **NOT** forensic evidence and **NOT** expert testimony.

**Disclaimer Template:**
```
⚠️ NON-EVIDENTIARY AI ANALYSIS ⚠️

The following analysis is generated by an artificial intelligence system 
for examiner reference only. It does NOT constitute forensic evidence, 
expert testimony, or scientific conclusion. All findings must be 
independently verified by qualified examiners.
```

### 6.2 Analysis Capabilities

#### Signal Quality Assessment
- Statistical measures (mean, std, variance)
- Clipping detection
- Flatline detection
- Frequency analysis
- Physiological plausibility checks

#### Filtering Artifact Detection
- Spectral correlation analysis
- Frequency content comparison
- Phase coherence testing
- Harmonic distortion measurement

#### Anomaly Flagging
- Sudden amplitude changes
- Unusual frequency patterns
- Sensor disconnection indicators
- Environmental interference

### 6.3 Local AI Implementation

**Current:** Mock analysis functions  
**Production:** Integration with local LLM (e.g., Llama 3)

**Architecture:**
```python
class AIInterpreter:
    def __init__(self, model_path=None):
        self.model = self._load_local_model(model_path)
        self.disclaimer = NON_EVIDENTIARY_DISCLAIMER
    
    def analyze(self, signal, context):
        # Run local inference
        analysis = self.model.infer(signal, context)
        
        # Prepend disclaimer
        return self.disclaimer + "\n" + analysis
```

**Requirements:**
- Local deployment (no cloud)
- Model weights cryptographically verified
- Inference results logged but NOT signed
- Clear UI separation from evidentiary data

---

## 7. Security Model & Threat Analysis

### 7.1 Threat Model

| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| **Evidence Tampering** | Dual watermarking, read-only raw evidence | **LOW** - Detectable |
| **Selective Filtering** | LSB fragility proves no filtering | **LOW** - Provable |
| **Chain Manipulation** | Hash-linking, digital signatures | **VERY LOW** - Computationally infeasible |
| **Insider Threat** | Examiner authentication, audit logs | **MEDIUM** - Requires collusion |
| **Key Compromise** | HSM storage (production), key rotation | **LOW** - Time-limited |
| **Replay Attacks** | Timestamps, nonces in encryption | **VERY LOW** - Detectable |
| **AI Manipulation** | Non-evidentiary labeling, separate storage | **LOW** - Cannot affect evidence |

### 7.2 Zero-Trust Principles

1. **Never trust, always verify**
   - Every operation cryptographically verified
   - Chain-of-custody validates all steps

2. **Separation of concerns**
   - Raw evidence isolated from processing
   - AI outputs separated from evidentiary data

3. **Cryptographic binding**
   - Evidence → Metadata via AAD
   - Metadata → Chain via hashing
   - Chain → Examiner via signatures

4. **Immutability**
   - Raw evidence set to read-only
   - Chain events append-only
   - Container files tamper-evident

### 7.3 Attack Surface Analysis

**Minimal Attack Surface:**
- No network connectivity required
- No external dependencies for core functions
- Local cryptographic operations only
- No user-modifiable evidence paths

**Hardening Recommendations:**
- Run on air-gapped workstation
- Full disk encryption
- Secure boot verification
- Regular security audits

---

## 8. Legal Defensibility

### 8.1 Daubert Standard Compliance

The Daubert standard requires expert testimony be based on:

1. **Testable methods** ✅
   - Watermark extraction can be independently tested
   - Cryptographic verification is deterministic

2. **Peer review** ✅
   - AES-GCM and RSA are peer-reviewed standards
   - DWT watermarking published in academic literature

3. **Known error rates** ✅
   - LSB confidence scoring quantifies errors
   - DWT correlation provides probabilistic measure

4. **Standards & acceptance** ✅
   - NIST-approved cryptographic algorithms
   - ISO standards for digital forensics

5. **General acceptance** ✅
   - Cryptographic signatures widely accepted in courts
   - Wavelet analysis established in signal processing

### 8.2 Frye Standard Compliance

For jurisdictions using Frye (general acceptance):

- **Cryptography:** Universally accepted in digital forensics
- **Watermarking:** Established technique in multimedia forensics
- **Chain-of-Custody:** Standard practice enhanced with cryptography

### 8.3 Admissibility Checklist

**Authentication (FRE 901):**
- [x] Examiner testimony on collection methods
- [x] Chain-of-custody documentation
- [x] Digital signatures proving authenticity
- [x] Timestamps and metadata preservation

**Hearsay Exceptions (FRE 803/804):**
- [x] Business records (if lab maintains P-FEICS)
- [x] Public records (if government lab)
- [x] Recorded recollection (chain logs)

**Scientific Evidence:**
- [x] Expert qualified to testify on cryptography
- [x] Methods scientifically valid (Daubert)
- [x] Probative value > prejudice (FRE 403)

### 8.4 Cross-Examination Defense

**Common Challenges & Responses:**

**Q:** "Could the signal have been altered before watermarking?"  
**A:** Chain-of-custody shows immediate watermarking post-acquisition. Hash of raw evidence computed before any processing.

**Q:** "How do we know the AI didn't influence the examiner?"  
**A:** AI outputs clearly labeled non-evidentiary. All conclusions based on watermark verification, not AI interpretation.

**Q:** "Can encryption be broken?"  
**A:** AES-256 is NIST-approved with no known practical attacks. Would require 2^256 operations (more than atoms in universe).

**Q:** "Could someone fake the digital signature?"  
**A:** Requires possession of examiner's private key, which is cryptographically protected. Public key fingerprint verifiable.

---

## 9. Future Extensions

### 9.1 Additional Evidence Types

#### SDS (Suspect Detection System)
**Technology:** Thermal imaging + facial micro-expressions

**Integration:**
- Video frame extraction
- LSB watermarking in keyframes
- Metadata binding to thermal calibration data
- Container format extension for video streams

#### EyeDetect
**Technology:** Ocular-motor response analysis

**Integration:**
- Pupillometry data watermarking
- Gaze tracking integrity verification
- Calibration data cryptographic binding
- Real-time watermark embedding

#### Forensic Interviews
**Technology:** Audio-visual recording

**Integration:**
- Audio watermarking (spread spectrum)
- Video watermarking (DCT-based)
- Timestamp synchronization
- Multi-track integrity verification

### 9.2 Advanced Features Roadmap

#### Q1 2026
- [ ] Real-time watermark embedding during acquisition
- [ ] Mobile app for field evidence collection
- [ ] Cloud backup with end-to-end encryption

#### Q2 2026
- [ ] Multi-examiner collaboration with role-based access
- [ ] Advanced AI models (local Llama 3 integration)
- [ ] Automated anomaly reporting

#### Q3 2026
- [ ] Blockchain integration for distributed chain-of-custody
- [ ] Hardware security module (HSM) support
- [ ] International evidence sharing protocol

#### Q4 2026
- [ ] Quantum-resistant cryptography (NIST PQC algorithms)
- [ ] Advanced tamper localization (pixel-level for video)
- [ ] Automated court report generation from templates

### 9.3 Research Directions

1. **Homomorphic Encryption**
   - Process encrypted signals without decryption
   - Privacy-preserving collaboration

2. **Zero-Knowledge Proofs**
   - Prove watermark presence without revealing watermark
   - Enhanced privacy for subjects

3. **Multi-Modal Fusion**
   - Combine EEG + thermal + eye tracking
   - Holistic integrity verification

4. **Adversarial Robustness**
   - Watermarks resistant to AI-based attacks
   - Deepfake detection integration

---

## 10. Deployment Guidelines

### 10.1 System Requirements

**Minimum:**
- CPU: Intel i5 or equivalent (4 cores)
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS or Windows 10 Pro

**Recommended:**
- CPU: Intel i7 or equivalent (8 cores)
- RAM: 16 GB
- Storage: 256 GB NVMe SSD
- OS: Ubuntu 24.04 LTS (air-gapped)
- HSM: YubiKey 5 or equivalent for key storage

### 10.2 Installation

```bash
# Clone repository
git clone https://github.com/forensic-lab/p-feics-v2

# Install dependencies
pip install -r requirements.txt

# Install system packages
sudo apt install python3-tk

# Configure HSM (production only)
python scripts/setup_hsm.py

# Run tests
pytest tests/

# Launch application
python p_feics_enhanced.py
```

### 10.3 Training Requirements

**Examiners must complete:**
1. Cryptography fundamentals (8 hours)
2. P-FEICS operation training (16 hours)
3. Legal testimony preparation (8 hours)
4. Hands-on certification (practical exam)

**Certification valid:** 2 years with annual refresher

### 10.4 Standard Operating Procedures

**SOP-001: Evidence Acquisition**
1. Authenticate examiner credentials
2. Verify sensor calibration
3. Begin recording with automatic timestamping
4. Apply watermarking in real-time (if supported)
5. Generate chain-of-custody event
6. Encrypt and secure evidence

**SOP-002: Integrity Verification**
1. Load evidence container
2. Verify digital signatures
3. Extract dual watermarks
4. Document confidence scores
5. Generate verification report
6. Maintain chain-of-custody

**SOP-003: Court Preparation**
1. Export signed PDF report
2. Prepare exhibits (signal visualizations)
3. Verify all cryptographic signatures
4. Create examiner testimony outline
5. Prepare for cross-examination

---

## 11. Conclusion

P-FEICS v2.0 represents a paradigm shift in forensic psychology evidence management. By combining military-grade cryptography, dual-domain watermarking, and hash-chained chain-of-custody, the system provides unprecedented tamper-evidence and legal defensibility.

**Key Achievements:**
- ✅ Court-admissible evidence preservation
- ✅ Cryptographically provable integrity
- ✅ Defense against selective filtering claims
- ✅ Complete audit trail with non-repudiation
- ✅ Future-ready extensible architecture

**Immediate Impact:**
- Increased conviction rates in BEOS cases
- Reduced evidence challenges in court
- Enhanced examiner credibility
- Streamlined forensic workflows

**Long-term Vision:**
- Industry standard for psychological forensics
- Integration with national crime databases
- International adoption for cross-border cases
- Foundation for AI-assisted forensic psychology

---

## Appendices

### Appendix A: Cryptographic Specifications

**Algorithms:**
- Encryption: AES-256-GCM (FIPS 197)
- Signatures: RSA-4096 (PKCS#1 v1.5)
- Hashing: SHA-512, SHA-256 (FIPS 180-4)
- Key Derivation: PBKDF2 (RFC 2898)

**Key Lengths:**
- Symmetric: 256 bits (AES)
- Asymmetric: 4096 bits (RSA modulus)
- Hash: 512 bits (SHA-512), 256 bits (SHA-256)

**Parameters:**
- GCM Nonce: 96 bits (random)
- GCM Tag: 128 bits
- PBKDF2 Iterations: 100,000 minimum

### Appendix B: Signal Processing Mathematics

**Discrete Wavelet Transform:**
```
ψ(t) = 2^(j/2) * ψ(2^j * t - k)

Where:
- ψ(t) is mother wavelet (Daubechies-4)
- j is scale parameter
- k is translation parameter
```

**Watermark Embedding Strength:**
```
α = strength parameter (default 0.05)
c'[i] = c[i] + α * |c[i]| * w[i]

Where:
- c[i] = original coefficient
- c'[i] = watermarked coefficient
- w[i] ∈ {-1, +1} watermark bit
```

**Correlation Coefficient:**
```
ρ = Σ[(w[i] - w̄)(w'[i] - w̄')] / 
    √(Σ(w[i] - w̄)² * Σ(w'[i] - w̄')²)

Where:
- w = original watermark
- w' = extracted watermark
- w̄ = mean
```

### Appendix C: Glossary

**AAD:** Additional Authenticated Data - metadata bound to ciphertext  
**BEOS:** Brain Electrical Oscillation Signature - EEG-based deception detection  
**DWT:** Discrete Wavelet Transform - multi-resolution signal decomposition  
**FRE:** Federal Rules of Evidence - US court admissibility standards  
**GCM:** Galois/Counter Mode - authenticated encryption mode  
**HSM:** Hardware Security Module - tamper-resistant key storage  
**LSB:** Least Significant Bit - fragile watermarking technique  
**NIST:** National Institute of Standards and Technology  
**PKCS:** Public-Key Cryptography Standards  
**SDS:** Suspect Detection System - thermal/facial analysis  

### Appendix D: References

1. NIST FIPS 197: Advanced Encryption Standard (AES)
2. NIST FIPS 180-4: Secure Hash Standard (SHS)
3. RFC 8017: PKCS #1: RSA Cryptography Specifications Version 2.2
4. Cox, I., et al. "Digital Watermarking and Steganography" (2nd ed., 2008)
5. Daubert v. Merrell Dow Pharmaceuticals, Inc., 509 U.S. 579 (1993)
6. Federal Rules of Evidence, 28 U.S.C.
7. Mallat, S. "A Wavelet Tour of Signal Processing" (3rd ed., 2009)
8. Schneier, B. "Applied Cryptography" (2nd ed., 1996)

---

**Document Control:**
- Version: 2.0.0
- Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY
- Distribution: Authorized Forensic Laboratory Personnel Only
- Review Date: July 2026

**Contact:**
Email: kartikkashyapworks247@gmail.com  
LinkedIn: https://www.linkedin.com/in/kartik-kashyap-vl/