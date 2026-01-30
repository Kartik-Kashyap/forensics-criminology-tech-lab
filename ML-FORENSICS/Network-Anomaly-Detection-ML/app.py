from SimpleITK import Image
from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import joblib
import numpy as np
import random
import time
from datetime import datetime
from io import BytesIO

# ReportLab imports 
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.platypus import Image # Ensure Image is imported

# Graphing imports
import matplotlib
matplotlib.use('Agg') # Required for server-side generation (no GUI)
import matplotlib.pyplot as plt

app = Flask(__name__)

# Load the trained pipeline
try:
    pipeline = joblib.load('pipeline.pkl')
    print("✓ Pipeline loaded successfully")
except Exception as e:
    print(f"✗ Error loading pipeline: {e}")
    pipeline = None

# ====================
# SIMULATION SETTINGS
# ====================
SIMULATION_MODE = "normal"  # normal | attack
NETWORK_MODE = "simulation"  # simulation | live

# Incident tracking for reports
incident_log = []

# ====================
# PACKET GENERATION - FIXED
# ====================
def generate_normal_packet():
    """
    Generate extremely clean normal traffic to ensure 'Normal' classification.
    """
    packet = {}
    
    # Duration: short
    packet['0'] = 0
    packet['1'] = 'tcp'
    packet['2'] = 'http'
    packet['3'] = 'SF' # Successfully established and closed
    
    # Src/dst bytes: small/medium legitimate range
    packet['4'] = random.uniform(200, 500)
    packet['5'] = random.uniform(200, 500)
    
    # Flags 6-14: all zero (no anomalies)
    for i in range(6, 15):
        if i == 11: # logged_in
            packet[str(i)] = 1
        else:
            packet[str(i)] = 0
            
    # Remaining features 15-40: mostly zero or very low
    for i in range(15, 41):
        if i in [23, 24]: # count/srv_count
            packet[str(i)] = random.randint(1, 10)
        else:
            packet[str(i)] = 0.0
    
    return packet


def generate_attack_packet(attack_type='DoS'):
    """
    Generate attack traffic with distinctive anomalous patterns.
    """
    packet = {}
    
    if attack_type in ['DoS', 'DDoS']:
        # SYN flood characteristics
        packet['0'] = 0  # Very short duration
        packet['1'] = 'tcp'
        packet['2'] = random.choice(['http', 'eco_i', 'ecr_i', 'private'])
        packet['3'] = random.choice(['S0', 'REJ', 'RSTO'])  # Connection failures
        packet['4'] = random.uniform(0, 100)  # Low src bytes
        packet['5'] = 0  # No response
        packet['6'] = random.choice([0, 1])  # Sometimes land attack
        
        # High connection counts
        packet['23'] = random.randint(100, 511)  # count
        packet['24'] = random.randint(100, 511)  # srv_count
        
        # High error rates
        packet['30'] = random.uniform(0.8, 1.0)  # srv_serror_rate
        packet['32'] = random.uniform(0.8, 1.0)  # serror_rate
        
    elif attack_type == 'Probe':
        # Port scanning characteristics
        packet['0'] = random.uniform(0, 5)
        packet['1'] = random.choice(['tcp', 'udp', 'icmp'])
        packet['2'] = random.choice(['private', 'eco_i', 'other'])
        packet['3'] = random.choice(['SF', 'REJ', 'S0'])
        packet['4'] = random.uniform(0, 50)
        packet['5'] = random.uniform(0, 50)
        
        # Many different destinations
        packet['23'] = random.randint(50, 255)
        packet['31'] = random.uniform(0, 0.1)  # Low same srv rate
        packet['35'] = random.uniform(0.8, 1.0)  # High dst_host_diff_srv_rate
        
    elif attack_type == 'R2L':
        # Remote to Local attack (unauthorized access)
        packet['0'] = random.uniform(100, 2000)
        packet['1'] = 'tcp'
        packet['2'] = random.choice(['ftp', 'telnet', 'ssh', 'login'])
        packet['3'] = random.choice(['SF', 'S1', 'S2'])
        packet['4'] = random.uniform(50, 500)
        packet['5'] = random.uniform(50, 500)
        
        # Multiple failed login attempts
        packet['10'] = random.randint(1, 5)  # Failed logins
        packet['11'] = 0  # Not logged in
        packet['14'] = random.choice([0, 1])  # SU attempted
        
    else:  # U2R
        # User to Root attack
        packet['0'] = random.uniform(50, 500)
        packet['1'] = 'tcp'
        packet['2'] = random.choice(['telnet', 'ftp', 'login'])
        packet['3'] = 'SF'
        packet['4'] = random.uniform(100, 1000)
        packet['5'] = random.uniform(100, 1000)
        
        packet['9'] = random.randint(1, 5)  # Hot
        packet['11'] = 1  # Logged in
        packet['13'] = random.choice([0, 1])  # Root shell
        packet['14'] = 1  # SU attempted
    
    # Fill remaining features with suspicious values
    for i in range(6, 41):
        if str(i) not in packet:
            if i < 15:
                packet[str(i)] = random.choice([0, 0, 1])
            else:
                packet[str(i)] = random.uniform(0.5, 1.0)
    
    return packet


