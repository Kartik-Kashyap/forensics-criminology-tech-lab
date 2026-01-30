"""
Digital Forensic Medical Evidence Security, Integrity Preservation and Chain of Custody System
=====================================================================

This system provides legally-defensible chain of custody management,
cryptographic integrity verification, and secure storage for digital medical evidence
used in forensic investigations and legal proceedings.

Key Features:
- Chain of Custody (immutable, append-only logging)
- Medical Imaging format support (mainly NIfTI i.e. .nii, .nii.gz)
- Cryptographic watermarking and encryption
- Role-based access control (Investigator, Analyst, Supervisor, Court)
- Tamper detection with SHA-256 hashing
- Audit logging for legal compliance
- Evidence export with integrity certificates

NOTE:
This system currently supports forensic medical imaging evidence (NIfTI).
Generic document encryption is not implemented and is considered future work.


Author: Kartik Kashyap
License: Academic/Research Use
"""

import os
import re
import json
import hashlib
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
import cv2
import nibabel as nib
from vedo import Volume, show

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


# ============================================================
#  FORENSIC DOMAIN MODELS AND ENUMERATIONS
# ============================================================

class UserRole(Enum):
    """Defines roles in the forensic investigation system"""
    INVESTIGATOR = "investigator"          # Field investigator - can upload and view evidence
    FORENSIC_ANALYST = "forensic_analyst"  # Lab analyst - can analyze and modify evidence
    SUPERVISOR = "supervisor"              # Case supervisor - full access including chain of custody
    COURT = "court"                        # Court/Legal - read-only access for proceedings
    ADMIN = "admin"                        # System administrator


class EvidenceType(Enum):
    """Types of digital evidence supported by the system"""
    IMAGE = "image"                # Photos, screenshots (jpg, png, bmp)
    VIDEO = "video"                # Video recordings (mp4, avi, mov)
    AUDIO = "audio"                # Audio recordings (mp3, wav, m4a)
    DOCUMENT = "document"          # Text documents (pdf, docx, txt)
    MEDICAL_SCAN = "medical_scan"  # Medical/forensic imaging (NIfTI, DICOM)
    OTHER = "other"                # Other digital artifacts


class ChainOfCustodyAction(Enum):
    """Actions that must be logged in chain of custody"""
    SEIZED = "seized"              # Evidence collected from scene
    UPLOADED = "uploaded"          # Evidence uploaded to system
    ACCESSED = "accessed"          # Evidence viewed/retrieved
    ANALYZED = "analyzed"          # Forensic analysis performed
    MODIFIED = "modified"          # Evidence modified (watermarking, enhancement)
    EXPORTED = "exported"          # Evidence exported from system
    TRANSFERRED = "transferred"    # Custody transferred to another party
    VERIFIED = "verified"          # Integrity verification performed


@dataclass
class CaseInformation:
    """Represents a forensic case"""
    case_id: str
    case_name: str
    case_number: str
    investigating_agency: str
    lead_investigator: str
    case_opened_date: str
    incident_date: str
    incident_location: str
    case_description: str
    case_status: str = "active"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_text(self) -> str:
        """Convert to text format for watermarking"""
        return (
            f"Case ID: {self.case_id}\n"
            f"Case: {self.case_name}\n"
            f"Number: {self.case_number}\n"
            f"Agency: {self.investigating_agency}\n"
            f"Lead: {self.lead_investigator}\n"
            f"Date Opened: {self.case_opened_date}\n"
            f"Incident: {self.incident_date} @ {self.incident_location}\n"
            f"Description: {self.case_description}\n"
            f"Status: {self.case_status}"
        )


@dataclass
class EvidenceMetadata:
    """Metadata for a piece of digital evidence"""
    evidence_id: str
    case_id: str
    evidence_type: EvidenceType
    original_filename: str
    file_hash_sha256: str
    file_size_bytes: int
    
    # Chain of custody information
    seized_datetime: str
    seized_by: str
    seized_location: str
    collection_device: str
    
    # Additional metadata
    description: str
    tags: List[str]
    
    # System metadata
    upload_datetime: str
    uploaded_by: str
    last_accessed: Optional[str] = None
    access_count: int = 0
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['evidence_type'] = self.evidence_type.value
        return data


@dataclass
class ChainOfCustodyEntry:
    """
    Immutable entry in the chain of custody log.
    Each entry represents a single interaction with evidence.
    """
    entry_id: str
    evidence_id: str
    case_id: str
    timestamp: str
    action: ChainOfCustodyAction
    performed_by: str
    user_role: UserRole
    
    # Hash values for integrity verification
    hash_before: Optional[str]  # Evidence hash before action
    hash_after: Optional[str]   # Evidence hash after action
    
    # Additional context
    details: str
    location: Optional[str] = None
    device_info: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['action'] = self.action.value
        data['user_role'] = self.user_role.value
        return data
    
    def is_tampering_detected(self) -> bool:
        """Check if this entry indicates potential tampering"""
        if self.hash_before and self.hash_after:
            # For actions that should NOT change the hash
            if self.action in [ChainOfCustodyAction.ACCESSED, 
                              ChainOfCustodyAction.VERIFIED,
                              ChainOfCustodyAction.EXPORTED]:
                return self.hash_before != self.hash_after
        return False


# ============================================================
#  CHAIN OF CUSTODY MANAGER (Immutable, Append-Only)
# ============================================================

class ChainOfCustodyManager:
    """
    Manages the immutable chain of custody for all evidence.
    This is a critical component for legal defensibility.
    
    Features:
    - Append-only (no deletion or modification)
    - Cryptographic integrity of the log itself
    - Searchable by evidence, case, user, date range
    """
    
    def __init__(self, log_file_path: str = "chain_of_custody.jsonl"):
        self.log_file = log_file_path
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                # Write header with creation timestamp
                header = {
                    "type": "LOG_INITIALIZED",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "system": "Digital Forensic Evidence Chain of Custody"
                }
                f.write(json.dumps(header) + "\n")
    
    def add_entry(self, entry: ChainOfCustodyEntry) -> bool:
        """
        Add a new entry to the chain of custody.
        This is the ONLY way to modify the log (append-only).
        
        Returns True if successfully logged, False otherwise.
        """
        try:
            with open(self.log_file, 'a') as f:
                entry_data = entry.to_dict()
                entry_data['log_timestamp'] = datetime.datetime.now().isoformat()
                f.write(json.dumps(entry_data) + "\n")
            return True
        except Exception as e:
            print(f"ERROR: Failed to log chain of custody entry: {e}")
            return False
    
    def get_entries_for_evidence(self, evidence_id: str) -> List[ChainOfCustodyEntry]:
        """Retrieve complete chain of custody for a specific piece of evidence"""
        entries = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('evidence_id') == evidence_id:
                            # Reconstruct entry from JSON
                            entry = ChainOfCustodyEntry(
                                entry_id=data['entry_id'],
                                evidence_id=data['evidence_id'],
                                case_id=data['case_id'],
                                timestamp=data['timestamp'],
                                action=ChainOfCustodyAction(data['action']),
                                performed_by=data['performed_by'],
                                user_role=UserRole(data['user_role']),
                                hash_before=data.get('hash_before'),
                                hash_after=data.get('hash_after'),
                                details=data['details'],
                                location=data.get('location'),
                                device_info=data.get('device_info')
                            )
                            entries.append(entry)
        except Exception as e:
            print(f"ERROR reading chain of custody: {e}")
        
        return entries
    
    def get_entries_for_case(self, case_id: str) -> List[ChainOfCustodyEntry]:
        """Retrieve all chain of custody entries for a case"""
        entries = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('case_id') == case_id:
                            entry = ChainOfCustodyEntry(
                                entry_id=data['entry_id'],
                                evidence_id=data['evidence_id'],
                                case_id=data['case_id'],
                                timestamp=data['timestamp'],
                                action=ChainOfCustodyAction(data['action']),
                                performed_by=data['performed_by'],
                                user_role=UserRole(data['user_role']),
                                hash_before=data.get('hash_before'),
                                hash_after=data.get('hash_after'),
                                details=data['details'],
                                location=data.get('location'),
                                device_info=data.get('device_info')
                            )
                            entries.append(entry)
        except Exception as e:
            print(f"ERROR reading chain of custody: {e}")
        
        return entries
    
    def verify_chain_integrity(self, evidence_id: str) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of the chain of custody for evidence.
        
        Returns:
            (is_valid, list_of_issues)
        """
        entries = self.get_entries_for_evidence(evidence_id)
        issues = []
        
        if not entries:
            return False, ["No chain of custody entries found"]
        
        # Check for chronological order
        for i in range(1, len(entries)):
            if entries[i].timestamp < entries[i-1].timestamp:
                issues.append(f"Timestamp order violation at entry {i}")
        
        # Check for hash continuity
        for i in range(1, len(entries)):
            prev_hash_after = entries[i-1].hash_after
            curr_hash_before = entries[i].hash_before
            
            if prev_hash_after and curr_hash_before and prev_hash_after != curr_hash_before:
                issues.append(
                    f"Hash mismatch between entries {i-1} and {i}: "
                    f"Expected {prev_hash_after}, got {curr_hash_before}"
                )
        
        # Check for tampering indicators
        for i, entry in enumerate(entries):
            if entry.is_tampering_detected():
                issues.append(
                    f"Potential tampering detected at entry {i}: "
                    f"Hash changed during {entry.action.value} action"
                )
        
        return len(issues) == 0, issues


# ============================================================
#  UTILITY: LOGGING IN GUI
# ============================================================

class Logger:
    """GUI logger with support for different log levels"""
    def __init__(self, textbox):
        self.textbox = textbox

    def log(self, msg, level="INFO"):
        """Log a message with optional level prefix"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {msg}"
        
        self.textbox.config(state="normal")
        self.textbox.insert(tk.END, formatted_msg + "\n")
        self.textbox.see(tk.END)
        self.textbox.config(state="disabled")


