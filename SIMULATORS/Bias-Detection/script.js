// Data Generation
        class ForensicDataGenerator {
            constructor() {
                this.groups = {
                    male: {
                        name: 'MALE SUBJECTS',
                        truthfulMean: 0.35,
                        truthfulStd: 0.12,
                        deceptiveMean: 0.72,
                        deceptiveStd: 0.14,
                        color: '#00d4ff'
                    },
                    female: {
                        name: 'FEMALE SUBJECTS',
                        truthfulMean: 0.42,
                        truthfulStd: 0.13,
                        deceptiveMean: 0.70,
                        deceptiveStd: 0.13,
                        color: '#ff0000'
                    },
                    trauma: {
                        name: 'TRAUMA HISTORY',
                        truthfulMean: 0.48,
                        truthfulStd: 0.15,
                        deceptiveMean: 0.71,
                        deceptiveStd: 0.12,
                        color: '#ff6b35'
                    },
                    cultural: {
                        name: 'CULTURAL MINORITY',
                        truthfulMean: 0.45,
                        truthfulStd: 0.14,
                        deceptiveMean: 0.69,
                        deceptiveStd: 0.15,
                        color: '#00ff41'
                    }
                };
            }

            normalRandom(mean, std) {
                const u1 = Math.random();
                const u2 = Math.random();
                const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
                return Math.max(0, Math.min(1, mean + z * std));
            }

            generateDistribution(group, size = 200) {
                const data = {
                    truthful: [],
                    deceptive: []
                };

                for (let i = 0; i < size; i++) {
                    data.truthful.push(this.normalRandom(group.truthfulMean, group.truthfulStd));
                    data.deceptive.push(this.normalRandom(group.deceptiveMean, group.deceptiveStd));
                }

                return data;
            }

            calculateMetrics(truthful, deceptive, threshold) {
                const trueNegatives = truthful.filter(v => v < threshold).length;
                const falsePositives = truthful.filter(v => v >= threshold).length;
                const truePositives = deceptive.filter(v => v >= threshold).length;
                const falseNegatives = deceptive.filter(v => v < threshold).length;

                const total = truthful.length + deceptive.length;
                const accuracy = (truePositives + trueNegatives) / total;
                const fpr = falsePositives / (falsePositives + trueNegatives);
                const fnr = falseNegatives / (falseNegatives + truePositives);
                const precision = truePositives / (truePositives + falsePositives);
                const recall = truePositives / (truePositives + falseNegatives);

                return {
                    accuracy: (accuracy * 100).toFixed(1),
                    fpr: (fpr * 100).toFixed(1),
                    fnr: (fnr * 100).toFixed(1),
                    precision: (precision * 100).toFixed(1),
                    recall: (recall * 100).toFixed(1),
                    tp: truePositives,
                    fp: falsePositives,
                    tn: trueNegatives,
                    fn: falseNegatives
                };
            }
        }

        const dataGen = new ForensicDataGenerator();
        let currentThreshold = 0.65;
        let currentGroup = 'all';
        let currentVizMode = 'scatter';
        let mainChart = null;
        let groupData = {};

        // Generate initial data
        function initializeData() {
            for (const [key, group] of Object.entries(dataGen.groups)) {
                groupData[key] = dataGen.generateDistribution(group);
            }
            updateUI();
        }

        // Update Evidence Cards
        function updateEvidenceCards() {
            const container = document.getElementById('evidenceGrid');
            container.innerHTML = '';

            for (const [key, group] of Object.entries(dataGen.groups)) {
                const metrics = dataGen.calculateMetrics(
                    groupData[key].truthful,
                    groupData[key].deceptive,
                    currentThreshold
                );

                const card = document.createElement('div');
                card.className = `evidence-card ${currentGroup === key ? 'active' : ''}`;
                card.onclick = () => {
                    currentGroup = key;
                    document.getElementById('groupSelector').value = key;
                    updateUI();
                };

                const fprClass = parseFloat(metrics.fpr) > 20 ? 'danger' : parseFloat(metrics.fpr) > 10 ? 'warning' : 'safe';
                const accClass = parseFloat(metrics.accuracy) > 80 ? 'safe' : parseFloat(metrics.accuracy) > 70 ? 'warning' : 'danger';

                card.innerHTML = `
                    <div class="evidence-header">
                        <div class="evidence-title">${group.name}</div>
                        <div style="color: ${group.color};">●</div>
                    </div>
                    <div class="evidence-metrics">
                        <div class="metric">
                            <div class="metric-label">FALSE POSITIVE</div>
                            <div class="metric-value ${fprClass}">${metrics.fpr}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">ACCURACY</div>
                            <div class="metric-value ${accClass}">${metrics.accuracy}%</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0, 212, 255, 0.2); font-size: 0.85rem; color: var(--terminal-text); opacity: 0.8;">
                        TP: ${metrics.tp} | FP: ${metrics.fp} | TN: ${metrics.tn} | FN: ${metrics.fn}
                    </div>
                `;

                container.appendChild(card);
            }
        }

        // Update Findings
        function updateFindings() {
            const container = document.getElementById('findingsGrid');
            const metrics = {};
            
            for (const [key, group] of Object.entries(dataGen.groups)) {
                metrics[key] = dataGen.calculateMetrics(
                    groupData[key].truthful,
                    groupData[key].deceptive,
                    currentThreshold
                );
            }

            const genderBias = ((parseFloat(metrics.female.fpr) - parseFloat(metrics.male.fpr)) / parseFloat(metrics.male.fpr) * 100).toFixed(0);
            const traumaImpact = metrics.trauma.fpr;
            const maxFPR = Math.max(...Object.values(metrics).map(m => parseFloat(m.fpr)));
            const minFPR = Math.min(...Object.values(metrics).map(m => parseFloat(m.fpr)));
            const fprRange = ((maxFPR - minFPR) / minFPR * 100).toFixed(0);

            const findings = [
                {
                    title: '⚠ GENDER DISCRIMINATION DETECTED',
                    text: `Female subjects exhibit ${Math.abs(genderBias)}% ${genderBias > 0 ? 'higher' : 'lower'} false positive rates compared to male subjects at current threshold (${currentThreshold}). This disparity aligns with documented sex differences in physiological stress responses, including elevated baseline cortisol and heightened sympathetic nervous system reactivity in females during interrogation scenarios.`
                },
                {
                    title: '🔴 TRAUMA SURVIVOR VULNERABILITY',
                    text: `Individuals with trauma history show ${traumaImpact}% false positive rate, meaning nearly 1 in ${Math.round(100/parseFloat(traumaImpact))} truthful statements are incorrectly flagged as deceptive. Trauma-related hypervigilance, exaggerated startle responses, and chronic dysregulation of the HPA axis create physiological signatures that mimic deception, creating severe injustice for victims.`
                },
                {
                    title: '🌍 CULTURAL BIAS PATTERNS',
                    text: `Cultural minority subjects demonstrate distinct physiological patterns, with ${metrics.cultural.fpr}% false positive rate. This may reflect increased anxiety during interrogation (authority-figure stress), culturally-specific emotional expression norms, or interviewer bias effects. Cross-cultural validation of deception detection tools is critically lacking.`
                },
                {
                    title: '⚖ THRESHOLD PARADOX',
                    text: `The ${fprRange}% variation in false positive rates across groups reveals an impossible dilemma: No single decision threshold achieves equitable outcomes. Lowering the threshold to reduce false positives for trauma survivors increases false negatives for all groups. Group-specific calibration or complete abandonment of these tools may be ethically necessary.`
                }
            ];

            container.innerHTML = findings.map(f => `
                <div class="finding-box">
                    <div class="finding-title">${f.title}</div>
                    <div class="finding-text">${f.text}</div>
                </div>
            `).join('');
        }

        // Chart Rendering
        function renderChart() {
            const ctx = document.getElementById('mainChart');
            if (mainChart) {
                mainChart.destroy();
            }

            switch(currentVizMode) {
                case 'scatter':
                    renderScatterChart(ctx);
                    break;
                case 'comparison':
                    renderComparisonChart(ctx);
                    break;
                case 'roc':
                    renderROCChart(ctx);
                    break;
                case 'confusion':
                    renderConfusionMatrix(ctx);
                    break;
            }
        }

        function renderScatterChart(ctx) {
            const datasets = [];
            const groupsToShow = currentGroup === 'all' ? Object.keys(dataGen.groups) : [currentGroup];

            for (const key of groupsToShow) {
                const group = dataGen.groups[key];
                const data = groupData[key];

                // Truthful points
                datasets.push({
                    label: `${group.name} - Truthful`,
                    data: data.truthful.map((v, i) => ({ x: v, y: 0.3 + Math.random() * 0.2 })),
                    backgroundColor: group.color + '80',
                    borderColor: group.color,
                    pointRadius: 3,
                    pointHoverRadius: 5
                });

                // Deceptive points
                datasets.push({
                    label: `${group.name} - Deceptive`,
                    data: data.deceptive.map((v, i) => ({ x: v, y: 0.6 + Math.random() * 0.2 })),
                    backgroundColor: group.color + '40',
                    borderColor: group.color,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointStyle: 'triangle'
                });
            }

            mainChart = new Chart(ctx, {
                type: 'scatter',
                data: { datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#e5e7eb', font: { family: 'Share Tech Mono' } }
                        },
                        title: {
                            display: true,
                            text: 'PHYSIOLOGICAL RESPONSE DISTRIBUTION',
                            color: '#00d4ff',
                            font: { family: 'Share Tech Mono', size: 16 }
                        },
                        annotation: {
                            annotations: {
                                threshold: {
                                    type: 'line',
                                    xMin: currentThreshold,
                                    xMax: currentThreshold,
                                    borderColor: '#ffd700',
                                    borderWidth: 2,
                                    borderDash: [5, 5],
                                    label: {
                                        content: `THRESHOLD: ${currentThreshold}`,
                                        enabled: true,
                                        position: 'start',
                                        color: '#ffd700',
                                        backgroundColor: 'rgba(0, 0, 0, 0.8)'
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: { display: true, text: 'Physiological Response Score', color: '#e5e7eb' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' }
                        },
                        y: {
                            title: { display: true, text: 'Distribution', color: '#e5e7eb' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' }
                        }
                    }
                }
            });
        }

        function renderComparisonChart(ctx) {
            const labels = [];
            const fprData = [];
            const accData = [];

            for (const [key, group] of Object.entries(dataGen.groups)) {
                const metrics = dataGen.calculateMetrics(
                    groupData[key].truthful,
                    groupData[key].deceptive,
                    currentThreshold
                );
                labels.push(group.name);
                fprData.push(parseFloat(metrics.fpr));
                accData.push(parseFloat(metrics.accuracy));
            }

            mainChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'False Positive Rate (%)',
                            data: fprData,
                            backgroundColor: '#ff0000',
                            borderColor: '#ff0000',
                            borderWidth: 2
                        },
                        {
                            label: 'Accuracy (%)',
                            data: accData,
                            backgroundColor: '#00ff41',
                            borderColor: '#00ff41',
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#e5e7eb', font: { family: 'Share Tech Mono' } }
                        },
                        title: {
                            display: true,
                            text: 'BIAS COMPARISON ANALYSIS',
                            color: '#00d4ff',
                            font: { family: 'Share Tech Mono', size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb', font: { size: 10 } }
                        },
                        y: {
                            title: { display: true, text: 'Percentage (%)', color: '#e5e7eb' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' }
                        }
                    }
                }
            });
        }

        function renderROCChart(ctx) {
            const thresholds = Array.from({ length: 20 }, (_, i) => i / 19);
            const datasets = [];

            for (const [key, group] of Object.entries(dataGen.groups)) {
                const rocPoints = thresholds.map(t => {
                    const m = dataGen.calculateMetrics(
                        groupData[key].truthful,
                        groupData[key].deceptive,
                        t
                    );
                    return {
                        x: parseFloat(m.fpr) / 100,
                        y: parseFloat(m.recall) / 100
                    };
                });

                datasets.push({
                    label: group.name,
                    data: rocPoints,
                    borderColor: group.color,
                    backgroundColor: group.color + '20',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0
                });
            }

            // Add diagonal reference
            datasets.push({
                label: 'Random Classifier',
                data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
                borderColor: '#64748b',
                borderWidth: 1,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0
            });

            mainChart = new Chart(ctx, {
                type: 'line',
                data: { datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#e5e7eb', font: { family: 'Share Tech Mono' } }
                        },
                        title: {
                            display: true,
                            text: 'ROC CURVE - PERFORMANCE ACROSS THRESHOLDS',
                            color: '#00d4ff',
                            font: { family: 'Share Tech Mono', size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            title: { display: true, text: 'False Positive Rate', color: '#e5e7eb' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' },
                            min: 0,
                            max: 1
                        },
                        y: {
                            title: { display: true, text: 'True Positive Rate', color: '#e5e7eb' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' },
                            min: 0,
                            max: 1
                        }
                    }
                }
            });
        }

        function renderConfusionMatrix(ctx) {
            const groupKey = currentGroup === 'all' ? 'male' : currentGroup;
            const metrics = dataGen.calculateMetrics(
                groupData[groupKey].truthful,
                groupData[groupKey].deceptive,
                currentThreshold
            );

            const confusionData = [
                { x: 'Predicted: Truthful', y: 'Actual: Truthful', value: metrics.tn, label: `TN: ${metrics.tn}` },
                { x: 'Predicted: Deceptive', y: 'Actual: Truthful', value: metrics.fp, label: `FP: ${metrics.fp}` },
                { x: 'Predicted: Truthful', y: 'Actual: Deceptive', value: metrics.fn, label: `FN: ${metrics.fn}` },
                { x: 'Predicted: Deceptive', y: 'Actual: Deceptive', value: metrics.tp, label: `TP: ${metrics.tp}` }
            ];

            mainChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Predicted: Truthful', 'Predicted: Deceptive'],
                    datasets: [
                        {
                            label: 'Actual: Truthful',
                            data: [metrics.tn, metrics.fp],
                            backgroundColor: ['#00ff41', '#ff0000'],
                            borderColor: ['#00ff41', '#ff0000'],
                            borderWidth: 2
                        },
                        {
                            label: 'Actual: Deceptive',
                            data: [metrics.fn, metrics.tp],
                            backgroundColor: ['#ff6b35', '#00d4ff'],
                            borderColor: ['#ff6b35', '#00d4ff'],
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#e5e7eb', font: { family: 'Share Tech Mono' } }
                        },
                        title: {
                            display: true,
                            text: `CONFUSION MATRIX - ${dataGen.groups[groupKey].name}`,
                            color: '#00d4ff',
                            font: { family: 'Share Tech Mono', size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' }
                        },
                        y: {
                            title: { display: true, text: 'Count', color: '#e5e7eb' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                            ticks: { color: '#e5e7eb' }
                        }
                    }
                }
            });
        }

        // AI Integration
        async function analyzeWithAI() {
            const query = document.getElementById('aiQuery').value.trim();
            const responseDiv = document.getElementById('aiResponse');
            const analyzeBtn = document.getElementById('analyzeBtn');

            if (!query) {
                alert('⚠ Please enter a forensic analysis query');
                return;
            }

            analyzeBtn.disabled = true;
            responseDiv.innerHTML = '<span class="loading">⚡ ANALYZING... AI ENGINE PROCESSING REQUEST...</span>';

            // Gather current system state for context
            const context = {
                threshold: currentThreshold,
                group: currentGroup,
                metrics: {}
            };

            for (const [key, group] of Object.entries(dataGen.groups)) {
                context.metrics[key] = dataGen.calculateMetrics(
                    groupData[key].truthful,
                    groupData[key].deceptive,
                    currentThreshold
                );
            }

            const systemPrompt = `You are a forensic psychologist and AI ethics expert analyzing bias in deception detection systems. 

CURRENT SYSTEM STATE:
- Decision Threshold: ${currentThreshold}
- Active Group: ${currentGroup}
- Metrics: ${JSON.stringify(context.metrics, null, 2)}

Provide detailed, evidence-based analysis focusing on:
1. Statistical patterns and their implications
2. Ethical concerns and victim perspectives
3. Neurobiological mechanisms underlying bias
4. Practical recommendations

Be direct, scientific, and clear. Use specific numbers from the data.`;

            try {
                const response = await fetch('http://localhost:11434/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'llama3.2',
                        prompt: `${systemPrompt}\n\nUSER QUERY: ${query}`,
                        stream: false
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to connect to Ollama. Ensure Ollama is running on localhost:11434');
                }

                const data = await response.json();
                
                responseDiv.innerHTML = `<span style="color: var(--clearance-green);">🤖 AI FORENSIC ANALYSIS:</span>\n\n${data.response}`;
                
            } catch (error) {
                responseDiv.innerHTML = `<span style="color: var(--evidence-red);">❌ ERROR: ${error.message}</span>\n\nTroubleshooting:\n1. Ensure Ollama is installed and running\n2. Check that llama3.2 model is available (run: ollama pull llama3.2)\n3. Verify Ollama is accessible at http://localhost:11434\n4. Check browser console for detailed error logs`;
                console.error('Ollama error:', error);
            } finally {
                analyzeBtn.disabled = false;
            }
        }

        async function generateReport() {
            const responseDiv = document.getElementById('aiResponse');
            responseDiv.innerHTML = '<span class="loading">📋 GENERATING COMPREHENSIVE FORENSIC REPORT...</span>';

            const context = {
                threshold: currentThreshold,
                metrics: {}
            };

            for (const [key, group] of Object.entries(dataGen.groups)) {
                context.metrics[key] = dataGen.calculateMetrics(
                    groupData[key].truthful,
                    groupData[key].deceptive,
                    currentThreshold
                );
            }

            const reportPrompt = `Generate a comprehensive forensic report analyzing bias in this deception detection system.

DATA:
${JSON.stringify(context.metrics, null, 2)}
Threshold: ${currentThreshold}

Include:
1. Executive Summary
2. Statistical Analysis of Bias Patterns
3. Neurobiological Mechanisms
4. Ethical Implications
5. Recommendations for Reform
6. Victim Impact Assessment

Format as a professional forensic report with clear sections.`;

            try {
                const response = await fetch('http://localhost:11434/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'llama3.2',
                        prompt: reportPrompt,
                        stream: false
                    })
                });

                const data = await response.json();
                responseDiv.innerHTML = `<span style="color: var(--crime-yellow);">📋 FORENSIC REPORT - CASE #FBD-2026-001</span>\n\n${data.response}`;
                
            } catch (error) {
                responseDiv.innerHTML = `<span style="color: var(--evidence-red);">❌ ERROR: ${error.message}</span>`;
            }
        }

        // Event Listeners
        document.getElementById('thresholdSlider').addEventListener('input', (e) => {
            currentThreshold = parseFloat(e.target.value);
            document.getElementById('thresholdValue').textContent = currentThreshold.toFixed(2);
            updateUI();
        });

        document.getElementById('groupSelector').addEventListener('change', (e) => {
            currentGroup = e.target.value;
            updateUI();
        });

        document.getElementById('vizMode').addEventListener('change', (e) => {
            currentVizMode = e.target.value;
            const vizNames = {
                scatter: 'PHYSIOLOGICAL DISTRIBUTION',
                comparison: 'BIAS COMPARISON',
                roc: 'ROC CURVE ANALYSIS',
                confusion: 'CONFUSION MATRIX'
            };
            document.getElementById('currentViz').textContent = vizNames[currentVizMode];
            renderChart();
        });

        document.getElementById('aiQuery').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                analyzeWithAI();
            }
        });

        function updateUI() {
            updateEvidenceCards();
            updateFindings();
            renderChart();
        }

        // Initialize
        initializeData();