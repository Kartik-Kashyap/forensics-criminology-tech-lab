import React from 'react';
import { Server, Database, Lock, Layers } from 'lucide-react';

export const SystemSpecs: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-12 pb-20">
      
      {/* Introduction */}
      <section className="border-l-4 border-[#00ff41] pl-6 py-2">
        <h2 className="text-3xl font-bold text-white mb-2">SYSTEM ARCHITECTURE</h2>
        <p className="text-gray-400 font-mono text-sm max-w-2xl">
          High-level overview of the CUSTODIAN-ZERO microservices architecture, enforcing strict separation of concerns between user interface, business logic, and forensic processing.
        </p>
      </section>

      {/* Tech Stack Table */}
      <section>
        <h3 className="text-xl font-bold text-[#00f3ff] mb-6 flex items-center gap-2">
          <Layers size={20} /> TECHNICAL STACK
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
           <div className="bg-[#0a0b10] border border-[#1a1a1a] p-6">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-4">Frontend Layer</h4>
              <ul className="space-y-2 text-sm font-mono text-gray-300">
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Framework</span> <span className="text-[#00ff41]">React 18 / Next.js</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Styling</span> <span className="text-[#00ff41]">Tailwind CSS</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>State</span> <span className="text-[#00ff41]">Zustand / React Query</span></li>
              </ul>
           </div>
           <div className="bg-[#0a0b10] border border-[#1a1a1a] p-6">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-4">Backend Core</h4>
              <ul className="space-y-2 text-sm font-mono text-gray-300">
                <li className="flex justify-between border-b border-[#222] pb-1"><span>API Gateway</span> <span className="text-[#00ff41]">NestJS (Node.js)</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Database</span> <span className="text-[#00ff41]">PostgreSQL 16</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Queue</span> <span className="text-[#00ff41]">Redis</span></li>
              </ul>
           </div>
           <div className="bg-[#0a0b10] border border-[#1a1a1a] p-6">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-4">Forensic Engine</h4>
              <ul className="space-y-2 text-sm font-mono text-gray-300">
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Service</span> <span className="text-[#00ff41]">Python (FastAPI)</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>AI Inference</span> <span className="text-[#00ff41]">Ollama (LLaMA 3.2)</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Tools</span> <span className="text-[#00ff41]">FFmpeg, Tesseract, ExifTool</span></li>
              </ul>
           </div>
           <div className="bg-[#0a0b10] border border-[#1a1a1a] p-6">
              <h4 className="text-xs font-bold text-gray-500 uppercase mb-4">Security</h4>
              <ul className="space-y-2 text-sm font-mono text-gray-300">
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Encryption (Rest)</span> <span className="text-[#00ff41]">AES-256-GCM</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Encryption (Transit)</span> <span className="text-[#00ff41]">TLS 1.3</span></li>
                <li className="flex justify-between border-b border-[#222] pb-1"><span>Hashing</span> <span className="text-[#00ff41]">SHA-256 + SHA-3</span></li>
              </ul>
           </div>
        </div>
      </section>

      {/* Database Schema */}
      <section>
        <h3 className="text-xl font-bold text-[#00f3ff] mb-6 flex items-center gap-2">
          <Database size={20} /> DATABASE SCHEMA
        </h3>
        <div className="bg-[#080808] border border-[#333] p-6 font-mono text-xs overflow-x-auto text-gray-400">
<pre>{`
Table: users
------------------------
id              UUID PK
username        VARCHAR
role_id         FK
public_key      TEXT (For signature verification)

Table: evidence
------------------------
id              UUID PK
case_id         UUID FK
current_hash    CHAR(64) (SHA-256)
integrity_state ENUM ('VERIFIED', 'TAMPERED')
storage_path    VARCHAR (Encrypted pointer)
encryption_key  UUID (Reference to KMS)

Table: custody_log
------------------------
id              UUID PK
evidence_id     UUID FK
actor_id        UUID FK
action          ENUM ('INTAKE', 'VIEW', 'EXPORT')
timestamp       TIMESTAMPTZ
prev_hash       CHAR(64) (Merkle Link)
curr_hash       CHAR(64) (Evidence state at time)
signature       TEXT (User Digital Sig)

Table: ai_reports
------------------------
id              UUID PK
evidence_id     UUID FK
model_version   VARCHAR
raw_output      JSONB
advisory_flag   BOOLEAN DEFAULT TRUE
`}</pre>
        </div>
      </section>

      {/* Security Model */}
      <section>
        <h3 className="text-xl font-bold text-[#00f3ff] mb-6 flex items-center gap-2">
          <Lock size={20} /> SECURITY & INFRASTRUCTURE
        </h3>
        <div className="space-y-4">
           <div className="border-l-2 border-[#ff003c] pl-4">
              <h4 className="text-white font-bold text-sm">ZERO TRUST PRINCIPLE</h4>
              <p className="text-xs text-gray-500 mt-1">
                The AI Service is isolated in a restricted Docker network with NO internet access. 
                It communicates only with the Backend API via Redis Queue.
              </p>
           </div>
           <div className="border-l-2 border-[#ff003c] pl-4">
              <h4 className="text-white font-bold text-sm">ENCRYPTION STRATEGY</h4>
              <p className="text-xs text-gray-500 mt-1">
                Files are streamed through a crypto-transform stream (Node.js `crypto` module). 
                Raw files never touch the disk unencrypted. Keys are managed per-case.
              </p>
           </div>
           <div className="border-l-2 border-[#ff003c] pl-4">
              <h4 className="text-white font-bold text-sm">IMMUTABILITY</h4>
              <p className="text-xs text-gray-500 mt-1">
                The `custody_log` table operates as an append-only ledger. Database user permissions 
                prevent `UPDATE` or `DELETE` on this specific table.
              </p>
           </div>
        </div>
      </section>

       {/* Folder Structure */}
       <section>
        <h3 className="text-xl font-bold text-[#00f3ff] mb-6 flex items-center gap-2">
          <Server size={20} /> REPO STRUCTURE
        </h3>
        <div className="bg-[#080808] border border-[#333] p-6 font-mono text-xs overflow-x-auto text-gray-400">
<pre>{`
/monorepo-root
├── apps
│   ├── web (Next.js Frontend)
│   └── api (NestJS Backend Gateway)
├── services
│   ├── forensic-engine (Python/FastAPI)
│   └── audit-logger (Go Microservice)
├── packages
│   ├── shared-types
│   └── crypto-utils
├── infrastructure
│   ├── docker-compose.yml
│   └── k8s-manifests
├── docs
└── scripts
    ├── rotate-keys.sh
    └── verify-hashes.sh
`}</pre>
        </div>
      </section>

    </div>
  );
};