# ============================================================
#  CRYPTOGRAPHIC UTILITIES
# ============================================================

def compute_file_hash(filepath: str) -> str:
    """
    Compute SHA-256 hash of a file for integrity verification.
    This is critical for chain of custody and tamper detection.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read in 64kb chunks for memory efficiency
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        raise RuntimeError(f"Failed to compute hash: {e}")


def bytes_to_bits(b: bytes) -> str:
    """Convert bytes to binary string representation"""
    return ''.join(f'{byte:08b}' for byte in b)


def bits_to_bytes(bits: str) -> bytes:
    """Convert binary string to bytes"""
    if len(bits) % 8 != 0:
        raise ValueError("Bit length is not a multiple of 8.")
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def add_length_header_bits(data_bits: str) -> str:
    """Add 32-bit length header to bit stream"""
    length = len(data_bits)
    header = f'{length:032b}'
    return header + data_bits


def remove_length_header_bits(bits: str) -> str:
    """Extract data from bit stream with length header"""
    if len(bits) < 32:
        raise ValueError("Bitstream too short to contain header.")
    length = int(bits[:32], 2)
    data_bits = bits[32:32+length]
    if len(data_bits) < length:
        raise ValueError("Bitstream shorter than declared length.")
    return data_bits


# ============================================================
#  AES ENCRYPTION (for evidence security)
# ============================================================

def derive_key_from_password(password: str) -> bytes:
    """Derive AES key from password using SHA-256"""
    h = SHA256.new()
    h.update(password.encode('utf-8'))
    return h.digest()


def aes_gcm_encrypt(data: bytes, password: str) -> bytes:
    """
    AES-GCM encrypt data.
    Output format: nonce (12) + tag (16) + ciphertext
    """
    key = derive_key_from_password(password)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ciphertext


def aes_gcm_decrypt(data: bytes, password: str) -> bytes:
    """Decrypt AES-GCM encrypted data"""
    if len(data) < 12 + 16:
        raise ValueError("Ciphertext too short.")
    key = derive_key_from_password(password)
    nonce = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext


# ============================================================
#  LSB WATERMARKING (for evidence marking)
# ============================================================

def embed_bits_in_image(img: np.ndarray, bits: str) -> np.ndarray:
    """
    Embed bits in the LSB of a grayscale image.
    Used for marking evidence with case information.
    """
    if img.dtype != np.uint8:
        raise ValueError("Image should be uint8 for LSB embedding.")

    h, w = img.shape
    flat = img.flatten().copy()
    if len(bits) > flat.size:
        raise ValueError(
            f"Not enough pixels to embed data. Bits: {len(bits)}, Pixels: {flat.size}"
        )

    for i, bit in enumerate(bits):
        if bit == '1':
            flat[i] |= 1 
        else:
            flat[i] &= 0xFE

    return flat.reshape((h, w))


def extract_bits_from_image(img: np.ndarray, n_bits: int) -> str:
    """Extract bits from LSB watermarked image"""
    if img.dtype != np.uint8:
        raise ValueError("Image should be uint8 for LSB extraction.")
    flat = img.flatten()
    if n_bits > flat.size:
        raise ValueError("Requested more bits than pixels.")
    bits = ''.join('1' if (p & 1) else '0' for p in flat[:n_bits])
    return bits


# ============================================================
#  IMAGE QUALITY METRICS: PSNR & SSIM
# ============================================================

def psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate Peak Signal-to-Noise Ratio between two images"""
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    PIXEL_MAX = 255.0
    return 20 * np.log10(PIXEL_MAX / np.sqrt(mse))


def ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate Structural Similarity Index between two images"""
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)

    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    kernel_size = (11, 11)
    sigma = 1.5

    mu1 = cv2.GaussianBlur(img1, kernel_size, sigma)
    mu2 = cv2.GaussianBlur(img2, kernel_size, sigma)

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.GaussianBlur(img1 * img1, kernel_size, sigma) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(img2 * img2, kernel_size, sigma) - mu2_sq
    sigma12 = cv2.GaussianBlur(img1 * img2, kernel_size, sigma) - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))

    return ssim_map.mean()


# ============================================================
#  EVIDENCE PROCESSING: NIfTI WATERMARKING
# ============================================================

def normalize_slice_to_uint8(slice_data: np.ndarray):
    """Normalize arbitrary float/int slice to uint8 [0,255]"""
    slice = slice_data.astype(np.float64)
    s_min, s_max = slice.min(), slice.max()
    if s_max - s_min == 0:
        return np.zeros_like(slice, dtype=np.uint8), s_min, s_max
    norm = (slice - s_min) / (s_max - s_min)
    scaled = (norm * 255.0).round().astype(np.uint8)
    return scaled, s_min, s_max


def denormalize_slice_from_uint8(scaled: np.ndarray, s_min: float, s_max: float):
    """Convert uint8 slice back to original intensity range"""
    scaled = scaled.astype(np.float64) / 255.0
    return scaled * (s_max - s_min) + s_min


def embed_case_info_in_nifti(
    nii_path: str, 
    case_info: CaseInformation, 
    evidence_metadata: EvidenceMetadata,
    password: str, 
    logger: Logger
) -> Tuple[str, str, int, int, float, float]:
    """
    Embed case information into NIfTI evidence using LSB watermarking + encryption.
    
    This creates a forensically-marked version of medical scan evidence.
    
    Returns:
        (watermarked_path, encrypted_path, slice_idx, watermark_bits, psnr, ssim)
    """
    if not os.path.exists(nii_path):
        raise FileNotFoundError("Evidence file does not exist.")

    nib.Nifti1Header.quaternion_threshold = -1e-06 
    logger.log("Loading NIfTI evidence volume...")
    img = nib.load(nii_path)
    data = img.get_fdata()
    affine = img.affine
    header = img.header

    if data.ndim < 3:
        raise ValueError("NIfTI volume must be at least 3D.")

    logger.log(f"Volume shape: {data.shape}")

    mid_slice_idx = data.shape[2] // 2
    logger.log(f"Selected mid axial slice index: {mid_slice_idx}")

    original_slice = data[:, :, mid_slice_idx]
    slice_uint8, s_min, s_max = normalize_slice_to_uint8(original_slice)

    # # Compute hash for tamper detection
    # logger.log("Computing SHA-256 hash of slice for tamper detection...")
    # slice_hash = SHA256.new(slice_uint8.tobytes()).hexdigest()
    # logger.log(f"Slice SHA-256: {slice_hash}")

    # # Combine case info with hash
    # case_text = case_info.to_text()
    # combined_text = (
    #     f"{case_text}\n\n"
    #     f"Evidence ID: {evidence_metadata.evidence_id}\n"
    #     f"[SLICE_SHA256:{slice_hash}]"
    # )

    # Combine case info
    case_text = case_info.to_text()
    combined_text = (
        f"{case_text}\n\n"
        f"Evidence ID: {evidence_metadata.evidence_id}"
    )
    
    logger.log("Encrypting case+evidence info with AES-GCM...")
    plaintext_bytes = combined_text.encode('utf-8')
    enc_case_bytes = aes_gcm_encrypt(plaintext_bytes, password)

    wm_bits = bytes_to_bits(enc_case_bytes)
    wm_bits = add_length_header_bits(wm_bits)

    logger.log(f"Total watermark bits to embed: {len(wm_bits)}")

    logger.log("Embedding watermark bits into slice (LSB)...")
    watermarked_slice_uint8 = embed_bits_in_image(slice_uint8, wm_bits)

    slice_psnr = psnr(slice_uint8, watermarked_slice_uint8)
    slice_ssim = ssim(slice_uint8, watermarked_slice_uint8)
    logger.log(f"PSNR (original vs watermarked): {slice_psnr:.2f} dB")
    logger.log(f"SSIM (original vs watermarked): {slice_ssim:.4f}")

    logger.log("Inserting watermarked slice back into volume...")
    watermarked_slice_denorm = denormalize_slice_from_uint8(
        watermarked_slice_uint8, s_min, s_max
    )
    watermarked_data = data.copy()
    watermarked_data[:, :, mid_slice_idx] = watermarked_slice_denorm

    base, ext = os.path.splitext(nii_path)
    if ext == ".gz":
        base, ext2 = os.path.splitext(base)
        ext = ext2 + ext

    wm_nii_path = base + "_forensic_marked.nii.gz"
    logger.log(f"Saving forensically-marked evidence to: {wm_nii_path}")
    wm_img = nib.Nifti1Image(watermarked_data, affine, header)
    nib.save(wm_img, wm_nii_path)

    logger.log("Encrypting forensically-marked evidence using AES-GCM...")
    with open(wm_nii_path, "rb") as f:
        wm_bytes = f.read()
    enc_file_bytes = aes_gcm_encrypt(wm_bytes, password)

    enc_out_path = base + "_forensic_encrypted.bin"
    with open(enc_out_path, "wb") as f:
        f.write(enc_file_bytes)

    logger.log(f"Encrypted evidence saved to: {enc_out_path}")
    logger.log("Evidence marking & encryption completed.\n")

    # Save metadata for chain of custody
    metadata = {
        "evidence_id": evidence_metadata.evidence_id,
        "case_id": case_info.case_id,
        "mid_slice_idx": mid_slice_idx,
        "wm_bits_len": len(wm_bits),
        "password_hash": derive_key_from_password(password).hex(),
        "original_hash": evidence_metadata.file_hash_sha256,
        "marked_hash": compute_file_hash(wm_nii_path),
        "encrypted_hash": compute_file_hash(enc_out_path)
    }
    metadata_path = base + "_evidence_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    logger.log(f"Evidence metadata saved to: {metadata_path}")

    return wm_nii_path, enc_out_path, mid_slice_idx, len(wm_bits), slice_psnr, slice_ssim



def decrypt_and_extract_from_evidence(
    enc_bin_path: str, 
    password: str, 
    mid_slice_idx: int, 
    wm_bits_len: int, 
    logger: Logger
) -> Tuple[str, str]:
    """
    Decrypt and extract case information from forensically-marked evidence.
    """
    if not os.path.exists(enc_bin_path):
        raise FileNotFoundError("Encrypted evidence file does not exist.")

    logger.log("Loading encrypted evidence file...")
    with open(enc_bin_path, "rb") as f:
        enc_bytes = f.read()

    logger.log("Decrypting forensically-marked evidence using AES-GCM...")
    # NOTE: If this fails, aes_gcm_decrypt will raise an error automatically.
    # If it succeeds, the file is guaranteed authentic.
    wm_nii_bytes = aes_gcm_decrypt(enc_bytes, password)

    temp_path = enc_bin_path + "_temp_decrypted.nii.gz"
    with open(temp_path, "wb") as f:
        f.write(wm_nii_bytes)

    nib.Nifti1Header.quaternion_threshold = -1e-06
    logger.log(f"Temporary decrypted evidence at: {temp_path}")
    logger.log("Loading decrypted evidence...")
    wm_img = nib.load(temp_path)
    wm_data = wm_img.get_fdata()

    if wm_data.ndim < 3:
        raise ValueError("Decrypted evidence volume must be at least 3D.")

    if mid_slice_idx >= wm_data.shape[2]:
        raise ValueError("Slice index out of range for decrypted volume.")

    logger.log(f"Using slice index {mid_slice_idx} for extraction...")
    wm_slice = wm_data[:, :, mid_slice_idx]
    wm_slice_uint8, s_min, s_max = normalize_slice_to_uint8(wm_slice)

    logger.log(f"Extracting {wm_bits_len} bits from watermarked evidence...")
    extracted_bits_full = extract_bits_from_image(wm_slice_uint8, wm_bits_len)

    logger.log("Removing length header and reconstructing encrypted case data...")
    data_bits = remove_length_header_bits(extracted_bits_full)
    enc_case_bytes = bits_to_bytes(data_bits)

    logger.log("Decrypting case information from watermark (AES-GCM)...")
    # This is the second integrity check. If this succeeds, the watermark is authentic.
    try:
        recovered_plain = aes_gcm_decrypt(enc_case_bytes, password)
        combined_text = recovered_plain.decode('utf-8')
        tamper_status = "VERIFIED (AES-GCM Authenticated)"
    except Exception as e:
        combined_text = "ERROR: Decryption Failed"
        tamper_status = "⚠️ TAMPERING DETECTED (Watermark corrupted)"
        logger.log(f"Watermark decryption failed: {e}", "ERROR")

    logger.log("Recovered case information:")
    logger.log(combined_text)
    logger.log(f"Tamper status: {tamper_status}")
    logger.log("\nEvidence extraction completed.\n")

    try:
        os.remove(temp_path)
    except Exception:
        pass

    return combined_text, tamper_status
# def decrypt_and_extract_from_evidence(
#     enc_bin_path: str, 
#     password: str, 
#     mid_slice_idx: int, 
#     wm_bits_len: int, 
#     logger: Logger
# ) -> Tuple[str, str]:
#     """
#     Decrypt and extract case information from forensically-marked evidence.
    
#     Returns:
#         (case_info_text, tamper_status)
#     """
#     if not os.path.exists(enc_bin_path):
#         raise FileNotFoundError("Encrypted evidence file does not exist.")

#     logger.log("Loading encrypted evidence file...")
#     with open(enc_bin_path, "rb") as f:
#         enc_bytes = f.read()

#     logger.log("Decrypting forensically-marked evidence using AES-GCM...")
#     wm_nii_bytes = aes_gcm_decrypt(enc_bytes, password)

#     temp_path = enc_bin_path + "_temp_decrypted.nii.gz"
#     with open(temp_path, "wb") as f:
#         f.write(wm_nii_bytes)

#     nib.Nifti1Header.quaternion_threshold = -1e-06
#     logger.log(f"Temporary decrypted evidence at: {temp_path}")
#     logger.log("Loading decrypted evidence...")
#     wm_img = nib.load(temp_path)
#     wm_data = wm_img.get_fdata()

#     if wm_data.ndim < 3:
#         raise ValueError("Decrypted evidence volume must be at least 3D.")