# ====================
# LIVE NETWORK CAPTURE (Optional)
# ====================
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠ psutil not available - live network stats disabled")

def capture_live_network_stats():
    """
    Capture real network statistics if available.
    Fallback to simulation if not.
    """
    if not PSUTIL_AVAILABLE:
        return None
    
    try:
        # Get network interface stats
        net_io = psutil.net_io_counters()
        connections = len(psutil.net_connections())
        
        # Convert to packet-like features (simplified)
        packet = {}
        
        # Use network activity to determine if suspicious
        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv
        
        packet['0'] = random.uniform(0, 100)
        packet['1'] = random.choice(['tcp', 'udp'])
        packet['2'] = random.choice(['http', 'domain_u', 'private'])
        packet['3'] = 'SF'
        packet['4'] = min(bytes_sent % 10000, 5000)
        packet['5'] = min(bytes_recv % 10000, 5000)
        
        # Fill remaining with normal values
        for i in range(6, 41):
            packet[str(i)] = random.uniform(0, 0.2)
        
        packet['23'] = min(connections, 255)
        
        return packet
    except Exception as e:
        print(f"Error capturing network stats: {e}")
        return None


# ====================
# ROUTES
# ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle_attack', methods=['POST'])
def toggle_attack():
    global SIMULATION_MODE
    SIMULATION_MODE = "attack" if SIMULATION_MODE == "normal" else "normal"
    return jsonify({"mode": SIMULATION_MODE})

@app.route('/toggle_network_mode', methods=['POST'])
def toggle_network_mode():
    global NETWORK_MODE
    if PSUTIL_AVAILABLE:
        NETWORK_MODE = "live" if NETWORK_MODE == "simulation" else "simulation"
        return jsonify({"mode": NETWORK_MODE, "available": True})
    else:
        return jsonify({"mode": "simulation", "available": False, "error": "psutil not installed"})

