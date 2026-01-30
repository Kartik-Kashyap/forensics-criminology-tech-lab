import React, { useState, useCallback } from 'react';
import { Upload, File, Lock, ShieldAlert, CheckCircle } from 'lucide-react';

export const EvidenceIntake: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileHash, setFileHash] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const simulateProcessing = (selectedFile: File) => {
    setFile(selectedFile);
    setProcessing(true);
    setProgress(0);
    setFileHash(null);

    // Simulate hashing and encryption process
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += 5;
      setProgress(currentProgress);
      if (currentProgress >= 100) {
        clearInterval(interval);
        setProcessing(false);
        // Mock SHA-256 hash
        setFileHash('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'); 
      }
    }, 100);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      simulateProcessing(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      simulateProcessing(e.target.files[0]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 border-l-2 border-[#00ff41] pl-4">
        <h2 className="text-2xl font-bold text-white mb-1">SECURE EVIDENCE INTAKE</h2>
        <p className="text-sm text-gray-500">
          Files are hashed (SHA-256), encrypted (AES-256-GCM), and timestamped immediately upon ingestion.
        </p>
      </div>

      <div 
        className={`relative border-2 border-dashed h-64 flex flex-col items-center justify-center transition-all duration-300
          ${dragActive ? 'border-[#00ff41] bg-[#00ff41]/5' : 'border-[#333] bg-[#0a0a0a]'}
          ${processing ? 'pointer-events-none opacity-50' : 'cursor-pointer hover:border-gray-500'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
          onChange={handleChange}
          disabled={processing}
        />
        
        {!file && (
          <div className="text-center">
            <Upload size={48} className={`mx-auto mb-4 ${dragActive ? 'text-[#00ff41]' : 'text-gray-600'}`} />
            <p className="text-gray-300 font-bold">DRAG & DROP EVIDENCE ARTIFACTS</p>
            <p className="text-xs text-gray-600 mt-2">Supports: DD/RAW, MP4, JPEG, PDF, LOG</p>
            <p className="text-[10px] text-[#00ff41] mt-4 font-mono">SECURE_PROTOCOL_V4_ACTIVE</p>
          </div>
        )}

        {file && (
          <div className="text-center w-full px-12">
             <div className="flex items-center justify-center gap-3 mb-4 text-[#00f3ff]">
                <File size={32} />
                <span className="text-lg font-mono">{file.name}</span>
             </div>
             
             {processing && (
               <div className="w-full bg-[#111] h-2 rounded-full overflow-hidden border border-[#333]">
                 <div 
                   className="bg-[#00f3ff] h-full transition-all duration-100 ease-out"
                   style={{ width: `${progress}%` }}
                 />
               </div>
             )}
             
             {processing && (
                <div className="flex justify-between text-[10px] mt-2 font-mono text-gray-500">
                  <span>GENERATING_HASH_SHA256...</span>
                  <span>ENCRYPTING_AES_GCM...</span>
                </div>
             )}
          </div>
        )}
      </div>

      {/* Post-Upload Report */}
      {fileHash && (
        <div className="mt-8 bg-[#0a0a0a] border border-[#333] p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity">
            <ShieldAlert className="text-[#00ff41]" size={48} />
          </div>
          
          <div className="flex items-center gap-2 text-[#00ff41] mb-4">
             <CheckCircle size={18} />
             <span className="font-bold tracking-wider">INTAKE SUCCESSFUL</span>
          </div>

          <div className="grid grid-cols-2 gap-6 text-sm font-mono">
            <div>
              <span className="block text-gray-600 text-[10px] uppercase">Original Filename</span>
              <span className="text-white">{file?.name}</span>
            </div>
            <div>
              <span className="block text-gray-600 text-[10px] uppercase">File Size</span>
              <span className="text-white">{(file?.size || 0 / 1024).toFixed(2)} KB</span>
            </div>
            <div className="col-span-2">
              <span className="block text-gray-600 text-[10px] uppercase">SHA-256 HASH (IMMUTABLE ID)</span>
              <span className="text-[#00f3ff] break-all">{fileHash}</span>
            </div>
            <div>
              <span className="block text-gray-600 text-[10px] uppercase">Encryption Key ID</span>
              <span className="text-white flex items-center gap-2">
                <Lock size={12} className="text-[#00ff41]"/> 
                KEY-{Math.floor(Math.random()*10000)}-SECURE
              </span>
            </div>
            <div>
              <span className="block text-gray-600 text-[10px] uppercase">Timestamp (UTC)</span>
              <span className="text-white">{new Date().toISOString()}</span>
            </div>
          </div>

          <div className="mt-6 border-t border-[#1a1a1a] pt-4 flex gap-3">
             <button className="bg-[#00ff41] hover:bg-[#00cc33] text-black px-4 py-2 text-xs font-bold uppercase tracking-wider">
               Commit to Custody Log
             </button>
             <button className="border border-[#333] hover:border-white text-gray-300 px-4 py-2 text-xs font-bold uppercase tracking-wider">
               Discard & Wipe
             </button>
          </div>
        </div>
      )}
    </div>
  );
};
