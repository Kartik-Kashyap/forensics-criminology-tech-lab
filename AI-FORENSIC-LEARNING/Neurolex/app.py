import streamlit as st
import plotly.graph_objects as go
import data_gen
import analysis
import ai_expert
import time
from fpdf import FPDF

# --- PDF Generation Class ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'NeuroLex Forensic Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(case_context, stimulus, findings, ai_explanation):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Case Details
    pdf.cell(200, 10, txt=f"Case ID: {case_context['case_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Judge: {case_context['judge_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Defendant: {case_context['defendant']}", ln=True)
    pdf.cell(200, 10, txt=f"Expert Witness: {case_context['expert_name']} ({case_context['expert_title']})", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Stimulus: {stimulus}", ln=True)
    pdf.ln(10)
    
    # Findings
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Forensic Analysis Findings:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Amplitude: {findings['amplitude_uv']} uV", ln=True)
    pdf.cell(200, 10, txt=f"Latency: {findings['latency_ms']} ms", ln=True)
    pdf.cell(200, 10, txt=f"SNR: {findings['snr']}", ln=True)
    pdf.cell(200, 10, txt=f"Detection: {'POSITIVE' if findings['detection'] else 'NEGATIVE'}", ln=True)
    pdf.ln(10)
    
    # AI Explanation
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Expert Witness Explanation:", ln=True)
    pdf.set_font("Arial", size=11)
    # FPDF multi_cell handles basic wrapping
    pdf.multi_cell(0, 10, txt=ai_explanation.encode('latin-1', 'replace').decode('latin-1')) # Handle potential unicode issues
    
    return pdf.output(dest='S').encode('latin-1')

# --- Page Config ---
st.set_page_config(page_title="NeuroLex: Forensic Explainability", layout="wide")


# st.markdown("""
# <style>

# /* ===== GLOBAL ===== */
# html, body, [class*="css"] {
#     font-family: 'Inter', sans-serif;
# }

# /* App background */
# .stApp {
#     background: linear-gradient(180deg, #0b0f19 0%, #0e1324 100%);
#     color: #e5e7eb;
# }

# /* ===== HEADERS ===== */
# h1, h2, h3, h4 {
#     color: #f9fafb;
#     letter-spacing: 0.3px;
# }

# h1 {
#     font-weight: 800;
# }

# h3 {
#     margin-top: 0.5rem;
# }

# /* ===== SIDEBAR (CASE FILE) ===== */
# section[data-testid="stSidebar"] {
#     background: #070b14;
#     border-right: 1px solid #1f2937;
# }

# section[data-testid="stSidebar"] h1,
# section[data-testid="stSidebar"] h2,
# section[data-testid="stSidebar"] h3 {
#     color: #e5e7eb;
# }

# section[data-testid="stSidebar"] label {
#     color: #9ca3af;
#     font-weight: 600;
# }

# /* Inputs */
# .stTextInput input,
# .stSelectbox div,
# .stSlider {
#     background: #0f172a !important;
#     color: #e5e7eb !important;
#     border-radius: 8px;
#     border: 1px solid #1f2937;
# }

# /* ===== BUTTONS ===== */
# .stButton button {
#     background: linear-gradient(135deg, #f59e0b, #d97706);
#     color: black;
#     font-weight: 700;
#     border-radius: 10px;
#     padding: 0.6rem 1.2rem;
#     border: none;
#     transition: all 0.25s ease;
# }

# .stButton button:hover {
#     transform: translateY(-2px);
#     box-shadow: 0 10px 25px rgba(245, 158, 11, 0.35);
# }

# /* ===== METRICS ===== */
# [data-testid="metric-container"] {
#     background: #0f172a;
#     border-radius: 16px;
#     padding: 1rem;
#     border: 1px solid #1f2937;
#     box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
# }

# [data-testid="metric-container"] label {
#     color: #9ca3af;
# }

# [data-testid="metric-container"] div {
#     color: #f9fafb;
#     font-weight: 700;
# }

# /* ===== ALERTS ===== */
# .stAlert {
#     border-radius: 14px;
#     border-left: 6px solid;
# }

# .stAlert[data-baseweb="notification"][class*="error"] {
#     background: rgba(220, 38, 38, 0.15);
#     border-left-color: #dc2626;
# }

# .stAlert[data-baseweb="notification"][class*="success"] {
#     background: rgba(16, 185, 129, 0.15);
#     border-left-color: #10b981;
# }

# /* ===== PLOT CONTAINER ===== */
# .stPlotlyChart {
#     background: #020617;
#     border-radius: 16px;
#     padding: 0.5rem;
#     border: 1px solid #1f2937;
# }

# /* ===== INFO / AI EXPLANATION ===== */
# .stInfo {
#     background: rgba(37, 99, 235, 0.12);
#     border-left: 6px solid #2563eb;
#     border-radius: 14px;
#     color: #e5e7eb;
# }

# /* ===== EXPANDER (CROSS EXAMINATION) ===== */
# details {
#     background: #020617;
#     border-radius: 16px;
#     border: 1px solid #1f2937;
#     padding: 0.5rem 1rem;
# }

# /* ===== DOWNLOAD BUTTON ===== */
# .stDownloadButton button {
#     background: linear-gradient(135deg, #22c55e, #16a34a);
#     color: black;
#     font-weight: 700;
#     border-radius: 12px;
# }

# </style>
# """, unsafe_allow_html=True)



st.title("NeuroLex — Neuro-Forensic Evidence Dashboard")
st.markdown(
    "<span style='color:#9ca3af;'>Court-admissible neural evidence analysis & expert interpretation</span>",
    unsafe_allow_html=True
)


# --- Sidebar: Case Controls ---
with st.sidebar:
    st.header("Case File")
    
    # 1. Select a Stimulus to Analyze
    st.subheader("Select Evidence Probe")
    stimuli = data_gen.get_stimulus_data()
    selected_stimulus_name = st.selectbox("Stimulus Presented:", [s["text"] for s in stimuli])
    
    # Get the full object of selected stimulus
    selected_stimulus = next(s for s in stimuli if s["text"] == selected_stimulus_name)

    # In the Sidebar
    st.title("🗂️ Case File Setup")
    case_id = st.text_input("Case Number", value="CR-2024-88")
    judge_name = st.text_input("Presiding Judge", value="Hon. Justice Sharma")
    court_name = st.text_input("Court Jurisdiction", value="High Court of Delhi")
    defendant = st.text_input("Defendant Name", value="Rahul Verma")
    
    st.divider()
    st.subheader("👨‍⚖️ Expert Details")
    expert_name = st.text_input("Your Name", value="Dr. A. Gupta")
    expert_title = st.text_input("Title/Position", value="Senior Forensic Neuroscientist")

    # Collect context
    case_context = {
        "case_id": case_id,
        "judge_name": judge_name,
        "court_name": court_name,
        "defendant": defendant,
        "expert_name": expert_name,
        "expert_title": expert_title
    }

    # 2. The Simplicity Slider
    st.divider()
    st.subheader("Explanation Mode")
    audience = st.select_slider(
        "Select Target Audience:",
        options=["Jury", "Judge", "Expert"],
        value="Judge"
    )

    analyze_btn = st.button("Analyze Neural Response")

# --- Main Logic ---

# --- Main Logic ---

# Initialize Session State
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = {}

# Button Click: Run Analysis and Store in Session State
if analyze_btn:
    # 1. Generate/Load Data
    time_array, signal = data_gen.generate_mock_eeg(is_guilty=selected_stimulus["guilty_response"])

    # 2. Analyze Data
    findings = analysis.analyze_signal(time_array, signal)
    
    # Store everything needed for rendering
    st.session_state.results = {
        'time': time_array,
        'signal': signal,
        'findings': findings,
        'stimulus_text': selected_stimulus["text"],
        'case_context': case_context,
        'audience': audience
    }
    st.session_state.analysis_complete = True
    
    # Run Animation (Only when button is clicked)
    # Animation loop
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        # FAST for dev, can slow down if requested
        # time.sleep(0.01) 
        progress_bar.progress(i + 1)
        if i < 30:
            status_text.text("Filtering Alpha Waves...")
        elif i < 60:
            status_text.text("Isolating P300 Evoked Potential...")
        else:
            status_text.text("Running Llama 3.2 Narrative Engine...")
    
    # After animation, cleanup
    status_text.empty()
    progress_bar.empty()

# --- RENDER DASHBOARD (If analysis is complete) ---
if st.session_state.analysis_complete:
    # Retrieve data from session state
    res = st.session_state.results
    
    # If parameters changed significantly (like audience), we might want to regenerate the explanation ONLY
    # For now, let's keep it simple: The 'Analyze' button drives the main update.
    # However, for Audience slider, it is better if it updates dynamically!
    # Let's update the audience in the result set if it changed in the sidebar, 
    # but strictly, the user asked for "Analyze" button to update info.
    # So we will stick to using the STORED audience to avoid inconsistencies 
    # OR we use the current audience but keep the old signal.
    
    # Using CURRENT audience for the AI part allows dynamic slider usage without full re-analysis
    current_audience = audience
    
    # --- Layout: Top Row (Visuals) ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Real-time EEG Response")
        
        # Create Plotly Graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=res['time'], y=res['signal'], mode='lines', name='EEG Signal', line=dict(color='#00CC96')))
        
        # Highlight the P300 Window
        fig.add_vrect(x0=0.3, x1=0.6, fillcolor="red", opacity=0.1, annotation_text="P300 Window", annotation_position="top left")
        
        fig.update_layout(
            xaxis_title="Time (seconds)",
            yaxis_title="Amplitude (µV)",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Forensic Analysis")
        
        # Metric Cards
        m1, m2 = st.columns(2)
        m1.metric("Amplitude", f"{res['findings']['amplitude_uv']} µV", delta_color="inverse")
        m2.metric("Latency", f"{res['findings']['latency_ms']} ms")
        
        st.divider()
        
        # Detection Status
        if res['findings']["detection"]:
            st.error("⚠️ POSITIVE RESPONSE DETECTED")
            st.write("**Interpretation:** The brain recognized this information.")
        else:
            st.success("✅ NO RESPONSE DETECTED")
            st.write("**Interpretation:** No experiential memory found.")

    # --- Layout: Bottom Row (AI Explanation) ---
    st.divider()
    st.subheader(f"🤖 AI Expert Witness ({current_audience} Mode)")

    # We only generate the AI explanation if it's not already stored OR if audience changed
    # actually, to prevent constant regeneration, we should probably store it, 
    # BUT the user might want to slide the slider and see the change.
    
    # Strategy: Generate explanation dynamically here. It relies on Ollama which might differ slightly but is fine.
    # To prevent re-generation on CHAT interaction, we should check if we need to regenerate.
    
    # For simplicity and robustness regarding the simpler "Chat" issue: 
    # We will generate it immediately. Streamlit caching could be used, or just storing it.
    # Let's store the explanation in session_state specific to the audience.
    
    explanations_key = f"explanation_{current_audience}_{res['stimulus_text']}"
    
    if explanations_key not in st.session_state:
        with st.spinner(f"Generating explanation for {current_audience}..."):
            try:
                explanation = ai_expert.get_explanation(res['findings'], res['stimulus_text'], current_audience, res['case_context'])
                st.session_state[explanations_key] = explanation
            except Exception as e:
                st.error(f"Ollama Connection Error: {e}")
                st.session_state[explanations_key] = "Error generating explanation."
    
    explanation = st.session_state[explanations_key]
    st.info(explanation)
            
    # PDF Button
    pdf_bytes = generate_pdf(res['case_context'], res['stimulus_text'], res['findings'], explanation)
    st.download_button(
        label="📄 Download Forensic Report",
        data=pdf_bytes,
        file_name=f"{res['case_context']['case_id']}_report.pdf",
        mime='application/pdf'
    )

    # --- Feature: Chat with Evidence ---
    with st.expander("💬 Cross-Examine the Evidence (Q&A)"):
        user_q = st.text_input("Ask a question about this specific graph:")
        if user_q:
            # Create a unique key for the chat response to avoid re-running if not needed? 
            # Actually, standard Streamlit behavior is fine here: user hits enter, script reruns, 'user_q' is populated.
            # We run the function.
            with st.spinner("Consulting AI Expert..."):
                answer = ai_expert.chat_with_evidence(user_q, res['findings'])
                st.write(answer)