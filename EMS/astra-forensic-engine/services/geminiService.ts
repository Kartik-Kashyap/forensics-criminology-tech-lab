
import { Case, BiasAlert, AIReasoningLog } from "../types";

const OLLAMA_ENDPOINT = 'http://localhost:11434/api/generate';
const MODEL_NAME = 'llama3.2'; // Ensure this model is pulled in Ollama: `ollama pull llama3.2`

const SYSTEM_INSTRUCTION = `
You are a Senior Forensic Psychologist and Evidence Analyst. 
Your goal is to provide a peer-review of a criminal or civil case analysis.
You MUST:
1. Identify cognitive biases (confirmation bias, over-reliance on single sources, etc.).
2. Suggest alternate hypotheses for the evidence presented.
3. Be strictly neutral. DO NOT declare guilt or innocence.
4. Log your reasoning steps clearly.
5. Use professional, academic, and clinical language.
6. OUTPUT ONLY VALID JSON. Do not include markdown formatting or explanation outside the JSON.
`;

export const analyzeCaseForBias = async (caseData: Case): Promise<{ alerts: BiasAlert[], reasoning: AIReasoningLog[] }> => {
  const prompt = `
  ${SYSTEM_INSTRUCTION}

  Analyze the following case data for cognitive biases and provide a structured reasoning log.
  
  Case Summary: ${caseData.summary}
  Evidence Count: ${caseData.evidence.length}
  Evidence Details: ${caseData.evidence.map(e => `${e.name} (${e.type}): ${e.description}`).join('; ')}
  Timeline Events: ${caseData.events.map(ev => ev.title).join(', ')}

  Respond in JSON format according to this structure:
  {
    "alerts": [
      { "type": "CONFIRMATION", "title": "...", "description": "...", "severity": "WARNING", "suggestedAction": "..." }
    ],
    "reasoning": [
      { "step": 1, "thought": "...", "supportingEvidence": ["ID1"], "alternatives": ["Alt Hypothesis 1"] }
    ]
  }
  
  ENSURE THE RESPONSE IS VALID JSON.
  `;

  try {
    const response = await fetch(OLLAMA_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL_NAME,
        prompt: prompt,
        stream: false,
        format: "json", // Enforce JSON mode if supported by the model/ollama version
        options: {
          temperature: 0.3, // Lower temperature for more deterministic/analytical output
        }
      }),
    });

    if (!response.ok) {
      throw new Error(`Ollama API Error: ${response.statusText}`);
    }

    const jsonResponse = await response.json();
    const rawText = jsonResponse.response;

    // Additional safety: try to parse the JSON if it's wrapped in markdown code blocks or similar
    // Llama 3.2 with format: 'json' should be clean, but just in case
    let data;
    try {
      data = JSON.parse(rawText);
    } catch (e) {
      console.warn("Raw text was not perfect JSON, attempting cleanup", rawText);
      const match = rawText.match(/\{[\s\S]*\}/);
      if (match) {
        data = JSON.parse(match[0]);
      } else {
        throw e;
      }
    }

    return {
      alerts: data.alerts || [],
      reasoning: data.reasoning || []
    };
  } catch (error) {
    console.error("Ollama Analysis Error:", error);
    // Return dummy data or empty to avoid crashing UI
    return { alerts: [], reasoning: [] };
  }
};
