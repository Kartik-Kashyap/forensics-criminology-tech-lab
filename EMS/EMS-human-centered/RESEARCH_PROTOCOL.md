# Research Protocol Template

## Using the Forensic Evidence Management System for Academic Research

---

## Purpose of This Document

This template provides guidance for researchers who want to use this system in academic studies of forensic psychology, criminology, human-computer interaction, or related fields.

**Important**: This system is designed for research purposes. Any human subjects research requires IRB approval and informed consent.

---

## Part 1: Research Design Considerations

### 1.1 Suitable Research Questions

This system can help investigate questions such as:

**Cognitive Bias Research:**
- Does making investigators aware of their access patterns reduce confirmation bias?
- How does role-based access control affect investigative thoroughness?
- What feedback mechanisms most effectively reduce premature conclusion formation?

**Procedural Compliance:**
- Does separation of duties improve chain of custody documentation quality?
- How does justification requirement affect decision-making speed and quality?
- What factors predict procedural violations?

**Human-AI Interaction:**
- How do investigators respond to AI-generated explanations?
- Does LLM transparency increase trust in the system?
- What level of AI assistance optimizes human decision-making?

**Training Effectiveness:**
- Can this system improve forensic science student learning outcomes?
- Does simulation-based training transfer to real investigative skills?
- How does feedback immediacy affect procedural learning?

### 1.2 Research Design Options

#### Experimental Study
```
Design: Randomized controlled trial
Groups: 
  - Experimental: System with bias alerts enabled
  - Control: System with bias alerts disabled
Measures:
  - Access pattern diversity (Gini coefficient)
  - Time to conclusion
  - Evidence coverage (% of items examined)
  - Decision accuracy (if ground truth available)
```

#### Observational Study
```
Design: Naturalistic observation
Participants: Forensic science students in coursework
Measures:
  - Behavioral patterns over time
  - Learning curve analysis
  - Role compliance rates
  - Voluntary feedback-seeking
```

#### Mixed Methods Study
```
Design: Quantitative + qualitative
Quantitative: System-logged behavioral data
Qualitative: Post-task interviews
Triangulation: Compare stated vs. actual behavior
Analysis: Thematic analysis + statistical tests
```

---

## Part 2: IRB Approval Requirements

### 2.1 Human Subjects Considerations

**This system likely qualifies as human subjects research if:**
- ✅ You're collecting data about people's behavior
- ✅ Participants are identifiable (even temporarily)
- ✅ You're studying decision-making or cognitive processes

**It may NOT require full IRB review if:**
- Educational setting with existing data collection practices
- Completely anonymized with no possibility of re-identification
- Purely technical evaluation with no human behavior analysis

**Consult your institution's IRB for definitive guidance.**

### 2.2 Required IRB Documentation

#### Informed Consent Elements

Your consent form should explain:

1. **Purpose**: "This study examines how digital evidence management systems affect investigative decision-making"

2. **Procedures**: "You will use a prototype evidence management system to complete simulated investigative tasks. Your interactions will be logged including evidence access patterns, time spent, and actions taken."

3. **Data Collection**: "The system automatically logs:
   - Which evidence items you view and when
   - How long you spend on each item
   - Actions you perform (view, copy, export)
   - Justifications you provide for actions
   - Your role and user ID (anonymized for analysis)"

4. **Risks**: "Risks are minimal. You may experience:
   - Mild stress from task demands
   - Concern about being monitored
   - Discomfort if bias indicators triggered"

5. **Benefits**: "You may learn about:
   - Proper evidence handling procedures
   - Your own decision-making patterns
   - Cognitive biases in forensic contexts"

6. **Confidentiality**: "Data will be:
   - Anonymized (user IDs replaced with participant numbers)
   - Aggregated for analysis (no individual identification)
   - Stored securely (encrypted, password-protected)
   - Destroyed after [X years]"

7. **Voluntary Participation**: "You may:
   - Withdraw at any time without penalty
   - Skip any tasks you're uncomfortable with
   - Request your data be deleted"

#### Risk Mitigation

**Psychological Risks:**
- Bias indicators may cause embarrassment or defensiveness
- Mitigation: Frame alerts as learning opportunities, not performance evaluation
- Debrief: Explain that ALL investigators show biases; this is normal

