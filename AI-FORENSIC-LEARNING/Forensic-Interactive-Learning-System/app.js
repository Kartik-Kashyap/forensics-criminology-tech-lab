// ====================================
// Forensic Learning System - Main Application
// Orchestrates UI, AI interactions, and learning flow
// ====================================

class ForensicLearningSystem {
    constructor() {
        this.currentMode = 'concepts';
        this.currentPersona = 'tutor';
        this.currentConcept = null;
        this.userProgress = this.loadProgress();
        this.conversationHistory = [];
        this.llmConnected = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.populateCurriculum();
        this.populateConceptDropdown();
        this.checkOllamaConnection();
        this.restoreSettings();
    }

    // ====================================
    // Event Listeners
    // ====================================

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const mode = e.currentTarget.dataset.mode;
                if (mode) {
                    this.switchMode(mode);
                }
            });
        });

        // Persona selection
        document.querySelectorAll('input[name="persona"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentPersona = e.target.value;
                this.showNotification(`Switched to ${AIPersonas.personas[this.currentPersona].name}`, 'info');
            });
        });

        // Concept selection
        const conceptDropdown = document.getElementById('concept-dropdown');
        if (conceptDropdown) {
            conceptDropdown.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadConcept(e.target.value);
                }
            });
        }

        // Ollama connection
        const connectBtn = document.getElementById('connect-llm');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.connectOllama());
        }

        // Settings
        const settingsToggle = document.getElementById('settings-toggle');
        const settingsPanel = document.getElementById('settings-panel');
        if (settingsToggle && settingsPanel) {
            settingsToggle.addEventListener('click', () => {
                settingsPanel.classList.toggle('open');
            });
        }

        const saveSettings = document.getElementById('save-settings');
        if (saveSettings) {
            saveSettings.addEventListener('click', () => this.saveSettings());
        }

        // Temperature slider
        const tempSlider = document.getElementById('temperature');
        const tempValue = document.getElementById('temp-value');
        if (tempSlider && tempValue) {
            tempSlider.addEventListener('input', (e) => {
                tempValue.textContent = e.target.value;
            });
        }

        // Wikipedia search
        const wikiSearchBtn = document.getElementById('wiki-search');
        const wikiModal = document.getElementById('wiki-modal');
        const wikiClose = wikiModal?.querySelector('.close');

        if (wikiSearchBtn && wikiModal) {
            wikiSearchBtn.addEventListener('click', () => {
                wikiModal.classList.add('active');
            });
        }

        if (wikiClose) {
            wikiClose.addEventListener('click', () => {
                wikiModal.classList.remove('active');
            });
        }

        const wikiSearchButton = document.getElementById('wiki-search-btn');
        const wikiInput = document.getElementById('wiki-input');
        if (wikiSearchButton && wikiInput) {
            wikiSearchButton.addEventListener('click', () => this.searchWikipedia());
            wikiInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.searchWikipedia();
            });
        }

        // Quiz generation
        const generateQuiz = document.getElementById('generate-quiz');
        if (generateQuiz) {
            generateQuiz.addEventListener('click', () => this.generateQuiz());
        }

        // Socratic dialogue
        const socraticSend = document.getElementById('socratic-send');
        const socraticInput = document.getElementById('socratic-input');
        if (socraticSend && socraticInput) {
            socraticSend.addEventListener('click', () => this.sendSocraticMessage());
            socraticInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendSocraticMessage();
            });
        }
    }

    // ====================================
    // Mode Switching
    // ====================================

    switchMode(mode) {
        this.currentMode = mode;

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.mode === mode) {
                link.classList.add('active');
            }
        });

        if (mode === 'quiz') {
            this.populateTopicDropdown();
        }

        // Update content
        document.querySelectorAll('.mode-section').forEach(section => {
            section.classList.remove('active');
        });

        const activeSection = document.getElementById(`mode-${mode}`);
        if (activeSection) {
            activeSection.classList.add('active');
        }

        // Initialize mode-specific content
        this.initializeMode(mode);
    }

    initializeMode(mode) {
        switch (mode) {
            case 'cases':
                this.loadCaseStudies();
                break;
            case 'simulation':
                this.loadSimulations();
                break;
            case 'socratic':
                this.initializeSocraticDialogue();
                break;
        }
    }

    // ====================================
    // Curriculum Management
    // ====================================

    populateCurriculum() {
        const curriculumTree = document.getElementById('curriculum-tree');
        if (!curriculumTree) return;

        ForensicKnowledge.curriculum.forEach(item => {
            const div = document.createElement('div');
            div.className = 'curriculum-item';
            div.textContent = item.title;
            div.dataset.conceptId = item.id;

            if (this.userProgress.completed.includes(item.id)) {
                div.classList.add('completed');
            }

            div.addEventListener('click', () => {
                this.switchMode('concepts');
                document.getElementById('concept-dropdown').value = item.id;
                this.loadConcept(item.id);
            });

            curriculumTree.appendChild(div);
        });
    }

    populateConceptDropdown() {
        const dropdown = document.getElementById('concept-dropdown');
        if (!dropdown) return;

        ForensicKnowledge.curriculum.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.title;
            dropdown.appendChild(option);
        });
    }

    // ====================================
    // Concept Loading and Display
    // ====================================

    async loadConcept(conceptId) {
        this.currentConcept = conceptId;
        const concept = ForensicKnowledge.concepts[conceptId];

        if (!concept) {
            this.showNotification('Concept not found', 'error');
            return;
        }

        const conceptDisplay = document.getElementById('concept-content');
        if (!conceptDisplay) return;

        // Check if we should use AI or static content
        if (this.llmConnected) {
            await this.loadConceptWithAI(conceptId, concept);
        } else {
            this.loadConceptStatic(concept);
        }

        // Mark as viewed in progress
        if (!this.userProgress.viewed.includes(conceptId)) {
            this.userProgress.viewed.push(conceptId);
            this.saveProgress();
        }
    }

    loadConceptStatic(concept) {
        const conceptDisplay = document.getElementById('concept-content');

        const html = `
            <div class="concept-card">
                <h3>${concept.name}</h3>
                <p class="tagline"><em>${concept.tagline}</em></p>
                
                <h4>📋 Case Introduction</h4>
                <div class="case-example">${concept.caseIntroduction}</div>
                
                <h4>📚 Definition</h4>
                <p>${concept.definition}</p>
                
                <h4>🔑 Key Points</h4>
                ${concept.keyPoints.map(kp => `
                    <div style="margin: 1rem 0; padding-left: 1rem; border-left: 3px solid var(--accent-cyan);">
                        <strong>${kp.point}:</strong> ${kp.explanation}
                    </div>
                `).join('')}
                
                ${concept.realWorldApplication ? `
                    <h4>🌍 Real-World Applications</h4>
                    <ul>
                        ${concept.realWorldApplication.map(app => `<li>${app}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${concept.limitations ? `
                    <h4>⚠️ Limitations</h4>
                    <ul>
                        ${concept.limitations.map(lim => `<li>${lim}</li>`).join('')}
                    </ul>
                ` : ''}
                
                <div class="ethical-note">
                    ${concept.ethicalConsiderations}
                </div>
                
                ${concept.socraticQuestions ? `
                    <h4>💭 Reflection Questions</h4>
                    <ul>
                        ${concept.socraticQuestions.map(q => `<li>${q}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${concept.casePractice ? `
                    <h4>🎯 Practice Scenario</h4>
                    <div class="case-example">
                        <p><strong>Scenario:</strong> ${concept.casePractice.scenario}</p>
                        <p><strong>Questions to Consider:</strong></p>
                        <ol>
                            ${concept.casePractice.questions.map(q => `<li>${q}</li>`).join('')}
                        </ol>
                    </div>
                ` : ''}
            </div>
            
            <div style="margin-top: 2rem; text-align: center;">
                <button onclick="app.askAIAboutConcept()" class="btn-primary" ${!this.llmConnected ? 'disabled' : ''}>
                    💬 Discuss with AI Tutor
                </button>
                <button onclick="app.markConceptComplete()" class="btn-primary">
                    ✓ Mark as Complete
                </button>
            </div>
        `;

        conceptDisplay.innerHTML = html;
    }

    async loadConceptWithAI(conceptId, concept) {
        const conceptDisplay = document.getElementById('concept-content');
        conceptDisplay.innerHTML = '<div class="loading"></div><p class="thinking">Generating personalized explanation...</p>';

        const userLevel = this.estimateUserLevel();
        const prompt = AIPersonas.generateConceptExplanationPrompt(
            concept.name,
            userLevel,
            this.currentPersona
        );

        const result = await OllamaInterface.generate(prompt);

        if (result.success) {
            const html = `
                <div class="concept-card">
                    <div style="background: rgba(0, 217, 255, 0.1); padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                        <strong>${AIPersonas.personas[this.currentPersona].avatar} ${AIPersonas.personas[this.currentPersona].name} explains:</strong>
                    </div>
                    ${this.formatAIResponse(result.response)}
                </div>
                
                <div style="margin-top: 2rem;">
                    <button onclick="app.askAIAboutConcept()" class="btn-primary">💬 Ask a Question</button>
                    <button onclick="app.loadConceptStatic(ForensicKnowledge.concepts['${conceptId}'])" class="btn-primary">
                        📖 View Static Content
                    </button>
                    <button onclick="app.markConceptComplete()" class="btn-primary">✓ Mark as Complete</button>
                </div>
            `;
            conceptDisplay.innerHTML = html;
        } else {
            this.showNotification('AI generation failed. Showing static content.', 'warning');
            this.loadConceptStatic(concept);
        }
    }

    markConceptComplete() {
        if (!this.currentConcept) return;

        if (!this.userProgress.completed.includes(this.currentConcept)) {
            this.userProgress.completed.push(this.currentConcept);
            this.saveProgress();
            this.showNotification('Concept marked as complete!', 'success');

            // Update curriculum display
            document.querySelectorAll('.curriculum-item').forEach(item => {
                if (item.dataset.conceptId === this.currentConcept) {
                    item.classList.add('completed');
                }
            });
        }
    }

    async askAIAboutConcept() {
        const userQuestion = prompt('What would you like to know about this concept?');
        if (!userQuestion) return;

        const concept = ForensicKnowledge.concepts[this.currentConcept];
        const personaData = AIPersonas.personas[this.currentPersona];

        const context = `We are discussing: ${concept.name}. ${concept.definition}`;
        const fullPrompt = personaData.getPrompt(context, userQuestion);

        const conceptDisplay = document.getElementById('concept-content');
        conceptDisplay.innerHTML += '<div class="loading"></div><p class="thinking">Thinking...</p>';

        const result = await OllamaInterface.generate(fullPrompt);

        if (result.success) {
            const responseHtml = `
                <div class="concept-card" style="background: rgba(0, 217, 255, 0.05); margin-top: 1rem;">
                    <strong>Your Question:</strong>
                    <p>${userQuestion}</p>
                    <strong>${personaData.avatar} ${personaData.name} responds:</strong>
                    ${this.formatAIResponse(result.response)}
                </div>
            `;

            const loadingElements = conceptDisplay.querySelectorAll('.loading, .thinking');
            loadingElements.forEach(el => el.remove());
            conceptDisplay.innerHTML += responseHtml;
        }
    }

    // ====================================
    // Case Studies
    // ====================================

    loadCaseStudies() {
        const caseList = document.getElementById('case-list');
        if (!caseList) return;

        caseList.innerHTML = '';

        ForensicKnowledge.caseStudies.forEach(caseStudy => {
            const card = document.createElement('div');
            card.className = 'case-card';
            card.innerHTML = `
                <h3>${caseStudy.title}</h3>
                <p>${caseStudy.scenario.substring(0, 150)}...</p>
                <span class="case-difficulty difficulty-${caseStudy.difficulty}">
                    ${caseStudy.difficulty.toUpperCase()}
                </span>
            `;
            card.addEventListener('click', () => this.loadCase(caseStudy));
            caseList.appendChild(card);
        });
    }

    async loadCase(caseStudy) {
        const activeCase = document.getElementById('active-case');
        if (!activeCase) return;

        const html = `
            <div class="concept-card">
                <h3>${caseStudy.title}</h3>
                <span class="case-difficulty difficulty-${caseStudy.difficulty}">
                    ${caseStudy.difficulty.toUpperCase()}
                </span>
                
                <h4>📋 Scenario</h4>
                <div class="case-example">${caseStudy.scenario}</div>
                
                <h4>🔍 Evidence Available</h4>
                <ul>
                    ${caseStudy.evidence.map(e => `<li>${e}</li>`).join('')}
                </ul>
                
                <h4>❓ Questions to Investigate</h4>
                <ol>
                    ${caseStudy.questions.map(q => `<li>${q}</li>`).join('')}
                </ol>
                
                <div style="margin-top: 2rem;">
                    <button onclick="app.discussCaseWithAI('${caseStudy.id}')" class="btn-primary" ${!this.llmConnected ? 'disabled' : ''}>
                        💬 Discuss with ${AIPersonas.personas[this.currentPersona].name}
                    </button>
                    <button onclick="app.loadCaseStudies()" class="btn-small">← Back to Cases</button>
                </div>
            </div>
        `;

        activeCase.innerHTML = html;
    }

    async discussCaseWithAI(caseId) {
        const caseStudy = ForensicKnowledge.caseStudies.find(c => c.id === caseId);
        if (!caseStudy) return;

        const userResponse = prompt('Share your analysis or ask a question about this case:');
        if (!userResponse) return;

        const context = `Case: ${caseStudy.title}. Scenario: ${caseStudy.scenario}. Evidence: ${caseStudy.evidence.join(', ')}`;
        const personaData = AIPersonas.personas[this.currentPersona];
        const fullPrompt = personaData.getPrompt(context, userResponse);

        const activeCase = document.getElementById('active-case');
        activeCase.innerHTML += '<div class="loading"></div><p class="thinking">Analyzing your response...</p>';

        const result = await OllamaInterface.generate(fullPrompt);

        if (result.success) {
            const responseHtml = `
                <div class="concept-card" style="background: rgba(0, 217, 255, 0.05); margin-top: 1rem;">
                    <strong>Your Analysis:</strong>
                    <p>${userResponse}</p>
                    <strong>${personaData.avatar} ${personaData.name} responds:</strong>
                    ${this.formatAIResponse(result.response)}
                </div>
            `;

            const loadingElements = activeCase.querySelectorAll('.loading, .thinking');
            loadingElements.forEach(el => el.remove());
            activeCase.innerHTML += responseHtml;
        }
    }

    // ====================================
    // Quiz Generation
    // ====================================

    // Add this to your initialization or where you switch to the quiz mode
    populateTopicDropdown() {
        const dropdown = document.getElementById('quiz-topic-dropdown');
        if (!dropdown) return;

        // Clear existing options except the first
        dropdown.innerHTML = '<option value="">-- Choose from Lessons --</option>';

        // Loop through your ForensicKnowledge.concepts and add them
        Object.entries(ForensicKnowledge.concepts).forEach(([key, concept]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = concept.name;
            // Auto-select if it's the current concept the user was studying
            if (key === this.currentConcept) option.selected = true;
            dropdown.appendChild(option);
        });
    }

    async generateQuiz() {
        const difficulty = document.getElementById('quiz-difficulty')?.value || 'intermediate';
        const count = parseInt(document.getElementById('quiz-count')?.value) || 5;

        // --- NEW TOPIC LOGIC ---
        const manualTopic = document.getElementById('quiz-topic-manual')?.value.trim();
        const selectedConceptKey = document.getElementById('quiz-topic-dropdown')?.value;

        let topicName = "";

        if (manualTopic) {
            topicName = manualTopic; // Priority 1: Manual input
        } else if (selectedConceptKey) {
            topicName = ForensicKnowledge.concepts[selectedConceptKey].name; // Priority 2: Dropdown
        } else if (this.currentConcept) {
            topicName = ForensicKnowledge.concepts[this.currentConcept].name; // Priority 3: Current lesson
        } else {
            this.showNotification('Please enter or select a topic', 'warning');
            return;
        }

        // -----------

        if (!this.llmConnected) {
            this.showNotification('Please connect to Ollama first', 'warning');
            return;
        }

        // if (!this.currentConcept) {
        //     this.showNotification('Please select a concept first', 'warning');
        //     return;
        // }

        // const concept = ForensicKnowledge.concepts[this.currentConcept];
        // const quizContent = document.getElementById('quiz-content');

        // quizContent.innerHTML = '<div class="loading"></div><p class="thinking">Generating quiz questions...</p>';

        // const prompt = AIPersonas.generateQuizPrompt(concept.name, difficulty, count);
        // const result = await OllamaInterface.generate(prompt, { temperature: 0.8 });

        const quizContent = document.getElementById('quiz-content');
        quizContent.innerHTML = `<div class="loading"></div><p class="thinking">Generating quiz questions for "${topicName}"...</p>`;

        // Pass the determined topicName to the prompt generator
        const prompt = AIPersonas.generateQuizPrompt(topicName, difficulty, count);
        const result = await OllamaInterface.generate(prompt, { temperature: 0.8 });

        if (result.success) {
            try {
                // // Parse JSON response
                // let jsonText = result.response.trim();
                // // Remove markdown code blocks if present
                // jsonText = jsonText.replace(/```json\n?/g, '').replace(/```\n?/g, '');
                let jsonText = result.response.trim();
                // 1. Remove markdown code blocks (more robust regex)
                jsonText = jsonText.replace(/^```(?:json)?\n?|```$/gm, '');

                // 2. Remove potential non-JSON text before or after the JSON block
                const jsonStart = jsonText.indexOf('{');
                const jsonEnd = jsonText.lastIndexOf('}');
                if (jsonStart !== -1 && jsonEnd !== -1) {
                    jsonText = jsonText.substring(jsonStart, jsonEnd + 1);
                }
                const quizData = JSON.parse(jsonText);

                this.displayQuiz(quizData.questions);
            } catch (error) {
                console.error('Quiz parsing error:', error);
                quizContent.innerHTML = `
                    <div class="ethical-note">
                        <p>Unable to parse quiz format. Raw response:</p>
                        <pre style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">${result.response}</pre>
                    </div>
                `;
            }
        } else {
            quizContent.innerHTML = '<p class="error">Failed to generate quiz. Please try again.</p>';
        }
    }

    displayQuiz(questions) {
        const quizContent = document.getElementById('quiz-content');
        let currentQuestion = 0;
        let score = 0;
        let answers = [];

        const showQuestion = (index) => {
            if (index >= questions.length) {
                this.showQuizResults(score, questions.length, answers);
                return;
            }

            const q = questions[index];
            quizContent.innerHTML = `
                <div class="quiz-question">
                    <h4>Question ${index + 1} of ${questions.length}</h4>
                    <p style="font-size: 1.1rem; margin: 1rem 0;">${q.question}</p>
                    <ul class="quiz-options">
                        ${Object.entries(q.options).map(([key, value]) => `
                            <li data-option="${key}">${key}. ${value}</li>
                        `).join('')}
                    </ul>
                    <div style="margin-top: 2rem;">
                        <button id="submit-answer" class="btn-primary" disabled>Submit Answer</button>
                    </div>
                    <div id="answer-feedback"></div>
                </div>
            `;

            let selectedOption = null;

            quizContent.querySelectorAll('.quiz-options li').forEach(li => {
                li.addEventListener('click', function () {
                    quizContent.querySelectorAll('.quiz-options li').forEach(item => {
                        item.classList.remove('selected');
                    });
                    this.classList.add('selected');
                    selectedOption = this.dataset.option;
                    document.getElementById('submit-answer').disabled = false;
                });
            });

            document.getElementById('submit-answer').addEventListener('click', () => {
                if (!selectedOption) return;

                const correct = selectedOption === q.correct;
                if (correct) score++;

                answers.push({
                    question: q.question,
                    selected: selectedOption,
                    correct: q.correct,
                    isCorrect: correct
                });

                quizContent.querySelectorAll('.quiz-options li').forEach(li => {
                    li.style.pointerEvents = 'none';
                    if (li.dataset.option === q.correct) {
                        li.classList.add('correct');
                    } else if (li.dataset.option === selectedOption && !correct) {
                        li.classList.add('incorrect');
                    }
                });

                const feedback = document.getElementById('answer-feedback');
                feedback.innerHTML = `
                    <div class="ethical-note" style="margin-top: 1rem; ${correct ? 'border-left-color: var(--success-green);' : ''}">
                        <strong>${correct ? '✓ Correct!' : '✗ Incorrect'}</strong>
                        <p>${q.explanation}</p>
                        <button onclick="app.nextQuizQuestion(${index + 1})" class="btn-primary" style="margin-top: 1rem;">
                            ${index + 1 < questions.length ? 'Next Question →' : 'See Results'}
                        </button>
                    </div>
                `;
            });
        };

        // Store state for next question navigation
        this.quizState = { questions, showQuestion, score, answers };
        showQuestion(0);
    }

    nextQuizQuestion(index) {
        if (this.quizState) {
            this.quizState.showQuestion(index);
        }
    }

    showQuizResults(score, total, answers) {
        const quizContent = document.getElementById('quiz-content');
        const percentage = (score / total * 100).toFixed(0);

        // --- FIX: Safely determine the topic name for the history ---
        const manualTopic = document.getElementById('quiz-topic-manual')?.value.trim();
        const dropdownElement = document.getElementById('quiz-topic-dropdown');
        const selectedText = dropdownElement?.options[dropdownElement.selectedIndex]?.text;

        // Priority: Manual Input > Dropdown Selection > Current Concept > Fallback
        const historyTopicName = manualTopic || selectedText || (this.currentConcept ? ForensicKnowledge.concepts[this.currentConcept].name : "General Forensics");

        // Create the history object
        const historyItem = {
            topic: historyTopicName,
            score: score,
            total: total,
            percent: percentage,
            date: new Date().toLocaleString(),
            difficulty: document.getElementById('quiz-difficulty')?.value || 'intermediate'
        };

        // Save to our local array and localStorage
        if (!this.userProgress.history) this.userProgress.history = [];
        this.userProgress.history.unshift(historyItem);
        this.saveProgress();

        let feedback = '';
        if (percentage >= 80) {
            feedback = '🌟 Excellent work! You have a strong understanding of this concept.';
        } else if (percentage >= 60) {
            feedback = '👍 Good job! Review the questions you missed to strengthen your knowledge.';
        } else {
            feedback = '📚 Keep studying! Review the concept material and try again.';
        }

        quizContent.innerHTML = `
            <div class="concept-card">
                <h3>Quiz Results: ${historyTopicName}</h3>
                <div style="text-align: center; font-size: 3rem; margin: 2rem 0; color: var(--accent-cyan);">
                    ${score} / ${total}
                </div>
                <div style="text-align: center; font-size: 1.5rem; margin: 1rem 0;">
                    ${percentage}%
                </div>
                <p style="text-align: center; font-size: 1.1rem; margin: 2rem 0;">
                    ${feedback}
                </p>
                
                <h4>Review Your Answers:</h4>
                ${answers.map((a, i) => `
                    <div style="margin: 1rem 0; padding: 1rem; background: ${a.isCorrect ? 'rgba(46, 204, 113, 0.1)' : 'rgba(220, 20, 60, 0.1)'}; border-radius: 6px;">
                        <strong>Q${i + 1}:</strong> ${a.question}<br>
                        <strong>Your answer:</strong> ${a.selected} ${a.isCorrect ? '✓' : '✗'}<br>
                        ${!a.isCorrect ? `<strong>Correct answer:</strong> ${a.correct}` : ''}
                    </div>
                `).join('')}
                
                <div style="margin-top: 2rem; text-align: center;">
                    <button onclick="app.generateQuiz()" class="btn-primary">Generate New Quiz</button>
                    <button onclick="app.switchMode('concepts')" class="btn-primary">Back to Concepts</button>
                </div>
            </div>
        `;

        // // Update user progress
        // this.userProgress.quizzes.push({
        //     concept: this.currentConcept,
        //     score: percentage,
        //     date: new Date().toISOString()
        // });
        // this.saveProgress();
        // Add a call to refresh the history table
        this.displayHistory();
    }

    displayHistory() {
        const container = document.getElementById('quiz-history-list');
        if (!container || !this.userProgress.history || this.userProgress.history.length === 0) return;

        let html = `
        <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
            <thead>
                <tr style="border-bottom: 2px solid var(--accent-cyan); text-align: left;">
                    <th style="padding: 10px;">Date</th>
                    <th style="padding: 10px;">Topic</th>
                    <th style="padding: 10px;">Difficulty</th>
                    <th style="padding: 10px;">Score</th>
                </tr>
            </thead>
            <tbody>
    `;

        // Show last 5-10 items
        this.userProgress.history.slice(0, 10).forEach(item => {
            html += `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 10px; font-size: 0.8rem;">${item.date}</td>
                <td style="padding: 10px;">${item.topic}</td>
                <td style="padding: 10px; text-transform: capitalize;">${item.difficulty}</td>
                <td style="padding: 10px;">
                    <strong style="color: ${item.percent >= 70 ? '#2ecc71' : '#e74c3c'}">
                        ${item.score}/${item.total} (${item.percent}%)
                    </strong>
                </td>
            </tr>
        `;
        });

        html += `</tbody></table>`;
        container.innerHTML = html;
    }

    // ====================================
    // Socratic Dialogue
    // ====================================

    initializeSocraticDialogue() {
        const chatContainer = document.getElementById('socratic-chat');
        if (!chatContainer) return;

        if (chatContainer.children.length === 0) {
            this.addChatMessage('ai', `Welcome! I'm ${AIPersonas.personas[this.currentPersona].name}. Let's explore forensic concepts together through dialogue. What concept would you like to discuss?`);
        }
    }

    async sendSocraticMessage() {
        const input = document.getElementById('socratic-input');
        if (!input || !input.value.trim()) return;

        const userMessage = input.value.trim();
        input.value = '';

        if (!this.llmConnected) {
            this.showNotification('Please connect to Ollama first', 'warning');
            return;
        }

        this.addChatMessage('user', userMessage);
        this.conversationHistory.push({ role: 'user', content: userMessage });

        // Determine if this is the start or continuation
        let prompt;
        if (this.conversationHistory.length <= 1) {
            // Starting conversation
            const userLevel = this.estimateUserLevel();
            prompt = AIPersonas.generateSocraticPrompt(userMessage, userLevel);
        } else {
            // Continuing conversation
            const personaData = AIPersonas.personas[this.currentPersona];
            const context = this.conversationHistory.slice(-5).map(m =>
                `${m.role === 'user' ? 'Student' : personaData.name}: ${m.content}`
            ).join('\n\n');

            prompt = `${personaData.systemPrompt}\n\nConversation so far:\n${context}\n\nContinue the Socratic dialogue based on the student's latest response.`;
        }

        const chatContainer = document.getElementById('socratic-chat');
        const thinkingMsg = this.addChatMessage('ai', '<span class="thinking">Thinking</span>');

        const result = await OllamaInterface.generate(prompt);

        thinkingMsg.remove();

        if (result.success) {
            this.addChatMessage('ai', result.response);
            this.conversationHistory.push({ role: 'assistant', content: result.response });
        } else {
            this.addChatMessage('ai', 'I apologize, I encountered an error. Please try again.');
        }
    }

    addChatMessage(sender, content) {
        const chatContainer = document.getElementById('socratic-chat');
        if (!chatContainer) return null;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const personaName = sender === 'ai' ? AIPersonas.personas[this.currentPersona].name : 'You';

        messageDiv.innerHTML = `
            <strong>${personaName}</strong>
            ${this.formatAIResponse(content)}
        `;

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return messageDiv;
    }

    // ====================================
    // Simulations
    // ====================================

    loadSimulations() {
        const simulationList = document.getElementById('simulation-list');
        if (!simulationList) return;

        simulationList.innerHTML = '';

        ForensicKnowledge.simulations.forEach(sim => {
            const card = document.createElement('div');
            card.className = 'simulation-card';
            card.innerHTML = `
                <h3>${sim.title}</h3>
                <p>${sim.description}</p>
                <span class="simulation-difficulty difficulty-${sim.difficulty}">
                    ${sim.difficulty.toUpperCase()}
                </span>
            `;
            card.addEventListener('click', () => this.startSimulation(sim));
            simulationList.appendChild(card);
        });
    }

    async startSimulation(simulation) {
        if (!this.llmConnected) {
            this.showNotification('Simulations require AI connection', 'warning');
            return;
        }

        this.currentSimulation = {
            ...simulation,
            currentState: { ...simulation.initialState },
            history: []
        };

        const workspace = document.getElementById('active-simulation');
        workspace.innerHTML = `
            <div class="concept-card">
                <h3>${simulation.title}</h3>
                <p>${simulation.description}</p>
                <div id="sim-narrative"></div>
                <div id="sim-choices"></div>
                <button onclick="app.loadSimulations()" class="btn-small" style="margin-top: 1rem;">
                    ← Back to Simulations
                </button>
            </div>
        `;

        // Start simulation
        this.updateSimulation("BEGIN");
    }

    async updateSimulation(userAction) {
        const prompt = AIPersonas.generateCaseSimulationPrompt(this.currentSimulation, userAction);

        const narrative = document.getElementById('sim-narrative');
        narrative.innerHTML = '<div class="loading"></div><p class="thinking">Processing your decision...</p>';

        const result = await OllamaInterface.generate(prompt, { temperature: 0.8 });

        if (result.success) {
            try {
                let jsonText = result.response.trim();
                jsonText = jsonText.replace(/```json\n?/g, '').replace(/```\n?/g, '');
                const simData = JSON.parse(jsonText);

                narrative.innerHTML = `
                    <div class="case-example" style="margin: 1rem 0;">
                        ${simData.narrative}
                    </div>
                    ${simData.consequences.length > 0 ? `
                        <div style="margin: 1rem 0;">
                            <strong>Consequences:</strong>
                            <ul>
                                ${simData.consequences.map(c => `<li>${c}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${simData.feedback ? `
                        <div class="ethical-note">
                            <strong>Feedback:</strong> ${simData.feedback}
                        </div>
                    ` : ''}
                `;

                const choices = document.getElementById('sim-choices');
                choices.innerHTML = `
                    <h4 style="margin-top: 2rem;">What will you do?</h4>
                    ${simData.nextChoices.map((choice, i) => `
                        <button 
                            onclick="app.updateSimulation('${choice.option.replace(/'/g, "\\'")}')" 
                            class="btn-primary"
                            style="display: block; width: 100%; margin: 0.5rem 0; text-align: left;"
                        >
                            ${choice.option} <span style="float: right; font-size: 0.8rem;">[${choice.risk} risk]</span>
                        </button>
                    `).join('')}
                `;

                // Update simulation state
                Object.assign(this.currentSimulation.currentState, simData.stateUpdate || {});
                this.currentSimulation.history.push({ action: userAction, result: simData });

            } catch (error) {
                console.error('Simulation parsing error:', error);
                narrative.innerHTML = `<p>Error processing simulation. Raw response: ${result.response}</p>`;
            }
        }
    }

    // ====================================
    // Ollama Connection
    // ====================================

    async checkOllamaConnection() {
        const result = await OllamaInterface.testConnection();

        if (result.success) {
            this.llmConnected = true;
            this.updateConnectionStatus(true);
            console.log('Ollama models available:', result.models);
        } else {
            this.llmConnected = false;
            this.updateConnectionStatus(false);
        }
    }

    async connectOllama() {
        this.showNotification('Connecting to Ollama...', 'info');
        await this.checkOllamaConnection();

        if (this.llmConnected) {
            this.showNotification('Connected to Ollama successfully!', 'success');
        } else {
            this.showNotification('Failed to connect. Make sure Ollama is running on localhost:11434', 'error');
        }
    }

    updateConnectionStatus(connected) {
        const status = document.getElementById('llm-status');
        if (status) {
            status.className = `status-indicator ${connected ? 'online' : 'offline'}`;
            status.textContent = `LLM: ${connected ? 'Connected' : 'Disconnected'}`;
        }

        const connectBtn = document.getElementById('connect-llm');
        if (connectBtn) {
            connectBtn.textContent = connected ? 'Reconnect' : 'Connect to Ollama';
        }
    }

    // ====================================
    // Settings Management
    // ====================================

    saveSettings() {
        const settings = {
            url: document.getElementById('ollama-url')?.value || 'http://localhost:11434',
            model: document.getElementById('ollama-model')?.value || 'llama3.2',
            temperature: parseFloat(document.getElementById('temperature')?.value) || 0.7
        };

        OllamaInterface.updateSettings(settings);
        localStorage.setItem('forensic-llm-settings', JSON.stringify(settings));

        this.showNotification('Settings saved!', 'success');
        this.checkOllamaConnection();
    }

    restoreSettings() {
        const saved = localStorage.getItem('forensic-llm-settings');
        if (saved) {
            const settings = JSON.parse(saved);

            if (document.getElementById('ollama-url')) {
                document.getElementById('ollama-url').value = settings.url;
            }
            if (document.getElementById('ollama-model')) {
                document.getElementById('ollama-model').value = settings.model;
            }
            if (document.getElementById('temperature')) {
                document.getElementById('temperature').value = settings.temperature;
                document.getElementById('temp-value').textContent = settings.temperature;
            }

            OllamaInterface.updateSettings(settings);
        }
    }

    // ====================================
    // User Progress
    // ====================================

    loadProgress() {
        const saved = localStorage.getItem('forensic-user-progress');
        if (saved) {
            return JSON.parse(saved);
        }

        return {
            viewed: [],
            completed: [],
            quizzes: [],
            lastAccess: new Date().toISOString()
        };
    }

    saveProgress() {
        this.userProgress.lastAccess = new Date().toISOString();
        localStorage.setItem('forensic-user-progress', JSON.stringify(this.userProgress));
    }

    estimateUserLevel() {
        const completedCount = this.userProgress.completed.length;
        const avgQuizScore = this.userProgress.quizzes.length > 0
            ? this.userProgress.quizzes.reduce((sum, q) => sum + q.score, 0) / this.userProgress.quizzes.length
            : 0;

        if (completedCount < 3 || avgQuizScore < 60) {
            return 'beginner';
        } else if (completedCount < 8 || avgQuizScore < 80) {
            return 'intermediate';
        } else {
            return 'advanced';
        }
    }

    // ====================================
    // Wikipedia Integration
    // ====================================

    searchWikipedia() {
        const input = document.getElementById('wiki-input');
        if (!input || !input.value.trim()) return;

        const query = encodeURIComponent(input.value.trim());
        const url = `https://en.wikipedia.org/wiki/Special:Search?search=${query}`;

        window.open(url, '_blank');

        const modal = document.getElementById('wiki-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    // ====================================
    // Utility Functions
    // ====================================

    formatAIResponse(text) {
        // Convert markdown-style formatting to HTML
        let formatted = text
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        return `<p>${formatted}</p>`;
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? 'var(--success-green)' : type === 'error' ? 'var(--evidence-red)' : 'var(--accent-cyan)'};
            color: white;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize the application when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ForensicLearningSystem();
});