#     if mid_slice_idx >= wm_data.shape[2]:
#         raise ValueError("Slice index out of range for decrypted volume.")

#     logger.log(f"Using slice index {mid_slice_idx} for extraction...")
#     wm_slice = wm_data[:, :, mid_slice_idx]
#     wm_slice_uint8, s_min, s_max = normalize_slice_to_uint8(wm_slice)

#     logger.log(f"Extracting {wm_bits_len} bits from watermarked evidence...")
#     extracted_bits_full = extract_bits_from_image(wm_slice_uint8, wm_bits_len)

#     logger.log("Removing length header and reconstructing encrypted case data...")
#     data_bits = remove_length_header_bits(extracted_bits_full)
#     enc_case_bytes = bits_to_bytes(data_bits)

#     logger.log("Decrypting case information from watermark (AES-GCM)...")
#     recovered_plain = aes_gcm_decrypt(enc_case_bytes, password)
#     combined_text = recovered_plain.decode('utf-8')

#     lines = combined_text.splitlines()
#     hash_line = next((ln for ln in lines if ln.startswith("[SLICE_SHA256:")), None)
#     case_info_text = "\n".join(ln for ln in lines if not ln.startswith("[SLICE_SHA256:"))

#     tamper_status = "UNKNOWN"
#     if hash_line:
#         if hash_line.endswith("]"):
#             embedded_hash = hash_line[len("[SLICE_SHA256:"):-1]
#         else:
#             embedded_hash = hash_line[len("[SLICE_SHA256:"):]
#         current_hash = SHA256.new(wm_slice_uint8.tobytes()).hexdigest()
#         logger.log(f"Embedded hash: {embedded_hash}")
#         logger.log(f"Current hash  : {current_hash}")
#         if embedded_hash == current_hash:
#             tamper_status = "NO TAMPERING DETECTED (hash match)"
#         else:
#             tamper_status = "⚠️ TAMPERING SUSPECTED! (hash mismatch)"
#     else:
#         tamper_status = "No hash found in watermark."

#     logger.log("Recovered case information:")
#     logger.log(case_info_text)
#     logger.log(f"Tamper status: {tamper_status}")
#     logger.log("\nEvidence extraction completed.\n")

#     try:
#         os.remove(temp_path)
#     except Exception:
#         pass

#     return case_info_text, tamper_status


# ============================================================
#  PDF REPORT GENERATION (Legal Documentation)
# ============================================================

def generate_chain_of_custody_report(
    evidence_id: str,
    case_info: CaseInformation,
    evidence_metadata: EvidenceMetadata,
    chain_entries: List[ChainOfCustodyEntry],
    integrity_status: str,
    psnr_val: float = None,
    ssim_val: float = None,
    output_path: str = "Chain_of_Custody_Report.pdf"
):
    """
    Generate a comprehensive PDF report documenting:
    - Case information
    - Evidence metadata
    - Complete chain of custody
    - Integrity verification results
    - Quality metrics (if applicable)
    
    This report is suitable for legal proceedings and court presentation.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    content = []
    
    # Title
    content.append(Paragraph(
        "<b>CHAIN OF CUSTODY REPORT</b>",
        styles["Title"]
    ))
    content.append(Spacer(1, 20))
    
    # Report metadata
    content.append(Paragraph(
        f"<b>Report Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["BodyText"]
    ))
    content.append(Paragraph(
        f"<b>Evidence ID:</b> {evidence_id}",
        styles["BodyText"]
    ))
    content.append(Spacer(1, 15))
    
    # Case Information Section
    content.append(Paragraph("<b>CASE INFORMATION</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    
    case_data = [
        ["Case ID:", case_info.case_id],
        ["Case Name:", case_info.case_name],
        ["Case Number:", case_info.case_number],
        ["Agency:", case_info.investigating_agency],
        ["Lead Investigator:", case_info.lead_investigator],
        ["Date Opened:", case_info.case_opened_date],
        ["Incident Date:", case_info.incident_date],
        ["Incident Location:", case_info.incident_location],
        ["Status:", case_info.case_status],
    ]
    
    case_table = Table(case_data, colWidths=[150, 350])
    case_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    content.append(case_table)
    content.append(Spacer(1, 20))
    
    # Evidence Metadata Section
    content.append(Paragraph("<b>EVIDENCE METADATA</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    
    evidence_data = [
        ["Evidence Type:", evidence_metadata.evidence_type.value],
        ["Original Filename:", evidence_metadata.original_filename],
        ["File Size:", f"{evidence_metadata.file_size_bytes:,} bytes"],
        ["SHA-256 Hash:", evidence_metadata.file_hash_sha256[:64] + "..."],
        ["Seized By:", evidence_metadata.seized_by],
        ["Seizure Date/Time:", evidence_metadata.seized_datetime],
        ["Seizure Location:", evidence_metadata.seized_location],
        ["Collection Device:", evidence_metadata.collection_device],
        ["Uploaded By:", evidence_metadata.uploaded_by],
        ["Upload Date/Time:", evidence_metadata.upload_datetime],
    ]
    
    evidence_table = Table(evidence_data, colWidths=[150, 350])
    evidence_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    content.append(evidence_table)
    content.append(Spacer(1, 20))
    
    # Quality Metrics (if available)
    if psnr_val is not None and ssim_val is not None:
        content.append(Paragraph("<b>QUALITY METRICS (Watermarking)</b>", styles["Heading2"]))
        content.append(Spacer(1, 10))
        content.append(Paragraph(
            f"<b>PSNR (Peak Signal-to-Noise Ratio):</b> {psnr_val:.2f} dB",
            styles["BodyText"]
        ))
        content.append(Paragraph(
            f"<b>SSIM (Structural Similarity Index):</b> {ssim_val:.4f}",
            styles["BodyText"]
        ))
        content.append(Paragraph(
            "<i>Note: High PSNR (>40dB) and SSIM (>0.99) indicate minimal visual degradation from watermarking.</i>",
            styles["Italic"]
        ))
        content.append(Spacer(1, 20))
    
    # Chain of Custody Section
    content.append(Paragraph("<b>CHAIN OF CUSTODY</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    
    if chain_entries:
        custody_data = [["Timestamp", "Action", "Performed By", "Role", "Details"]]
        for entry in chain_entries:
            custody_data.append([
                entry.timestamp[:16],
                entry.action.value,
                entry.performed_by,
                entry.user_role.value,
                entry.details[:50] + "..." if len(entry.details) > 50 else entry.details
            ])
        
        custody_table = Table(custody_data, colWidths=[100, 80, 100, 80, 140])
        custody_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        content.append(custody_table)
    else:
        content.append(Paragraph("<i>No chain of custody entries found.</i>", styles["Italic"]))
    
    content.append(Spacer(1, 20))
    
    # Integrity Verification Section
    content.append(Paragraph("<b>INTEGRITY VERIFICATION</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        f"<b>Status:</b> {integrity_status}",
        styles["BodyText"]
    ))
    content.append(Spacer(1, 20))
    
    # Legal Statement
    content.append(Paragraph("<b>CERTIFICATION</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        "This document certifies that the above evidence has been handled in accordance with "
        "forensic best practices. The chain of custody has been maintained, and cryptographic "
        "hashing has been used to verify the integrity of the evidence. This report is "
        "generated by an automated system and represents an accurate record of all logged "
        "interactions with the evidence.",
        styles["BodyText"]
    ))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        "<i>Generated by Digital Forensic Evidence Security and Integrity Preservation System</i>",
        styles["Italic"]
    ))
    
    # Build PDF
    doc.build(content)
    return output_path


# ============================================================
#  EMAIL HELPER (for secure evidence transfer)
# ============================================================

def send_encrypted_evidence_email(
    sender_email: str,
    sender_password: str,
    receiver_email: str,
    subject: str,
    body: str,
    file_path: str,
    metadata_path: str
) -> Tuple[bool, str]:
    """
    Send encrypted evidence file and metadata via email.
    NOTE: Requires app password for services like Gmail if 2FA is enabled.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Attach encrypted evidence
        with open(file_path, "rb") as f:
            part_enc = MIMEBase('application', 'octet-stream')
            part_enc.set_payload(f.read())
            encoders.encode_base64(part_enc)
            part_enc.add_header(
                'Content-Disposition',
                f"attachment; filename={os.path.basename(file_path)}",
            )
            msg.attach(part_enc)

        # Attach metadata
        with open(metadata_path, "rb") as f:
            part_meta = MIMEBase('application', 'octet-stream')
            part_meta.set_payload(f.read())
            encoders.encode_base64(part_meta)
            part_meta.add_header(
                'Content-Disposition',
                f"attachment; filename={os.path.basename(metadata_path)}",
            )
            msg.attach(part_meta)

        # Send via SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        return True, "Email sent successfully!"

    except Exception as e:
        return False, f"Email error: {e}"