**Privacy Risks:**
- Behavioral data could be re-identified
- Mitigation: Immediate anonymization, no names in dataset
- Storage: Encrypted, access-controlled databases

**Academic Risks:**
- If used in coursework, students may fear grade impact
- Mitigation: Clearly separate research from grading
- Alternative: Allow students to opt out of data use while still completing exercise

### 2.3 Sample IRB Application Sections

#### Study Population
```
Participants: 
- N = 60 undergraduate students in forensic science program
- Age: 18+ (adults only)
- Recruitment: Course announcement, extra credit offered
- Inclusion: Currently enrolled in FORSC 301 or higher
- Exclusion: None

Vulnerable Populations: None
```

#### Procedures
```
Session 1 (60 minutes):
1. Informed consent process (10 min)
2. System tutorial (15 min)
3. Practice scenario (10 min)
4. Research scenario (20 min)
5. Post-task survey (5 min)

Session 2 (Optional, 30 minutes):
1. Semi-structured interview about experience
2. Debrief and explanation of study goals
```

#### Data Security
```
Collection:
- System logs to local encrypted database
- No external transmission
- No identifiable information in logs

Storage:
- University secure server
- Access limited to research team
- Password protected, encrypted

Analysis:
- User IDs replaced with participant numbers
- Mapping key stored separately, destroyed after verification

Retention:
- 7 years per university policy
- Then securely deleted
```

---

## Part 3: Data Collection Protocol

### 3.1 Participant Instructions

**Sample Welcome Script:**
```
"Welcome to this research study on digital forensic evidence management.

Today, you'll use a prototype system designed to help investigators manage 
digital evidence while maintaining legal chain of custody requirements.

The system will log your interactions - what evidence you view, when, and 
what actions you take. This data helps us understand how people make 
investigative decisions and how systems can support better outcomes.

Remember:
- There are no right or wrong approaches
- This is about the system, not evaluating you personally
- Bias indicators that appear are normal - everyone has cognitive biases
- You can stop at any time

Do you have any questions before we begin?"
```

### 3.2 Experimental Scenarios

#### Sample Scenario: Missing Person Investigation

**Scenario Description:**
```
CASE-2026-042: Missing Person - Sarah Martinez, age 24

Sarah Martinez was reported missing by her roommate on January 10, 2026. 
The following digital evidence has been collected:

Evidence Items:
1. Sarah's laptop computer (disk image)
2. Screenshots from Sarah's phone (backup from cloud)
3. Security camera footage from her apartment building
4. Email correspondence between Sarah and unknown party
5. Social media posts from week before disappearance
6. Financial records showing recent large withdrawals
7. GPS data from Sarah's car (last 30 days)

Your task:
As a forensic analyst, examine the evidence to establish a timeline 
of Sarah's activities in the 48 hours before she was reported missing.

You have 20 minutes to:
- Review available evidence
- Create a working copy of relevant items
- Document your findings
- Prepare evidence for potential court use
```

**Experimental Manipulation:**
- **Control Group**: System shows evidence list only
- **Experimental Group**: System shows evidence list + bias indicators

**Ground Truth** (for accuracy measurement):
Hidden in evidence is clear timeline. Accuracy = how complete the timeline.

#### Sample Scenario: Corporate Fraud Investigation

**Scenario Description:**
```
CASE-2026-073: Corporate Fraud - Tech Solutions Inc.

Anonymous whistleblower alleges CFO Jane Thompson has been 
embezzling company funds through fake vendor payments.

Evidence Items:
1. Accounting database (Excel files, 18 months)
2. Email correspondence (CFO and Accounts Payable)
3. Bank statements (company account)
4. Vendor contracts and invoices
5. Wire transfer records
6. CFO's work computer (browser history, documents)
7. Internal audit reports

Your task:
Determine whether evidence supports the fraud allegation.

Challenges:
- Large volume of financial data
- Some documents contradict others
- Need to maintain objectivity (innocent until proven guilty)
```

**Experimental Manipulation:**
- **Biasing Condition**: Scenario emphasizes "strong evidence of fraud"
- **Neutral Condition**: Scenario presents facts without suggestion

**Measure**: Does biasing condition lead to premature conclusions?

### 3.3 Dependent Variables to Measure