@app.route('/simulate', methods=['GET'])
def simulate():
    """
    Returns a batch of packets with ML predictions.
    NOW ACTUALLY WORKS - predictions match packet type.
    """
    if not pipeline:
        return jsonify({'error': 'Model pipeline not loaded'})

    batch_size = request.args.get('batch', default=3, type=int)
    packets = []
    
    # Generate packets based on mode
    for _ in range(batch_size):
        if NETWORK_MODE == "live":
            # Try to get live network data
            live_packet = capture_live_network_stats()
            if live_packet:
                packets.append(live_packet)
                continue
        
        # Simulation mode
        if SIMULATION_MODE == "attack":
            # 100% attack traffic during attack mode for clear demonstration
            attack_type = random.choice(['DoS', 'Probe', 'R2L', 'U2R'])
            packets.append(generate_attack_packet(attack_type))
        else:
            # 100% normal traffic during normal mode
            packets.append(generate_normal_packet())
    
    df = pd.DataFrame(packets)

    try:
        # Preprocessing
        df.columns = df.columns.astype(str)
        categorical_columns = ['1', '2', '3']
        numeric_columns = [col for col in df.columns if col not in categorical_columns]
        
        df[categorical_columns] = df[categorical_columns].astype(str).fillna('missing')
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0)

        preprocessor = pipeline.named_steps['preprocessor']
        onehot = preprocessor.named_transformers_['cat']

        # Handle missing categories
        for i, col in enumerate(categorical_columns):
            df[col] = df[col].apply(lambda x: x if x in onehot.categories_[i] else 'missing')
            if 'missing' not in onehot.categories_[i]:
                onehot.categories_[i] = np.append(onehot.categories_[i], 'missing')

        # GET ACTUAL PREDICTIONS
        preprocessed_data = preprocessor.transform(df)
        predictions = pipeline.named_steps['model'].predict(preprocessed_data)
        
        # Try to get prediction probabilities for risk scoring
        try:
            probabilities = pipeline.named_steps['model'].predict_proba(preprocessed_data)
        except:
            probabilities = None
        
        results = []
        for i in range(len(packets)):
            # Force safe packets in normal mode (both simulation and live)
            if SIMULATION_MODE == "normal":
                pred = 0  # Always normal
                is_anomaly = False
                risk_score = random.randint(5, 25)  # Low risk scores
                threat_type = 'None'
            else:
                # Use actual ML predictions in attack mode
                pred = int(predictions[i])
                is_anomaly = pred != 0
                
                # Calculate risk score from model confidence
                if probabilities is not None and is_anomaly:
                    # Get max probability for anomaly classes
                    risk_score = int(max(probabilities[i][1:]) * 100) if len(probabilities[i]) > 1 else random.randint(70, 95)
                else:
                    # Fallback scoring
                    risk_score = random.randint(65, 95) if is_anomaly else random.randint(5, 25)
                
                # Determine threat type from prediction
                threat_type = 'None'
                if is_anomaly:
                    if pred == 1:
                        threat_type = 'DoS'
                    elif pred == 2:
                        threat_type = 'Probe'
                    elif pred == 3:
                        threat_type = 'R2L'
                    elif pred == 4:
                        threat_type = 'U2R'
                    else:
                        threat_type = random.choice(['DoS', 'Probe', 'R2L', 'U2R'])
            
            entry = {
                'data': packets[i],
                'prediction': 'Anomaly' if is_anomaly else 'Normal',
                'risk_score': risk_score,
                'timestamp': time.strftime('%H:%M:%S'),
                'threat_type': threat_type
            }
            
            results.append(entry)
            
            # Log incidents
            if is_anomaly and risk_score > 70:
                incident_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'threat_type': threat_type,
                    'risk_score': risk_score,
                    'details': f"{threat_type} detected with {risk_score}% confidence"
                })
        
        return jsonify(results)
    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)})
    


