from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize Ollama (Ensure 'ollama run llama3.2' is active in terminal)
llm = OllamaLLM(model="llama3.2")

def get_explanation(findings, stimulus_text, audience_level, case_context):
    """
    Uses Llama 3.2 to translate technical findings based on audience.
    levels: 'Jury' (Simple), 'Judge' (Formal), 'Expert' (Technical)
    """
    
    tech_summary = (
        f"Stimulus: '{stimulus_text}'. "
        f"Max Amplitude: {findings['amplitude_uv']} microvolts. "
        f"Latency: {findings['latency_ms']} ms. "
        f"Signal-to-Noise Ratio: {findings['snr']}. "
        f"Conclusion: {'Positive for Experiential Knowledge' if findings['detection'] else 'Negative (No recognition)'}."
    )

    case_info_str = (
        f"Case Number: {case_context.get('case_id', 'Unknown')}\n"
        f"Judge: {case_context.get('judge_name', 'Presiding Judge')}\n"
        f"Defendant: {case_context.get('defendant', 'Defendant')}\n"
        f"Expert Witness: {case_context.get('expert_name', 'Forensic Expert')}, {case_context.get('expert_title', 'Neuroscientist')}"
    )

    prompts = {
        "Jury": """
        You are {expert_name}, {expert_title}.
        You are testifying in the case of {defendant} (Case #{case_id}).
        Explain brain evidence to the Jury. 
        Use an analogy (like a 'recognition reflex' or 'mental fingerprint'). 
        Keep it under 3 sentences. Avoid jargon.
        
        Data: {data}
        """,
        
        "Judge": """
        You are {expert_name}, {expert_title}.
        You are submitting a formal legal report to Judge {judge_name} for Case #{case_id}.
        Defendant: {defendant}.
        Focus on the admissibility, reliability, and the correlation between the stimulus and the physiological response.
        Use formal legal/forensic tone.
        
        Data: {data}
        """,
        
        "Expert": """
        You are {expert_name}, {expert_title}.
        You are writing a peer-review note for another Neuroscientist regarding Case #{case_id}.
        Focus on the P300 wave morphology, latency timing, and artifact possibilities. 
        Be concise and technical.
        
        Data: {data}
        """
    }

    # Fill in the dynamic parts of the prompt first
    template_str = prompts[audience_level].format(
        expert_name=case_context.get('expert_name', 'The Expert'),
        expert_title=case_context.get('expert_title', 'Neuroscientist'),
        case_id=case_context.get('case_id', 'Unknown'),
        judge_name=case_context.get('judge_name', 'Presiding Judge'),
        defendant=case_context.get('defendant', 'Defendant'),
        data="{data}" # Leave this key for the chain to fill
    )

    prompt = ChatPromptTemplate.from_template(template_str)
    chain = prompt | llm
    
    return chain.invoke({"data": tech_summary})

def chat_with_evidence(user_question, current_findings):
    """Allows the user to ask Q&A about the specific graph."""
    prompt = ChatPromptTemplate.from_template("""
    You are an AI Forensic Assistant. Answer the user's question specifically based on the current EEG findings.
    
    Current Findings: {findings}
    User Question: {question}
    
    Answer concisely.
    """)
    chain = prompt | llm
    return chain.invoke({"findings": str(current_findings), "question": user_question})