#### Behavioral Metrics (Automatic)
```python
dependent_variables = {
    "evidence_coverage": "% of evidence items examined",
    "access_diversity": "Gini coefficient of access distribution",
    "time_to_first_export": "Minutes until export action",
    "total_time": "Total session duration",
    "repeated_access_rate": "Max accesses to single item / total accesses",
    "working_copy_usage": "# of working copies created",
    "justification_length": "Average characters per justification",
    "alert_response": "Actions taken after bias alert"
}
```

#### Self-Report Measures (Survey)
```
Post-Task Questionnaire (1-7 Likert scale):

Perceived Bias:
1. "I examined all evidence equally thoroughly"
2. "I focused on evidence supporting my initial theory"
3. "I actively looked for evidence contradicting my theory"

System Usability:
4. "The system helped me work more systematically"
5. "Bias alerts were helpful for my decision-making"
6. "The system was easy to use"

Trust in AI:
7. "AI explanations were accurate and helpful"
8. "I trusted the AI-generated summaries"
9. "AI transparency was important to me"

Perceived Fairness:
10. "The system treated me fairly"
11. "I felt the system respected my professional judgment"
12. "Bias alerts felt accusatory" (reverse scored)
```

#### Qualitative Data (Interview)
```
Interview Protocol:

1. "Tell me about your experience using the system."
   - Probe: What did you find helpful? Frustrating?

2. "Did you notice the [bias alerts / AI explanations]?"
   - Probe: How did you respond to them?

3. "How did the system affect your investigation approach?"
   - Probe: Would you have done anything differently without it?

4. "What would you change about the system?"
   - Probe: Missing features? Confusing elements?

5. "Do you think this kind of system could be useful in real investigations?"
   - Probe: What would be needed for real-world use?
```

---

## Part 4: Data Analysis Plan

### 4.1 Quantitative Analysis

#### Hypothesis 1: Bias alerts reduce confirmation bias

**Operational Definition:** Confirmation bias = high Gini coefficient (concentrated attention)

**Analysis:**
```
Independent Variable: Group (alerts vs. no alerts)
Dependent Variable: Gini coefficient of evidence access

Test: Independent samples t-test
H0: μ_alerts = μ_control
H1: μ_alerts < μ_control

Expected: Alerts group shows more distributed attention (lower Gini)

Power Analysis: 
  Effect size: d = 0.5 (medium)
  Power: 0.80
  Alpha: 0.05
  Required N: 64 per group
```

#### Hypothesis 2: AI explanations increase trust

**Operational Definition:** Trust = Likert ratings on trust items

**Analysis:**
```
Repeated Measures:
  Time 1: Before using system (baseline trust in AI)
  Time 2: After using system (trust after experience)

Test: Paired samples t-test
H0: μ_before = μ_after
H1: μ_after > μ_before

Moderator Analysis: Does explanation quality moderate trust change?
```

#### Additional Analyses

**Correlation Analysis:**
```python
# Do behavioral patterns predict decision accuracy?
correlations = {
    "evidence_coverage vs. accuracy": "More coverage → higher accuracy?",
    "time_invested vs. accuracy": "U-shaped? (too fast or too slow both bad)",
    "alert_response vs. accuracy": "Heeding alerts → better outcomes?"
}
```

**Regression Analysis:**
```python
# What predicts confirmation bias?
model = """
Gini ~ Group + PriorExperience + CognitiveLoad + Time + Error
"""
# Control for experience, complexity, time pressure
```

### 4.2 Qualitative Analysis

#### Thematic Analysis Procedure

**Step 1: Familiarization**
- Read all interview transcripts
- Note initial impressions
- Identify interesting patterns

**Step 2: Coding**
```
Initial Codes (example):
- "System helped me stay organized"
- "Alerts made me defensive"
- "AI explanations unclear"
- "Felt monitored/watched"
- "Learned about my biases"
- "Would use in real work"
```

**Step 3: Theme Development**
```
Potential Themes:
1. "System as scaffold" - Helps structure thinking
2. "Resistance to feedback" - Defensiveness about bias alerts
3. "Trust through transparency" - AI explanations build confidence
4. "Privacy concerns" - Discomfort with monitoring
```

**Step 4: Validation**
- Inter-rater reliability (2+ coders)
- Member checking (participant feedback)
- Triangulation with quantitative data

#### Mixed Methods Integration