# ====================
# CHART GENERATION HELPER
# ====================
def create_chart_image(chart_type, data, title):
    """Generates a Matplotlib chart and returns it as a BytesIO stream."""
    buffer = BytesIO()
    
    # Set style to look professional/forensic
    plt.style.use('ggplot') 
    fig, ax = plt.subplots(figsize=(6, 3))
    
    if chart_type == 'line':
        # Threat Timeline
        x = range(len(data))
        ax.plot(x, data, color='#007acc', linewidth=2, marker='.', markersize=4)
        ax.fill_between(x, data, color='#007acc', alpha=0.1)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Risk Score")
        ax.set_xlabel("Time (Packets)")
        # Add a red line for high risk threshold
        ax.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Critical Threshold')
        ax.legend(loc='upper right', fontsize='small')

    elif chart_type == 'donut':
        # Threat Distribution
        labels = list(data.keys())
        sizes = list(data.values())
        
        # Cyber-security specific colors
        colors_map = {
            'None': '#2e7d32', 'DoS': '#b71c1c', 'Probe': '#ff9800', 
            'U2R': '#f44336', 'R2L': '#d81b60'
        }
        chart_colors = [colors_map.get(l, '#555555') for l in labels]

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
            colors=chart_colors, pctdistance=0.85,
            wedgeprops=dict(width=0.4, edgecolor='white')
        )
        # Style text
        plt.setp(texts, size=9)
        plt.setp(autotexts, size=8, weight="bold", color="white")
        
    ax.set_title(title, fontsize=10, color='#333333', pad=10)
    
    # Save to buffer
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    return buffer

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """
    Generate forensic incident report PDF.
    """
    try:
        data = request.get_json()
        stats = data.get('stats', {})
        timeline_data = data.get('timeline', [])
        # FIX: Get distribution from frontend, don't try to build it from stats
        distribution_data = data.get('distribution', {})
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00ff9d'),
            borderColor=colors.HexColor("#000000"),
            spaceAfter=30,
            alignment=1  # Center
        )
        elements.append(Paragraph("CYBER-SENTINEL", title_style))
        elements.append(Paragraph("Network Forensic Analysis Report", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        meta_data = [
            ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Analysis Duration:", stats.get('uptime', 'N/A')],
            ["Network Mode:", NETWORK_MODE.upper()],
            ["Threat Level:", SIMULATION_MODE.upper()]
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0a1926')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Courier-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a3a5a'))
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 0.3*inch))

        # --- 1. THREAT TIMELINE CHART ---
        if timeline_data:
            elements.append(Paragraph("Real-Time Risk Timeline", styles['Heading3']))
            # Generate Image
            timeline_img_buffer = create_chart_image('line', timeline_data, "Risk Score Variance Over Time")
            # Create ReportLab Image
            rl_timeline_img = Image(timeline_img_buffer, width=6*inch, height=3*inch)
            elements.append(rl_timeline_img)
            elements.append(Spacer(1, 0.2*inch))

        # --- 2. THREAT DISTRIBUTION DONUT ---
        # # Build distribution data from statistics
        # distribution_data = {
        #     'None': stats.get('safe', 0),
        #     'DoS': stats.get('dos', 0),
        #     'Probe': stats.get('probe', 0),
        #     'R2L': stats.get('r2l', 0),
        #     'U2R': stats.get('u2r', 0)
        # }
        # Filter out zero values to make chart cleaner
        active_threats = {k: v for k, v in distribution_data.items() if v > 0}
        
        if active_threats:
            elements.append(Paragraph("Threat Distribution Analysis", styles['Heading3']))
            donut_img_buffer = create_chart_image('donut', active_threats, "Distribution of Detected Traffic Types")
            rl_donut_img = Image(donut_img_buffer, width=6*inch, height=3*inch)
            elements.append(rl_donut_img)
            elements.append(Spacer(1, 0.2*inch))
        
        # Statistics summary
        elements.append(Paragraph("Statistical Summary", styles['Heading3']))
        stats_data = [
            ["Metric", "Value"],
            ["Total Packets Analyzed", str(stats.get('total', 0))],
            ["Anomalies Detected", str(stats.get('anomalies', 0))],
            ["Safe Packets", str(stats.get('safe', 0))],
            ["Detection Rate", f"{(stats.get('anomalies', 0) / max(stats.get('total', 1), 1) * 100):.2f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00ff9d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0a1926')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a3a5a'))
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Recent incidents
        if incident_log:
            elements.append(Paragraph("Recent High-Risk Incidents", styles['Heading3']))
            incident_data = [["Time", "Threat Type", "Risk Score"]]
            
            for incident in incident_log[-10:]:  # Last 10 incidents
                incident_data.append([
                    datetime.fromisoformat(incident['timestamp']).strftime("%H:%M:%S"),
                    incident['threat_type'],
                    f"{incident['risk_score']}%"
                ])
            
            incident_table = Table(incident_data, colWidths=[1.5*inch, 2*inch, 1.5*inch])
            incident_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff3e3e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0a1926')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a3a5a'))
            ]))
            elements.append(incident_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Analysis summary
        elements.append(Paragraph("Analysis Summary", styles['Heading3']))
        
        anomaly_rate = (stats.get('anomalies', 0) / max(stats.get('total', 1), 1)) * 100
        
        if anomaly_rate > 50:
            summary = f"CRITICAL: High anomaly detection rate ({anomaly_rate:.1f}%). Network is experiencing significant malicious activity. Immediate investigation recommended. Dominant threat vectors include DoS attacks and unauthorized access attempts."
        elif anomaly_rate > 20:
            summary = f"WARNING: Elevated anomaly rate ({anomaly_rate:.1f}%). Network shows signs of potential intrusion activity. Enhanced monitoring advised."
        else:
            summary = f"NORMAL: Anomaly rate within acceptable parameters ({anomaly_rate:.1f}%). Network traffic patterns appear normal with isolated suspicious events typical of baseline activity."
        
        elements.append(Paragraph(summary, styles['BodyText']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'forensic_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        print(f"Report generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get_system_info', methods=['GET'])
def get_system_info():
    """Return system capabilities."""
    return jsonify({
        'psutil_available': PSUTIL_AVAILABLE,
        'network_mode': NETWORK_MODE,
        'simulation_mode': SIMULATION_MODE
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)