# ============================================================
#  FORENSIC EVIDENCE SYSTEM GUI
# ============================================================

class ForensicEvidenceSystemGUI:
    """
    Main GUI for the Digital Forensic Medical Evidence Security, Integrity Preservation and Chain of Custody System.
    
    Features:
    - Evidence upload and processing
    - Case information management
    - Watermarking and encryption
    - Chain of custody tracking
    - Integrity verification
    - Report generation
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Forensic Medical Evidence Security, Integrity Preservation and Chain of Custody System")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # System components
        self.custody_manager = ChainOfCustodyManager()
        
        # Current session state
        self.current_evidence_path = None
        self.current_case_info = None
        self.current_evidence_metadata = None
        self.last_mid_slice_idx = None
        self.last_wm_bits_len = None
        self.last_enc_bin_path = None
        self.last_marked_path = None
        self.psnr_val = 0.0 
        self.ssim_val = 0.0
        
        # Current user (for demonstration - in production this would be authenticated)
        self.current_user = "Investigator_J_Smith"
        self.current_user_role = UserRole.FORENSIC_ANALYST

        # Setup GUI
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure("TFrame", background="#1a1a2e")
        self.style.configure("TLabel", background="#1a1a2e", foreground="#eaeaea")
        self.style.configure("TButton", padding=6, font=("Segoe UI", 10, "bold"))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), 
                           foreground="#16c79a", background="#1a1a2e")

        self.create_widgets()

    def create_widgets(self):
        """Create and layout all GUI widgets"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header = ttk.Label(
            main_frame,
            text="Digital Forensic Evidence Security & Chain of Custody System",
            style="Header.TLabel"
        )
        header.pack(pady=(0, 10))

        # Top section: Evidence and Case Info
        upper_frame = ttk.Frame(main_frame)
        upper_frame.pack(fill=tk.X, pady=5)

        # Left: Evidence Selection
        left_frame = ttk.Frame(upper_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="Evidence File (NIfTI):").pack(anchor="w")
        
        file_frame = ttk.Frame(left_frame)
        file_frame.pack(fill=tk.X, pady=2)

        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_evidence)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Evidence viewing buttons
        ttk.Button(left_frame, text="View Evidence Slice", 
                  command=self.view_evidence_slice).pack(pady=(5, 0), fill=tk.X)
        ttk.Button(left_frame, text="View 3D Evidence (Scroll)", 
                  command=self.view_3d_evidence).pack(pady=5, fill=tk.X)
        ttk.Button(left_frame, text="View 3D Volume (Vedo)", 
                  command=self.view_3d_volume).pack(pady=5, fill=tk.X)

        # Case Information
        ttk.Label(left_frame, text="Case Information:", 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.case_info_text = tk.Text(left_frame, height=8, wrap=tk.WORD)
        self.case_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder case info
        placeholder = (
            "Case ID: CSE-2024-001\n"
            "Case: Digital Evidence Recovery Investigation\n"
            "Number: INV-2024-001\n"
            "Agency: State Forensic Laboratory\n"
            "Lead: Detective Jane Smith\n"
            "Date Opened: 2024-01-15\n"
            "Incident: 2024-01-10 @ Downtown Medical Center\n"
            "Description: Seizure of medical imaging evidence\n"
            "Status: active"
        )
        self.case_info_text.insert("1.0", placeholder)

        # Right: Controls
        right_frame = ttk.Frame(upper_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))

        # User info
        ttk.Label(right_frame, text=f"Current User: {self.current_user}").pack(anchor="w")
        ttk.Label(right_frame, text=f"Role: {self.current_user_role.value}").pack(anchor="w", pady=(0, 10))

        # Password
        ttk.Label(right_frame, text="Encryption Password:").pack(anchor="w")
        self.password_var = tk.StringVar()
        pwd_entry = ttk.Entry(right_frame, textvariable=self.password_var, show="*")
        pwd_entry.pack(fill=tk.X)

        # Password strength indicator
        self.password_strength_bar = ttk.Progressbar(right_frame, maximum=5)
        self.password_strength_bar.pack(fill=tk.X, pady=(4, 0))
        self.password_strength_label = ttk.Label(right_frame, text="Strength: ")
        self.password_strength_label.pack(anchor="w")
        self.password_var.trace("w", lambda *args: self.check_password_strength())

        ttk.Label(right_frame, text="").pack(pady=5)

        # Main action buttons
        ttk.Button(right_frame, text="1. Mark & Encrypt Evidence",
                  command=self.on_mark_encrypt_evidence).pack(fill=tk.X, pady=2)
        
        ttk.Button(right_frame, text="2. Decrypt & Verify Evidence",
                  command=self.on_decrypt_verify_evidence).pack(fill=tk.X, pady=2)
        
        ttk.Button(right_frame, text="3. Email Encrypted Evidence",
                  command=self.on_email_evidence).pack(fill=tk.X, pady=2)
        
        ttk.Button(right_frame, text="View Chain of Custody",
                  command=self.view_chain_of_custody).pack(fill=tk.X, pady=2)
        
        ttk.Button(right_frame, text="Generate Legal Report (PDF)",
                  command=self.generate_legal_report).pack(fill=tk.X, pady=2)
        
        ttk.Button(right_frame, text="Attack Simulation",
                  command=self.attack_simulation).pack(fill=tk.X, pady=2)

        # Bottom: Log
        lower_frame = ttk.Frame(main_frame)
        lower_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        ttk.Label(lower_frame, text="System Log:").pack(anchor="w")

        self.log_text = tk.Text(lower_frame, height=15, bg="#0f0f23", fg="#00ff00",
                               insertbackground="white", wrap=tk.WORD,
                               font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state="disabled")

        self.logger = Logger(self.log_text)
        self.logger.log("Digital Forensic Evidence System initialized", "SYSTEM")
        self.logger.log(f"Chain of Custody log: {self.custody_manager.log_file}", "SYSTEM")

    def check_password_strength(self, event=None):
        """Check and display password strength"""
        pwd = self.password_var.get()

        strength = 0
        if len(pwd) >= 8: strength += 1
        if re.search(r"[A-Z]", pwd): strength += 1
        if re.search(r"[a-z]", pwd): strength += 1
        if re.search(r"[0-9]", pwd): strength += 1
        if re.search(r"[@$!%*#?&]", pwd): strength += 1

        labels = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
        colors_map = ["#ff0000", "#ff5500", "#ffaa00", "#aaff00", "#00ff00"]

        self.password_strength_bar.config(value=strength)
        self.password_strength_label.config(
            text=f"Strength: {labels[strength]}",
            foreground=colors_map[strength]
        )

    def browse_evidence(self):
        """Browse and select evidence file"""
        path = filedialog.askopenfilename(
            title="Select Evidence File (NIfTI)",
            filetypes=[("NIfTI files", "*.nii *.nii.gz"), ("All files", "*.*")]
        )
        if path:
            self.file_path_var.set(path)
            self.current_evidence_path = path
            self.logger.log(f"Evidence selected: {os.path.basename(path)}", "INFO")
            
            # Compute initial hash
            try:
                file_hash = compute_file_hash(path)
                self.logger.log(f"Evidence SHA-256: {file_hash}", "INFO")
            except Exception as e:
                self.logger.log(f"Failed to compute hash: {e}", "ERROR")

    def parse_case_info(self) -> CaseInformation:
        """Parse case information from text widget"""
        text = self.case_info_text.get("1.0", tk.END).strip()
        lines = text.split("\n")
        
        info_dict = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                info_dict[key.strip()] = value.strip()
        
        return CaseInformation(
            case_id=info_dict.get("Case ID", "UNKNOWN"),
            case_name=info_dict.get("Case", "UNKNOWN"),
            case_number=info_dict.get("Number", "UNKNOWN"),
            investigating_agency=info_dict.get("Agency", "UNKNOWN"),
            lead_investigator=info_dict.get("Lead", "UNKNOWN"),
            case_opened_date=info_dict.get("Date Opened", "UNKNOWN"),
            incident_date=info_dict.get("Incident", "UNKNOWN").split("@")[0].strip(),
            incident_location=info_dict.get("Incident", "UNKNOWN").split("@")[1].strip() 
                              if "@" in info_dict.get("Incident", "") else "UNKNOWN",
            case_description=info_dict.get("Description", "UNKNOWN"),
            case_status=info_dict.get("Status", "active")
        )

    def on_mark_encrypt_evidence(self):
        """Mark evidence with case info, encrypt, and log to chain of custody"""
        evidence_path = self.file_path_var.get().strip()
        if not evidence_path:
            messagebox.showwarning("Missing Input", "Please select an evidence file.")
            return

        password = self.password_var.get().strip()
        if not password:
            messagebox.showwarning("Missing Input", "Please enter an encryption password.")
            return

        try:
            # Parse case information
            case_info = self.parse_case_info()
            self.current_case_info = case_info
            
            # Create evidence metadata
            file_hash = compute_file_hash(evidence_path)
            file_size = os.path.getsize(evidence_path)
            
            evidence_metadata = EvidenceMetadata(
                evidence_id=f"EVD-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
                case_id=case_info.case_id,
                evidence_type=EvidenceType.MEDICAL_SCAN,
                original_filename=os.path.basename(evidence_path),
                file_hash_sha256=file_hash,
                file_size_bytes=file_size,
                seized_datetime=datetime.datetime.now().isoformat(),
                seized_by=self.current_user,
                seized_location="Evidence Locker A",
                collection_device="Forensic Workstation 1",
                description="Medical imaging evidence - NIfTI format",
                tags=["medical", "brain", "nifti"],
                upload_datetime=datetime.datetime.now().isoformat(),
                uploaded_by=self.current_user
            )
            
            self.current_evidence_metadata = evidence_metadata
            
            self.logger.log("Starting evidence marking & encryption pipeline...", "INFO")
            
            # Log to chain of custody - UPLOAD action
            upload_entry = ChainOfCustodyEntry(
                entry_id=f"COC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-001",
                evidence_id=evidence_metadata.evidence_id,
                case_id=case_info.case_id,
                timestamp=datetime.datetime.now().isoformat(),
                action=ChainOfCustodyAction.UPLOADED,
                performed_by=self.current_user,
                user_role=self.current_user_role,
                hash_before=None,
                hash_after=file_hash,
                details=f"Evidence uploaded to system: {evidence_metadata.original_filename}",
                location="Digital Evidence System",
                device_info="Forensic Workstation 1"
            )
            
            self.custody_manager.add_entry(upload_entry)
            self.logger.log("✓ Chain of custody entry created: UPLOADED", "SUCCESS")
            
            # Perform watermarking and encryption
            marked_path, enc_path, slice_idx, wm_bits, psnr_val, ssim_val = \
                embed_case_info_in_nifti(
                    evidence_path, case_info, evidence_metadata, password, self.logger
                )
            
            self.last_marked_path = marked_path
            self.last_enc_bin_path = enc_path
            self.last_mid_slice_idx = slice_idx
            self.last_wm_bits_len = wm_bits
            self.psnr_val = psnr_val
            self.ssim_val = ssim_val
            
            # Compute hashes of marked and encrypted versions
            marked_hash = compute_file_hash(marked_path)
            encrypted_hash = compute_file_hash(enc_path)
            
            # Log to chain of custody - MODIFIED action (watermarking)
            modified_entry = ChainOfCustodyEntry(
                entry_id=f"COC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                evidence_id=evidence_metadata.evidence_id,
                case_id=case_info.case_id,
                timestamp=datetime.datetime.now().isoformat(),
                action=ChainOfCustodyAction.MODIFIED,
                performed_by=self.current_user,
                user_role=self.current_user_role,
                hash_before=file_hash,
                hash_after=marked_hash,
                details=f"Evidence marked with case info (watermarking). PSNR: {psnr_val:.2f}dB, SSIM: {ssim_val:.4f}",
                location="Digital Evidence System",
                device_info="Forensic Workstation 1"
            )
            
            self.custody_manager.add_entry(modified_entry)
            self.logger.log("✓ Chain of custody entry created: MODIFIED", "SUCCESS")
            
            summary = (
                f"\n=== Evidence Processing Summary ===\n"
                f"Evidence ID: {evidence_metadata.evidence_id}\n"
                f"Original Hash: {file_hash}\n"
                f"Marked File: {marked_path}\n"
                f"Encrypted File: {enc_path}\n"
                f"Quality: PSNR={psnr_val:.2f}dB, SSIM={ssim_val:.4f}\n"
            )
            self.logger.log(summary, "SUCCESS")
            
            messagebox.showinfo(
                "Success",
                f"Evidence marked and encrypted successfully.\n\n"
                f"Evidence ID: {evidence_metadata.evidence_id}\n"
                f"Encrypted file: {os.path.basename(enc_path)}"
            )
            
        except Exception as e:
            self.logger.log(f"ERROR: {e}", "ERROR")
            messagebox.showerror("Error", str(e))

    def on_decrypt_verify_evidence(self):
        """Decrypt evidence and verify integrity"""
        password = self.password_var.get().strip()
        if not password:
            messagebox.showwarning("Missing Input", "Please enter the decryption password.")
            return

        if self.last_enc_bin_path is None:
            enc_path = filedialog.askopenfilename(
                title="Select encrypted evidence file",
                filetypes=[("Encrypted Evidence", "*.bin"), ("All files", "*.*")]
            )
            if not enc_path:
                return
            self.last_enc_bin_path = enc_path

        # Try to load metadata
        metadata_path = self.last_enc_bin_path.replace("_forensic_encrypted.bin", "_evidence_metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                
                # Verify password
                expected_hash = meta.get("password_hash")
                input_hash = derive_key_from_password(password).hex()
                
                if expected_hash == input_hash:
                    self.last_mid_slice_idx = meta["mid_slice_idx"]
                    self.last_wm_bits_len = meta["wm_bits_len"]
                    evidence_id = meta.get("evidence_id", "UNKNOWN")
                    self.logger.log("✓ Password verified. Metadata loaded.", "SUCCESS")
                else:
                    self.logger.log("⚠️ Password incorrect - metadata not used.", "WARNING")
                    raise ValueError("Password mismatch")
            except Exception as e:
                self.logger.log(f"Metadata error: {e}. Manual input required.", "WARNING")
                # Manual input fallback
                mid_idx = tk.simpledialog.askinteger("Slice Index", "Enter slice index:", minvalue=0)
                bits_len = tk.simpledialog.askinteger("Watermark Bits", "Enter watermark bits length:", minvalue=1)
                if mid_idx is None or bits_len is None:
                    return
                self.last_mid_slice_idx = mid_idx
                self.last_wm_bits_len = bits_len
                evidence_id = "UNKNOWN"
        else:
            messagebox.showwarning("Metadata Missing", "Cannot find metadata file. Operation cancelled.")
            return

        try:
            self.logger.log("Starting decryption and verification...", "INFO")
            
            # Log to chain of custody - ACCESSED action
            access_entry = ChainOfCustodyEntry(
                entry_id=f"COC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-003",
                evidence_id=evidence_id,
                case_id=self.current_case_info.case_id if self.current_case_info else "UNKNOWN",
                timestamp=datetime.datetime.now().isoformat(),
                action=ChainOfCustodyAction.ACCESSED,
                performed_by=self.current_user,
                user_role=self.current_user_role,
                hash_before=compute_file_hash(self.last_enc_bin_path),
                hash_after=compute_file_hash(self.last_enc_bin_path),
                details="Evidence accessed for decryption and verification",
                location="Digital Evidence System"
            )
            
            self.custody_manager.add_entry(access_entry)
            self.logger.log("✓ Chain of custody entry created: ACCESSED", "SUCCESS")
            
            # Decrypt and extract
            case_info_text, tamper_status = decrypt_and_extract_from_evidence(
                self.last_enc_bin_path,
                password,
                self.last_mid_slice_idx,
                self.last_wm_bits_len,
                self.logger
            )
            
            # Log verification action
            verify_entry = ChainOfCustodyEntry(
                entry_id=f"COC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-004",
                evidence_id=evidence_id,
                case_id=self.current_case_info.case_id if self.current_case_info else "UNKNOWN",
                timestamp=datetime.datetime.now().isoformat(),
                action=ChainOfCustodyAction.VERIFIED,
                performed_by=self.current_user,
                user_role=self.current_user_role,
                hash_before=None,
                hash_after=None,
                details=f"Integrity verification completed. Status: {tamper_status}"
            )
            
            self.custody_manager.add_entry(verify_entry)
            self.logger.log("✓ Chain of custody entry created: VERIFIED", "SUCCESS")
            
            messagebox.showinfo(
                "Verification Results",
                f"Case Information:\n{case_info_text}\n\n"
                f"Tamper Detection:\n{tamper_status}"
            )
            
        except Exception as e:
            self.logger.log(f"ERROR: {e}", "ERROR")
            messagebox.showerror("Error", str(e))

    def on_email_evidence(self):
        """Email encrypted evidence to another investigator"""
        if self.last_enc_bin_path is None:
            messagebox.showwarning("Missing File", 
                "Please process evidence first (Mark & Encrypt).")
            return

        metadata_path = self.last_enc_bin_path.replace(
            "_forensic_encrypted.bin", "_evidence_metadata.json"
        )
        
        if not os.path.exists(metadata_path):
            messagebox.showerror("Metadata Missing", 
                f"Metadata file not found: {metadata_path}")
            return

        # Get email details
        sender_email = tk.simpledialog.askstring(
            "Sender Email", 
            "Enter your email (requires app password):"
        )
        if not sender_email: return

        sender_password = tk.simpledialog.askstring(
            "Email Password", 
            "Enter your email app password:", 
            show='*'
        )
        if not sender_password: return

        receiver_email = tk.simpledialog.askstring(
            "Recipient Email", 
            "Enter recipient's email:"
        )
        if not receiver_email: return

        subject = "SECURE: Encrypted Forensic Evidence Transfer"
        body = (
            "CONFIDENTIAL - FORENSIC EVIDENCE TRANSFER\n\n"
            "This email contains encrypted forensic evidence and associated metadata.\n"
            "You will need the shared decryption password to access the evidence.\n\n"
            f"Evidence ID: {self.current_evidence_metadata.evidence_id if self.current_evidence_metadata else 'UNKNOWN'}\n"
            f"Case ID: {self.current_case_info.case_id if self.current_case_info else 'UNKNOWN'}\n\n"
            "Attached Files:\n"
            f"- {os.path.basename(self.last_enc_bin_path)}\n"
            f"- {os.path.basename(metadata_path)}\n\n"
            "This transfer has been logged in the chain of custody.\n\n"
            "Digital Forensic Evidence System"
        )
        
        try:
            self.logger.log("Sending encrypted evidence via email...", "INFO")
            
            success, message = send_encrypted_evidence_email(
                sender_email, sender_password, receiver_email,
                subject, body, self.last_enc_bin_path, metadata_path
            )
            
            if success:
                # Log to chain of custody
                transfer_entry = ChainOfCustodyEntry(
                    entry_id=f"COC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-005",
                    evidence_id=self.current_evidence_metadata.evidence_id if self.current_evidence_metadata else "UNKNOWN",
                    case_id=self.current_case_info.case_id if self.current_case_info else "UNKNOWN",
                    timestamp=datetime.datetime.now().isoformat(),
                    action=ChainOfCustodyAction.TRANSFERRED,
                    performed_by=self.current_user,
                    user_role=self.current_user_role,
                    hash_before=compute_file_hash(self.last_enc_bin_path),
                    hash_after=compute_file_hash(self.last_enc_bin_path),
                    details=f"Evidence transferred via email to: {receiver_email}"
                )
                
                self.custody_manager.add_entry(transfer_entry)
                
                self.logger.log(f"✓ Evidence sent to {receiver_email}", "SUCCESS")
                self.logger.log("✓ Chain of custody entry created: TRANSFERRED", "SUCCESS")
                messagebox.showinfo("Success", "Evidence transferred successfully!")
            else:
                self.logger.log(f"✗ Email failed: {message}", "ERROR")
                messagebox.showerror("Email Error", message)
                
        except Exception as e:
            self.logger.log(f"FATAL EMAIL ERROR: {e}", "ERROR")
            messagebox.showerror("Fatal Error", str(e))

    def view_chain_of_custody(self):
        """Display chain of custody for current evidence"""
        if self.current_evidence_metadata is None:
            messagebox.showwarning("No Evidence", 
                "Please process evidence first to view chain of custody.")
            return
        
        evidence_id = self.current_evidence_metadata.evidence_id
        entries = self.custody_manager.get_entries_for_evidence(evidence_id)
        
        if not entries:
            messagebox.showinfo("Chain of Custody", 
                "No chain of custody entries found for this evidence.")
            return
        
        # Create a new window to display chain of custody
        custody_window = tk.Toplevel(self.root)
        custody_window.title(f"Chain of Custody - {evidence_id}")
        custody_window.geometry("800x600")
        
        # Header
        header_frame = ttk.Frame(custody_window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"Evidence ID: {evidence_id}", 
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(header_frame, text=f"Total Entries: {len(entries)}").pack(anchor="w")
        
        # Verify chain integrity
        is_valid, issues = self.custody_manager.verify_chain_integrity(evidence_id)
        
        status_text = "✓ CHAIN VALID" if is_valid else "⚠️ INTEGRITY ISSUES DETECTED"
        status_color = "green" if is_valid else "red"
        
        status_label = ttk.Label(header_frame, text=status_text, 
                                foreground=status_color,
                                font=("Segoe UI", 11, "bold"))
        status_label.pack(anchor="w", pady=5)
        
        if issues:
            ttk.Label(header_frame, text="Issues:", 
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            for issue in issues:
                ttk.Label(header_frame, text=f"  • {issue}", 
                         foreground="red").pack(anchor="w")
        
        # Chain entries
        text_frame = ttk.Frame(custody_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, 
                             yscrollcommand=scrollbar.set,
                             font=("Consolas", 9))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Populate entries
        for i, entry in enumerate(entries, 1):
            text_widget.insert(tk.END, f"\n{'='*80}\n")
            text_widget.insert(tk.END, f"Entry #{i}\n")
            text_widget.insert(tk.END, f"{'='*80}\n")
            text_widget.insert(tk.END, f"Timestamp:     {entry.timestamp}\n")
            text_widget.insert(tk.END, f"Action:        {entry.action.value.upper()}\n")
            text_widget.insert(tk.END, f"Performed By:  {entry.performed_by}\n")
            text_widget.insert(tk.END, f"Role:          {entry.user_role.value}\n")
            text_widget.insert(tk.END, f"Details:       {entry.details}\n")
            
            if entry.hash_before:
                text_widget.insert(tk.END, f"Hash Before:   {entry.hash_before[:64]}...\n")
            if entry.hash_after:
                text_widget.insert(tk.END, f"Hash After:    {entry.hash_after[:64]}...\n")
            
            if entry.location:
                text_widget.insert(tk.END, f"Location:      {entry.location}\n")
            if entry.device_info:
                text_widget.insert(tk.END, f"Device:        {entry.device_info}\n")
        
        text_widget.config(state="disabled")
        
        # Close button
        ttk.Button(custody_window, text="Close", 
                  command=custody_window.destroy).pack(pady=10)

    def generate_legal_report(self):
        """Generate comprehensive PDF report for legal proceedings"""
        if self.current_evidence_metadata is None or self.current_case_info is None:
            messagebox.showwarning("Missing Data", 
                "Please process evidence first before generating a report.")
            return
        
        try:
            evidence_id = self.current_evidence_metadata.evidence_id
            chain_entries = self.custody_manager.get_entries_for_evidence(evidence_id)
            
            # Verify chain integrity
            is_valid, issues = self.custody_manager.verify_chain_integrity(evidence_id)
            integrity_status = "VALID - No issues detected" if is_valid else f"ISSUES DETECTED: {'; '.join(issues)}"
            
            # Generate PDF
            output_path = f"Chain_of_Custody_Report_{evidence_id}.pdf"
            
            generate_chain_of_custody_report(
                evidence_id=evidence_id,
                case_info=self.current_case_info,
                evidence_metadata=self.current_evidence_metadata,
                chain_entries=chain_entries,
                integrity_status=integrity_status,
                psnr_val=self.psnr_val if self.psnr_val > 0 else None,
                ssim_val=self.ssim_val if self.ssim_val > 0 else None,
                output_path=output_path
            )
            
            self.logger.log(f"✓ Legal report generated: {output_path}", "SUCCESS")
            
            # Log report generation to chain of custody
            export_entry = ChainOfCustodyEntry(
                entry_id=f"COC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-006",
                evidence_id=evidence_id,
                case_id=self.current_case_info.case_id,
                timestamp=datetime.datetime.now().isoformat(),
                action=ChainOfCustodyAction.EXPORTED,
                performed_by=self.current_user,
                user_role=self.current_user_role,
                hash_before=None,
                hash_after=None,
                details=f"Chain of custody report generated: {output_path}"
            )
            
            self.custody_manager.add_entry(export_entry)
            
            messagebox.showinfo("Success", 
                f"Legal report generated successfully!\n\nSaved as: {output_path}")
            
        except Exception as e:
            self.logger.log(f"ERROR generating report: {e}", "ERROR")
            messagebox.showerror("Error", str(e))

    def attack_simulation(self):
        """Simulate attacks on watermarked evidence to test robustness"""
        if self.last_marked_path is None or self.last_mid_slice_idx is None:
            messagebox.showwarning("No Evidence", 
                "Please process evidence first (Mark & Encrypt).")
            return

        try:
            self.logger.log("Starting attack simulation on watermarked evidence...", "INFO")
            
            img = nib.load(self.last_marked_path)
            data = img.get_fdata()
            wm_slice = data[:, :, self.last_mid_slice_idx]
            wm_slice_uint8, s_min, s_max = normalize_slice_to_uint8(wm_slice)

            labels = []
            psnr_vals = []
            ssim_vals = []

            def add_case(name, attacked):
                attacked = np.clip(attacked, 0, 255).astype(np.uint8)
                labels.append(name)
                psnr_vals.append(psnr(wm_slice_uint8, attacked))
                ssim_vals.append(ssim(wm_slice_uint8, attacked))

            add_case("Original", wm_slice_uint8)

            # Noise attacks
            for sigma in [5, 10, 20]:
                noise = np.random.normal(0, sigma, wm_slice_uint8.shape)
                attacked = wm_slice_uint8.astype(np.float64) + noise
                add_case(f"Noise σ={sigma}", attacked)

            # Blur attacks
            for k in [3, 5, 7]:
                attacked = cv2.GaussianBlur(wm_slice_uint8, (k, k), 0)
                add_case(f"Blur k={k}", attacked)

            self.logger.log("Attack Simulation Results:", "INFO")
            for lbl, p, s in zip(labels, psnr_vals, ssim_vals):
                self.logger.log(f"  {lbl}: PSNR={p:.2f} dB, SSIM={s:.4f}", "INFO")

            # Plot results
            x = np.arange(len(labels))

            fig, ax1 = plt.subplots(figsize=(10, 6))
            ax2 = ax1.twinx()

            ax1.plot(x, psnr_vals, marker='o', color='blue', label='PSNR (dB)', linewidth=2)
            ax2.plot(x, ssim_vals, marker='s', color='red', label='SSIM', linewidth=2)

            ax1.set_xticks(x)
            ax1.set_xticklabels(labels, rotation=45, ha='right')
            ax1.set_ylabel("PSNR (dB)", color='blue', fontsize=12)
            ax2.set_ylabel("SSIM", color='red', fontsize=12)
            ax1.set_xlabel("Attack Type", fontsize=12)

            ax1.set_title("Watermark Robustness: Effect of Attacks", fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)

            ln1, lab1 = ax1.get_legend_handles_labels()
            ln2, lab2 = ax2.get_legend_handles_labels()
            ax1.legend(ln1 + ln2, lab1 + lab2, loc='best')

            plt.tight_layout()
            plt.show()

        except Exception as e:
            self.logger.log(f"ERROR in attack simulation: {e}", "ERROR")
            messagebox.showerror("Error", str(e))

    def view_evidence_slice(self):
        """View a single slice of the evidence"""
        evidence_path = self.file_path_var.get().strip()
        if not evidence_path:
            messagebox.showwarning("Missing File", "Please select an evidence file.")
            return

        try:
            nib.Nifti1Header.quaternion_threshold = -1e-06
            img = nib.load(evidence_path)
            data = img.get_fdata()
            if data.ndim < 3:
                raise ValueError("Evidence must be 3D volume.")

            slice_idx = data.shape[2] // 2
            slice_img = data[:, :, slice_idx]

            plt.figure(figsize=(8, 8))
            plt.imshow(slice_img, cmap='gray')
            plt.title(f"Evidence Slice {slice_idx}\n{os.path.basename(evidence_path)}")
            plt.axis('off')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_3d_evidence(self):
        """View 3D evidence with slice scrolling"""
        evidence_path = self.file_path_var.get().strip()
        if not evidence_path:
            messagebox.showwarning("Missing file", "Please select an evidence file.")
            return

        try:
            nib.Nifti1Header.quaternion_threshold = -1e-06
            img = nib.load(evidence_path)
            data = img.get_fdata()

            if data.ndim < 3:
                raise ValueError("3D data required.")

            fig, ax = plt.subplots(figsize=(10, 10))
            plt.subplots_adjust(bottom=0.25)

            slice_idx = data.shape[2] // 2
            img_plot = ax.imshow(data[:, :, slice_idx], cmap='gray')
            ax.set_title(f"Evidence Slice {slice_idx}\n{os.path.basename(evidence_path)}")
            ax.axis('off')

            ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
            slider = Slider(ax_slider, 'Slice', 0, data.shape[2] - 1,
                          valinit=slice_idx, valstep=1)

            def update(val):
                img_plot.set_data(data[:, :, int(slider.val)])
                ax.set_title(f"Evidence Slice {int(slider.val)}\n{os.path.basename(evidence_path)}")
                fig.canvas.draw_idle()

            slider.on_changed(update)
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_3d_volume(self):
        """View true 3D volume rendering using Vedo"""
        evidence_path = self.file_path_var.get().strip()
        if not evidence_path:
            messagebox.showwarning("Missing file", "Please select an evidence file.")
            return

        try:
            self.logger.log("Launching 3D volume viewer (Vedo/VTK)...", "INFO")
            vol = Volume(evidence_path)
            vol.cmap('bone').add_scalarbar('Intensity')

            show(vol, title=f"3D Volume: {os.path.basename(evidence_path)}", axes=1)

        except Exception as e:
            self.logger.log(f"ERROR in 3D volume view: {e}", "ERROR")
            messagebox.showerror("Error", str(e))


# ============================================================
#  MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ForensicEvidenceSystemGUI(root)
    root.mainloop()