**Convergent Validity:**
```
Quantitative: High Gini coefficient (concentrated attention)
    +
Qualitative: Theme "I knew what I was looking for"
    =
Triangulated Finding: Evidence of confirmation bias
```

**Divergent Findings:**
```
Quantitative: Alert group shows lower Gini (less bias)
But
Qualitative: "Alerts didn't change what I did"

Explanation: Implicit vs. explicit behavior change?
```

---

## Part 5: Ethical Research Practices

### 5.1 Minimizing Participant Distress

**Potential Distress Sources:**
1. Bias indicators triggering embarrassment
2. Feeling evaluated or judged
3. Concern about data use

**Mitigation Strategies:**

**Before Study:**
- Clear communication: "This studies the SYSTEM, not you"
- Normalize biases: "Everyone has cognitive biases - even experts"
- Emphasize learning: "This helps you understand your thinking"

**During Study:**
- Supportive language in alerts: "Consider reviewing..." not "You are biased"
- Option to pause or stop
- Researcher available for questions

**After Study:**
- Debrief: Explain what bias indicators mean
- Educational component: "Here's why everyone shows these patterns"
- Validation: "Your data will help improve systems for everyone"

### 5.2 Data Privacy Protection

**Anonymization Protocol:**
```python
def anonymize_participant_data(raw_data):
    """
    Step 1: Remove direct identifiers
    - Real names → Participant IDs (P001, P002, etc.)
    - Email addresses → Deleted
    - IP addresses → Deleted
    
    Step 2: Generalize quasi-identifiers
    - Exact timestamps → Time of day (morning/afternoon/evening)
    - Specific evidence items → Evidence type (image/document/video)
    
    Step 3: Create mapping key
    - Store separately from anonymized data
    - Destroy after data verification complete
    
    Step 4: Aggregate when possible
    - Report group means, not individuals
    - Minimum cell size of 5 for cross-tabs
    """
    
    anonymized = {
        "participant_id": generate_random_id(),
        "group": raw_data['group'],
        "session_date": generalize_to_week(raw_data['date']),
        "behavioral_metrics": raw_data['metrics'],
        # NO: name, email, exact times, case details
    }
    
    return anonymized
```

**Storage Security:**
```
Phase 1: Collection
- Encrypted database
- Access restricted to research team
- No cloud storage (local only)

Phase 2: Analysis  
- Work on anonymized data only
- No re-identification attempts
- Aggregated reporting

Phase 3: Retention
- 7 years per university policy
- Annual access reviews
- Then secure deletion (multi-pass overwrite)
```

### 5.3 Participant Rights

**Right to Information:**
- Full disclosure of data collection practices
- Explanation of how data will be used
- Access to study results upon completion

**Right to Withdraw:**
```
Withdrawal Procedure:
1. Participant notifies researcher (any time, no reason required)
2. Researcher immediately:
   - Stops data collection
   - Removes participant data from dataset
   - Securely deletes all records
3. No penalty, no questions asked
4. Extra credit (if offered) still awarded
```

**Right to Access:**
- Participants can request their own data
- Provided in readable format (not raw logs)
- Within 30 days of request

---

## Part 6: Publication and Dissemination

### 6.1 Reporting Standards

Follow APA guidelines for reporting:

**Method Section Must Include:**
- System specifications (version, settings)
- Participant demographics
- Scenario details
- Experimental manipulations
- Dependent variable definitions
- Analysis plan (pre-registered if possible)

**Results Section Must Include:**
- Descriptive statistics for all variables
- Effect sizes (not just p-values!)
- Confidence intervals
- Assumption checks
- Full statistical outputs in supplement

**Limitations Section Must Address:**
- Sample characteristics (generalizability)
- Artificial task constraints (external validity)
- System limitations (measurement error)
- Alternative explanations

### 6.2 Open Science Practices

**Pre-Registration:**
```
Before data collection, register:
- Hypotheses
- Sample size justification
- Analysis plan
- Stopping rules

Platform: OSF (osf.io) or AsPredicted

Benefit: Prevents HARKing (Hypothesizing After Results Known)
```

**Data Sharing:**
```
What to Share:
✅ Anonymized dataset
✅ Analysis code (R/Python scripts)
✅ Experimental materials (scenarios, surveys)
✅ Codebooks (variable definitions)

Where to Share:
- OSF repository
- University institutional repository
- Journal supplementary materials

What NOT to Share:
❌ Identifiable data
❌ Participant contact information
❌ Mapping keys
```

**Code Sharing:**
```
GitHub Repository Should Include:
- Complete system code
- Documentation
- Installation instructions
- Sample data (synthetic or anonymized)
- Issue tracker for bug reports

License: Academic research license (not commercial use)
```

### 6.3 Ethical Publication

**Authorship:**
- Credit all substantial contributors
- Data collectors deserve authorship
- Follow CRediT taxonomy for roles

**Conflicts of Interest:**
- Disclose funding sources
- Acknowledge system development role
- Note any commercial interests

**Limitations and Cautions:**
```
Required Disclosures:

1. "This system is a research prototype and has not been validated 
   for real forensic investigations."

2. "Bias indicators are for research purposes and should not be 
   used for personnel evaluation."

3. "Results may not generalize beyond student populations in 
   simulated scenarios."

4. "The system measures behavioral patterns, not bias itself, 
   which cannot be directly observed."
```

---

## Part 7: Sample Research Protocol

### Complete Study Example

**Title:** "The Effect of Real-Time Bias Feedback on Forensic Evidence Examination Patterns: A Randomized Controlled Trial"

**Research Question:** Does providing real-time feedback about access patterns reduce confirmation bias in digital forensic investigations?

**Participants:** 
- N = 80 undergraduate students (forensic science majors)
- Ages 18-25
- Recruited through course announcements
- Extra credit offered

**Design:**
- 2x2 factorial design
- IV1: Feedback (yes/no)
- IV2: Case complexity (simple/complex)
- Random assignment to conditions

**Procedure:**
```
Session 1 (Week 1): Baseline
1. Informed consent (5 min)
2. Demographics survey (5 min)
3. System tutorial (15 min)
4. Practice scenario (10 min)
5. Baseline scenario - NO feedback (20 min)

Session 2 (Week 2): Experimental
1. Brief review (5 min)
2. Experimental scenario - Feedback per condition (30 min)
   - Control: No bias alerts
   - Experimental: Bias alerts enabled
3. Post-task survey (10 min)
4. Debrief interview (15 min)
```

**Measures:**

*Primary DV:*
- Gini coefficient of evidence access distribution
- Lower = more distributed attention = less confirmation bias

*Secondary DVs:*
- Time to first export (premature conclusions)
- Evidence coverage (% items examined)
- Decision accuracy (compared to ground truth)

*Covariates:*
- Prior forensic experience
- Cognitive reflection test (CRT) score
- Need for cognition scale

**Analysis Plan:**

*Primary:*
```
ANOVA: Gini ~ Feedback * Complexity + Error

Planned Contrasts:
- Feedback vs. No Feedback (main effect)
- Simple vs. Complex (main effect)
- Interaction (is feedback more helpful in complex cases?)

Expected: Feedback reduces Gini, especially in complex cases
```

*Power:*
```
Effect size: f = 0.25 (medium)
Power: 0.80
Alpha: 0.05
Groups: 4
Required total N: 76 (actual N=80, allowing for dropout)
```

**Timeline:**
- Month 1: IRB approval, recruitment
- Month 2-3: Data collection
- Month 4: Analysis
- Month 5-6: Write-up and submission

**Budget:**
- Participant compensation: $800 (10/hr × 2hr × 80 participants)
- Research assistant: $2000
- Computing/software: $0 (open source)
- Total: $2800

---

## Conclusion

This research protocol template provides a framework for rigorous academic study using the Forensic Evidence Management System. Key principles:

1. **Ethical First:** IRB approval, informed consent, participant protection
2. **Rigorous Design:** Clear hypotheses, adequate power, proper controls
3. **Transparent Methods:** Pre-registration, open data, replicable procedures
4. **Responsible Reporting:** Acknowledge limitations, share materials, credit contributors

Remember: This system is a research tool. Use it ethically, report honestly, and contribute to cumulative knowledge about human factors in forensic science.

---

**For questions about research protocols, consult:**
- Your institutional IRB
- Advisor or research mentor
- APA ethical guidelines
- Relevant professional societies (AAFS, APA, etc.)

---

Last Updated: January 2026
