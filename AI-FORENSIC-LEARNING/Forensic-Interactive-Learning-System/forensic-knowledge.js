// ====================================
// Forensic Knowledge Base
// Structured knowledge for retrieval and reasoning
// ====================================

const ForensicKnowledge = {
    // Core curriculum structure with 15 fundamental concepts
    curriculum: [
        {
            id: 'locards-principle',
            title: "Locard's Exchange Principle",
            category: 'foundational',
            difficulty: 'beginner',
            keywords: ['trace evidence', 'transfer', 'contact', 'exchange']
        },
        {
            id: 'chain-of-custody',
            title: 'Chain of Custody',
            category: 'procedural',
            difficulty: 'beginner',
            keywords: ['evidence', 'documentation', 'integrity', 'admissibility']
        },
        {
            id: 'modus-operandi',
            title: 'Modus Operandi (MO)',
            category: 'behavioral',
            difficulty: 'intermediate',
            keywords: ['behavior', 'pattern', 'method', 'signature']
        },
        {
            id: 'crime-scene-management',
            title: 'Crime Scene Management',
            category: 'procedural',
            difficulty: 'beginner',
            keywords: ['preservation', 'documentation', 'search patterns', 'contamination']
        },
        {
            id: 'fingerprint-analysis',
            title: 'Fingerprint Analysis',
            category: 'physical-evidence',
            difficulty: 'intermediate',
            keywords: ['biometrics', 'patterns', 'identification', 'comparison']
        },
        {
            id: 'dna-forensics',
            title: 'DNA Forensic Analysis',
            category: 'biological-evidence',
            difficulty: 'advanced',
            keywords: ['genetics', 'STR', 'PCR', 'probability']
        },
        {
            id: 'bloodstain-pattern',
            title: 'Bloodstain Pattern Analysis',
            category: 'physical-evidence',
            difficulty: 'intermediate',
            keywords: ['trajectory', 'velocity', 'physics', 'reconstruction']
        },
        {
            id: 'forensic-toxicology',
            title: 'Forensic Toxicology',
            category: 'biological-evidence',
            difficulty: 'advanced',
            keywords: ['drugs', 'poisons', 'metabolism', 'screening']
        },
        {
            id: 'digital-forensics',
            title: 'Digital Forensics',
            category: 'digital-evidence',
            difficulty: 'intermediate',
            keywords: ['data recovery', 'metadata', 'encryption', 'chain of custody']
        },
        {
            id: 'ballistics',
            title: 'Forensic Ballistics',
            category: 'physical-evidence',
            difficulty: 'intermediate',
            keywords: ['firearms', 'trajectory', 'striations', 'GSR']
        },
        {
            id: 'forensic-entomology',
            title: 'Forensic Entomology',
            category: 'biological-evidence',
            difficulty: 'advanced',
            keywords: ['insects', 'PMI', 'decomposition', 'succession']
        },
        {
            id: 'questioned-documents',
            title: 'Questioned Document Examination',
            category: 'physical-evidence',
            difficulty: 'intermediate',
            keywords: ['handwriting', 'forgery', 'ink analysis', 'authentication']
        },
        {
            id: 'impression-evidence',
            title: 'Impression Evidence',
            category: 'physical-evidence',
            difficulty: 'beginner',
            keywords: ['shoe prints', 'tire tracks', 'tool marks', 'casting']
        },
        {
            id: 'forensic-psychology',
            title: 'Forensic Psychology',
            category: 'behavioral',
            difficulty: 'advanced',
            keywords: ['profiling', 'competency', 'testimony', 'mental state']
        },
        {
            id: 'expert-testimony',
            title: 'Expert Witness Testimony',
            category: 'legal',
            difficulty: 'advanced',
            keywords: ['daubert', 'frye', 'admissibility', 'ethics']
        }
    ],

    // Detailed concept definitions with case-based teaching approach
    concepts: {
        'locards-principle': {
            name: "Locard's Exchange Principle",
            tagline: "Every contact leaves a trace",
            
            caseIntroduction: `Detective Sarah Chen arrives at a break-in scene. The window is shattered, but there's no suspect. As she examines the broken glass, she notices tiny fabric fibers caught on a jagged edge. On the floor, she finds soil particles that don't match the local terrain. These seemingly insignificant traces will become crucial evidence.`,
            
            definition: `Locard's Exchange Principle states that when two objects come into contact, there is always a transfer of material between them. This principle is the foundation of trace evidence analysis in forensic science.`,
            
            keyPoints: [
                {
                    point: "Mutual Transfer",
                    explanation: "Both objects involved in contact will exchange materials, though the transfer may be asymmetric."
                },
                {
                    point: "Microscopic Evidence",
                    explanation: "Transferred materials are often microscopic - fibers, hair, pollen, glass fragments, soil particles."
                },
                {
                    point: "Time Sensitivity",
                    explanation: "Trace evidence can be lost or contaminated over time through natural processes or additional contacts."
                },
                {
                    point: "Context Matters",
                    explanation: "The significance of trace evidence depends on context - finding cat hair on a cat owner is different from finding it on someone claiming they've never been near cats."
                }
            ],
            
            realWorldApplication: [
                "Hit-and-run investigations: Paint transfers between vehicles",
                "Assault cases: Fiber transfer from clothing during struggle",
                "Burglary: Soil from suspect's shoes matching crime scene",
                "Sexual assault: DNA and fiber evidence linking suspect to victim"
            ],
            
            limitations: [
                "Transfer doesn't always occur in detectable amounts",
                "Secondary transfer can complicate interpretations (e.g., fibers transferred from one person to another, then to a crime scene)",
                "Environmental factors can destroy or alter trace evidence",
                "Some materials transfer more readily than others"
            ],
            
            ethicalConsiderations: `Trace evidence must be interpreted cautiously. The presence of someone's DNA or fibers at a scene doesn't automatically indicate guilt - there may be innocent explanations. Forensic scientists must avoid confirmation bias and present findings objectively, including alternative explanations.`,
            
            socraticQuestions: [
                "If a suspect's fiber is found at a crime scene, what alternative explanations might exist besides direct involvement?",
                "Why might the absence of trace evidence be as significant as its presence?",
                "How does the concept of secondary transfer complicate forensic investigations?",
                "What precautions must investigators take to prevent their own materials from contaminating a scene?"
            ],
            
            casePractice: {
                scenario: `A residential burglary occurred. The homeowner reports nothing was stolen, but drawers were rifled through. On the windowsill used for entry, investigators find: (1) Small glass fragments with fabric fibers, (2) A partial shoe print in soil, (3) A cigarette butt nearby. A suspect is identified three blocks away with a small cut on their hand.`,
                questions: [
                    "What types of trace evidence should investigators collect from the suspect?",
                    "How would you explain the significance of the glass fragments with fibers?",
                    "What might the absence of blood at the scene tell us?",
                    "What control samples would be needed for comparison?"
                ]
            }
        },

        'chain-of-custody': {
            name: "Chain of Custody",
            tagline: "Documenting evidence from scene to courtroom",
            
            caseIntroduction: `In a high-profile murder trial, the prosecution's case falls apart when the defense demonstrates a 45-minute gap in the evidence documentation. The blood sample that should prove the defendant's guilt becomes inadmissible. This case illustrates why meticulous chain of custody is critical.`,
            
            definition: `Chain of custody is the chronological documentation showing the seizure, custody, control, transfer, analysis, and disposition of physical or electronic evidence. It establishes that evidence has not been altered, tampered with, or substituted.`,
            
            keyPoints: [
                {
                    point: "Continuous Documentation",
                    explanation: "Every person who handles evidence must be documented with date, time, purpose, and transfer signatures."
                },
                {
                    point: "Sealed Packaging",
                    explanation: "Evidence must be packaged in tamper-evident containers with unique identifiers and seals."
                },
                {
                    point: "Admissibility Requirement",
                    explanation: "Without proper chain of custody, evidence may be deemed inadmissible in court, regardless of its relevance."
                },
                {
                    point: "Digital Evidence Challenges",
                    explanation: "Electronic evidence requires hash values and write-blockers to prove data wasn't altered during examination."
                }
            ],
            
            requiredDocumentation: [
                "Who collected the evidence and when",
                "How and where it was collected",
                "Who had custody at any given time",
                "How it was stored and secured",
                "Any changes in custody with signatures",
                "Who analyzed it and what procedures were used"
            ],
            
            commonFailures: [
                "Gaps in time documentation",
                "Missing signatures on transfer forms",
                "Improper storage conditions",
                "Unlocked evidence rooms or vehicles",
                "Using generic descriptions instead of unique identifiers",
                "Failure to document sub-sampling for analysis"
            ],
            
            ethicalConsiderations: `Chain of custody protects both the innocent and ensures justice for victims. Sloppy documentation can free guilty individuals or fail to exonerate the innocent. It's not just bureaucracy - it's a fundamental protection of constitutional rights.`,
            
            socraticQuestions: [
                "Why might a defense attorney focus heavily on chain of custody documentation?",
                "What could explain a gap in custody documentation, and would any explanation be acceptable?",
                "How does chain of custody protect defendants' rights?",
                "Why is chain of custody especially challenging in multi-jurisdictional cases?"
            ],
            
            casePractice: {
                scenario: `A laptop is seized during a search warrant execution at 10:15 AM. It's photographed at the scene, placed in an evidence bag, and transported to the lab. The forensic analyst begins examination at 2:45 PM the same day. During trial, the defense questions whether the laptop could have been accessed between seizure and analysis.`,
                questions: [
                    "What documentation should exist to account for the time gap?",
                    "What technical safeguards could prove the laptop wasn't altered?",
                    "Who should have signed the chain of custody form?",
                    "What information must appear on the evidence bag?"
                ]
            }
        },

        'modus-operandi': {
            name: "Modus Operandi (MO)",
            tagline: "Understanding criminal behavior patterns",
            
            caseIntroduction: `A series of burglaries across three months shows distinct patterns: always on Tuesday evenings, always targeting corner units, always entering through bathroom windows, always taking only jewelry and cash. The MO helps investigators predict the next target and link cases that might otherwise seem unrelated.`,
            
            definition: `Modus Operandi (MO) refers to the method of operation - the learned behaviors and techniques a criminal uses to successfully commit crimes. Unlike signature behaviors, MO is functional and can evolve over time as the offender learns.`,
            
            keyPoints: [
                {
                    point: "Functional Purpose",
                    explanation: "MO serves practical purposes: gaining entry, avoiding detection, controlling victims, escaping."
                },
                {
                    point: "Dynamic Nature",
                    explanation: "MO evolves as criminals learn from mistakes, media coverage, or law enforcement tactics."
                },
                {
                    point: "MO vs. Signature",
                    explanation: "MO is what the offender needs to do; signature is what they want to do for psychological gratification."
                },
                {
                    point: "Linking Cases",
                    explanation: "Similar MOs can help link cases to identify serial offenders, but differences don't rule out the same perpetrator."
                }
            ],
            
            moElements: [
                "Target selection (victim or location characteristics)",
                "Method of approach and con (how initial contact is made)",
                "Method of attack (level and type of force)",
                "Verbal activity (specific words or scripts)",
                "Precautionary acts (avoiding detection/identification)",
                "Items taken or left behind"
            ],
            
            limitations: [
                "MO can change significantly between crimes as offender learns",
                "Similar MOs don't necessarily mean same offender",
                "Media coverage can cause offenders to alter their MO",
                "Copycat criminals may adopt similar MOs"
            ],
            
            ethicalConsiderations: `MO analysis must avoid racial, ethnic, or socioeconomic profiling. Investigators should focus on specific behavioral patterns rather than demographic assumptions. Over-reliance on MO can lead to tunnel vision, causing investigators to miss evidence pointing to different suspects.`,
            
            socraticQuestions: [
                "Why might a burglar change from breaking windows to picking locks?",
                "How can you distinguish between an evolving MO and two different offenders?",
                "What's the danger of assuming all crimes with similar MOs are linked?",
                "How might media coverage of a crime series affect the offender's MO?"
            ],
            
            casePractice: {
                scenario: `Three robberies of convenience stores show these patterns:
Robbery 1 (Week 1): Late evening, handgun shown, demanded cash, polite to clerk, left on foot
Robbery 2 (Week 3): Late evening, handgun shown, demanded cash AND cigarettes, rude to clerk, left in vehicle
Robbery 3 (Week 5): Early morning, no weapon seen, note demanding cash, silent, left in vehicle`,
                questions: [
                    "Which elements suggest these might be the same offender?",
                    "Which differences might indicate different offenders?",
                    "What could explain the evolution if it is one offender?",
                    "What additional information would help link or separate these cases?"
                ]
            }
        },

        'crime-scene-management': {
            name: "Crime Scene Management",
            tagline: "Protecting and processing the scene",
            
            caseIntroduction: `First responders arrive at a suspected homicide. A crowd has gathered, family members are distraught, weather is deteriorating, and media helicopters circle overhead. The decisions made in the next 15 minutes will determine whether critical evidence is preserved or destroyed forever.`,
            
            definition: `Crime scene management encompasses all procedures used to protect, document, search, and process a crime scene to maximize evidence recovery while maintaining integrity and minimizing contamination.`,
            
            keyPoints: [
                {
                    point: "Scene Security",
                    explanation: "Establishing and maintaining perimeters to prevent unauthorized access and evidence contamination."
                },
                {
                    point: "Documentation Priority",
                    explanation: "Photograph and document before touching anything - you can never 'undisturb' a scene."
                },
                {
                    point: "Systematic Approach",
                    explanation: "Use established search patterns (grid, spiral, strip) to ensure complete coverage."
                },
                {
                    point: "Team Coordination",
                    explanation: "Multiple specialists (photographers, evidence technicians, detectives) must work in coordinated sequence."
                }
            ],
            
            sceneApproach: [
                "Secure and define boundaries (inner and outer perimeters)",
                "Document scene before entry (initial photography)",
                "Establish single entry/exit path to minimize contamination",
                "Conduct initial walkthrough without touching evidence",
                "Document with photography, videography, sketches, notes",
                "Systematic search using appropriate pattern",
                "Collect and package evidence with proper chain of custody",
                "Final documentation before releasing scene"
            ],
            
            searchPatterns: {
                "Grid/Double-Strip": "Two perpendicular line searches - thorough but time-consuming",
                "Spiral": "Working inward or outward from center - good for open areas",
                "Zone": "Divide scene into sectors - ideal for large or complex scenes",
                "Strip/Line": "Searchers walk in parallel lines - efficient for outdoor scenes",
                "Quadrant": "Divide into four sections from central point - good for confined spaces"
            },
            
            commonContamination: [
                "Unnecessary personnel entering scene",
                "Failure to use appropriate PPE",
                "Improper packaging allowing cross-contamination",
                "Using scene bathroom or phone",
                "Moving evidence before documentation",
                "Weather exposure before protection"
            ],
            
            ethicalConsiderations: `Investigators have an ethical duty to process scenes thoroughly regardless of victim status or perceived case importance. Rushing through scene processing to save resources can result in miscarriages of justice. Similarly, excessive scene processing that unnecessarily disrupts families must be balanced against investigative needs.`,
            
            socraticQuestions: [
                "Why might establishing an outer perimeter separate from the immediate scene be important?",
                "What's the risk of allowing EMTs or firefighters into a scene before documentation?",
                "How would you decide when weather protection is necessary versus when it might disturb evidence?",
                "Why document the scene before processing even if you plan to collect everything?"
            ],
            
            casePractice: {
                scenario: `You're first on scene at an outdoor assault. The victim has been transported to the hospital. It's currently sunny but rain is forecast in 3 hours. There's a blood trail, possible weapon (a rock), scattered clothing items, and tire tracks in soft soil. A crowd of 20 onlookers has gathered.`,
                questions: [
                    "What are your first three priorities?",
                    "How would you establish scene boundaries?",
                    "Which evidence requires immediate protection from weather?",
                    "What search pattern would you recommend and why?"
                ]
            }
        },

        'fingerprint-analysis': {
            name: "Fingerprint Analysis",
            tagline: "Uniqueness in the ridges",
            
            caseIntroduction: `A partial fingerprint on a doorframe becomes the only physical link between a suspect and a crime scene. But it's smudged, incomplete, and the suspect claims they visited the location weeks earlier for legitimate reasons. The forensic examiner must determine: is this print sufficient for identification, and can its location or age provide investigative value?`,
            
            definition: `Fingerprint analysis is the comparison of friction ridge skin patterns on fingers to establish identity. It relies on the principle that fingerprint patterns are unique and permanent throughout a person's life.`,
            
            keyPoints: [
                {
                    point: "Three Levels of Detail",
                    explanation: "Level 1: Overall pattern (loop, whorl, arch). Level 2: Minutiae (ridge endings, bifurcations). Level 3: Ridge contours and pore structure."
                },
                {
                    point: "ACE-V Methodology",
                    explanation: "Analysis, Comparison, Evaluation, Verification - the standard protocol for print examination."
                },
                {
                    point: "No Numerical Standard",
                    explanation: "Unlike popular belief, there's no universal 'point system' - examiners assess totality of detail."
                },
                {
                    point: "Latent vs. Known",
                    explanation: "Latent prints from scenes are compared to known prints from suspects or databases."
                }
            ],
            
            printTypes: {
                "Latent": "Hidden prints requiring development (powder, chemicals, alternate light)",
                "Patent": "Visible prints in substances like blood, ink, or grease",
                "Plastic": "3D impressions in soft materials like wax, putty, or clay"
            },
            
            developmentMethods: [
                "Powder dusting (most common for non-porous surfaces)",
                "Cyanoacrylate (superglue) fuming",
                "Ninhydrin (for porous surfaces, reacts with amino acids)",
                "Alternate light sources (fluorescence)",
                "Small particle reagent (for wet surfaces)",
                "Vacuum metal deposition (for difficult surfaces)"
            ],
            
            limitations: [
                "Quality of latent prints varies greatly - many are unusable",
                "Smudged or overlapping prints may be unreadable",
                "Surface texture affects print deposition and recovery",
                "Environmental conditions can degrade prints over time",
                "Examiners have made errors - no method is infallible"
            ],
            
            ethicalConsiderations: `The 2004 Madrid bombing case, where the FBI misidentified Brandon Mayfield's print, demonstrates the need for humility in fingerprint analysis. Cognitive bias (knowing a suspect's identity before comparison) can influence conclusions. Some courts now require documentation of the reasoning process and verification by independent examiners.`,
            
            socraticQuestions: [
                "Why might a print expert conclude 'inconclusive' rather than 'match' or 'exclusion'?",
                "How does context (where a print was found) affect its investigative value versus its identification value?",
                "What factors might cause a false positive identification?",
                "Why is verification by a second examiner important even for 'obvious' matches?"
            ],
            
            casePractice: {
                scenario: `A burglary scene yields several fingerprints: one clear print on a glass picture frame inside the house, one smudged print on the exterior doorknob, and one partial print (6 visible minutiae) on a jewelry box. A suspect is identified who admits to visiting the house once, six months ago, as a guest.`,
                questions: [
                    "Which print locations are most significant and why?",
                    "How does the suspect's admission affect interpretation?",
                    "Is 6 minutiae sufficient for identification?",
                    "What additional information about each print would be valuable?"
                ]
            }
        },

        // Additional concepts follow similar structure...
        // For brevity, I'll include abbreviated versions

        'dna-forensics': {
            name: "DNA Forensic Analysis",
            tagline: "The molecular fingerprint",
            caseIntroduction: `A sexual assault kit sat untested for 15 years. When finally processed, the DNA profile matched a suspect already in prison for a different crime - and linked him to three other unsolved cases. This demonstrates DNA's power while raising questions about resource allocation and justice delayed.`,
            definition: `Forensic DNA analysis compares specific regions of DNA to establish identity, relationships, or exclude individuals from involvement in crimes.`,
            keyPoints: [
                {point: "STR Analysis", explanation: "Short Tandem Repeats in 20+ locations provide statistical uniqueness"},
                {point: "CODIS Database", explanation: "National DNA database enables linking cases and identifying repeat offenders"},
                {point: "Touch DNA", explanation: "Minute samples from skin cells can yield profiles, but increase contamination risk"},
                {point: "Mixture Interpretation", explanation: "Multiple contributors complicate analysis and reduce certainty"}
            ],
            ethicalConsiderations: `DNA databases raise privacy concerns. Familial searching (using relatives' DNA to find suspects) is controversial. Low-level DNA (touch samples) can place innocent people under suspicion through secondary transfer.`,
            socraticQuestions: [
                "What's the difference between 'DNA match' and 'DNA evidence'?",
                "How might innocent DNA get to a crime scene?",
                "Should familial DNA searching be allowed? Why or why not?",
                "What does a 1 in 10 billion match probability actually mean?"
            ]
        },

        'bloodstain-pattern': {
            name: "Bloodstain Pattern Analysis",
            tagline: "Blood tells a story of physics and position",
            caseIntroduction: `Blood spatter on a wall contradicts the suspect's claim of self-defense. The angle and distribution indicate the victim was below the shooter, not attacking. But bloodstain analysis has been criticized - how certain can we be?`,
            definition: `Bloodstain pattern analysis uses the size, shape, distribution, and location of bloodstains to reconstruct events involving bloodshed.`,
            keyPoints: [
                {point: "Impact Spatter", explanation: "Blood dispersed by force - high velocity (gunshot) vs. low velocity (beating)"},
                {point: "Angle of Impact", explanation: "Elongated stains indicate acute angles, circular stains indicate 90-degree impact"},
                {point: "Point of Origin", explanation: "Stringing technique can estimate where blood originated in 3D space"},
                {point: "Transfer Patterns", explanation: "Blood moved from one surface to another through contact"}
            ],
            limitations: [
                "Categorization (high/medium/low velocity) is not always scientifically validated",
                "Many variables affect pattern formation",
                "Some conclusions exceed what physics can support",
                "Expert disagreement is common in interpretation"
            ],
            ethicalConsiderations: `BPA has been criticized for lack of standardization and validation. The 2009 NAS report questioned the scientific foundations of pattern analysis. Examiners must acknowledge limitations and avoid overstating certainty.`
        },

        'forensic-toxicology': {
            name: "Forensic Toxicology",
            tagline: "Detecting poisons, drugs, and chemicals",
            caseIntroduction: `A seemingly healthy person dies suddenly. Autopsy shows no obvious cause. Toxicology reveals lethal levels of prescription opioids - but were they prescribed, accidental, or homicidal? The toxicologist must answer not just 'what' but help determine 'how' and 'why.'`,
            definition: `Forensic toxicology is the analysis of biological specimens for drugs, alcohol, poisons, and other chemicals to support legal investigations.`,
            keyPoints: [
                {point: "Screening vs. Confirmation", explanation: "Presumptive tests (immunoassay) followed by confirmatory tests (GC-MS, LC-MS)"},
                {point: "Postmortem Changes", explanation: "Redistribution and decomposition can alter measured concentrations"},
                {point: "Interpretation Complexity", explanation: "Presence doesn't equal impairment or causation"},
                {point: "Therapeutic vs. Toxic", explanation: "Same substance can be therapeutic, toxic, or lethal depending on concentration and individual factors"}
            ],
            ethicalConsiderations: `Toxicologists must resist pressure to draw unwarranted conclusions. Finding a drug doesn't automatically explain cause of death or impairment. False positives from screening tests can have serious consequences.`
        },

        'digital-forensics': {
            name: "Digital Forensics",
            tagline: "Recovering electronic evidence",
            caseIntroduction: `The suspect's phone was 'factory reset' before seizure. Can deleted files be recovered? Text messages? Location history? Digital forensics can often retrieve what suspects think is gone - but must follow strict protocols to ensure admissibility.`,
            definition: `Digital forensics involves the preservation, collection, validation, identification, analysis, interpretation, documentation and presentation of digital evidence.`,
            keyPoints: [
                {point: "Write Protection", explanation: "Use write-blockers to prevent any modification of original evidence"},
                {point: "Hash Values", explanation: "Cryptographic hashes prove data hasn't been altered"},
                {point: "Deleted Data Recovery", explanation: "Deleted files often remain until overwritten"},
                {point: "Metadata Analysis", explanation: "Hidden data about files - creation dates, authors, locations, edit history"}
            ],
            ethicalConsiderations: `Digital privacy rights must be balanced with investigative needs. Cloud storage complicates jurisdiction and privacy. Encryption can make evidence inaccessible even with legal authority.`
        },

        'ballistics': {
            name: "Forensic Ballistics",
            tagline: "Connecting bullets to firearms",
            caseIntroduction: `A bullet recovered from a victim can potentially be matched to a specific firearm through microscopic striations. But recent studies question the uniqueness of these patterns - what level of certainty is justified?`,
            definition: `Forensic ballistics examines firearms, ammunition, and related evidence to determine what weapon was used and potentially link it to a specific gun.`,
            keyPoints: [
                {point: "Rifling Characteristics", explanation: "Lands and grooves create unique striations on bullets"},
                {point: "Firing Pin Impressions", explanation: "Cartridge cases show unique markings from firing pin and breech face"},
                {point: "NIBIN Database", explanation: "National database compares ballistic evidence across jurisdictions"},
                {point: "Distance Determination", explanation: "Gunshot residue patterns indicate shooting distance"}
            ],
            limitations: [
                "Uniqueness assumptions being scientifically re-evaluated",
                "Markings can change over time or with maintenance",
                "Lack of standardized error rates",
                "Examiner subjectivity in comparisons"
            ]
        },

        'forensic-entomology': {
            name: "Forensic Entomology",
            tagline: "Insects as witnesses",
            caseIntroduction: `A body is found in a remote area. Decomposition makes time of death estimation difficult. The forensic entomologist examines insect evidence - larvae development, species succession - to narrow the postmortem interval to within 36 hours.`,
            definition: `Forensic entomology uses insect evidence to estimate time since death, determine if a body was moved, detect drugs/toxins, and establish whether wounds occurred before or after death.`,
            keyPoints: [
                {point: "Insect Succession", explanation: "Predictable sequence of insect colonization as decomposition progresses"},
                {point: "Development Stages", explanation: "Temperature-dependent larval development provides timeline estimates"},
                {point: "Geographic Specificity", explanation: "Local insect populations and climate affect conclusions"},
                {point: "Drug Detection", explanation: "Insects can concentrate drugs from tissues, aiding toxicology when body fluids unavailable"}
            ],
            ethicalConsiderations: `PMI estimates from entomology have margins of error that must be clearly communicated. Temperature data accuracy is critical but often uncertain for outdoor scenes.`
        },

        'questioned-documents': {
            name: "Questioned Document Examination",
            tagline: "Uncovering forgery and authentication",
            caseIntroduction: `A will is contested - the signature looks right, but is it genuine? Document examiners analyze pressure patterns, stroke sequence, ink chemistry, and paper characteristics to determine authenticity.`,
            definition: `Questioned document examination analyzes documents to determine authenticity, detect alterations, identify authorship, or reveal hidden information.`,
            keyPoints: [
                {point: "Handwriting Comparison", explanation: "Analysis of individual writing characteristics and habits"},
                {point: "Ink and Paper Analysis", explanation: "Chemical and physical testing to detect forgery or determine age"},
                {point: "Indented Writing", explanation: "Recovering impressions from pages below the written page"},
                {point: "Alterations Detection", explanation: "Finding erasures, additions, or modifications"}
            ],
            limitations: [
                "Handwriting naturally varies within individuals",
                "Limited known samples reduce comparison confidence",
                "Disguised writing can complicate analysis",
                "Age dating of documents is imprecise"
            ]
        },

        'impression-evidence': {
            name: "Impression Evidence",
            tagline: "Tracks, marks, and traces",
            caseIntroduction: `Muddy shoe prints lead from the crime scene to a suspect's vehicle. But the suspect has five pairs of the same brand shoes. Can the examiner conclusively match these specific prints to these specific shoes?`,
            definition: `Impression evidence includes shoe prints, tire tracks, tool marks, and bite marks - patterns left by contact with a surface.`,
            keyPoints: [
                {point: "Class Characteristics", explanation: "Features shared by a group (shoe size, tread pattern, tire model)"},
                {point: "Individual Characteristics", explanation: "Unique wear patterns, cuts, or damage specific to one item"},
                {point: "Casting Techniques", explanation: "Dental stone, silicone, or other materials preserve 3D impressions"},
                {point: "Comparison Standards", explanation: "Test impressions from known items under similar conditions"}
            ],
            ethicalConsiderations: `Bite mark analysis has been discredited after wrongful convictions. Even shoe print and tool mark analysis face questions about examiner subjectivity and error rates.`
        },

        'forensic-psychology': {
            name: "Forensic Psychology",
            tagline: "Understanding criminal behavior and competency",
            caseIntroduction: `A defendant claims mental illness prevented understanding right from wrong. A forensic psychologist must evaluate competency to stand trial and criminal responsibility - determinations that will shape the entire legal process.`,
            definition: `Forensic psychology applies psychological principles to legal questions including competency, criminal responsibility, risk assessment, and eyewitness reliability.`,
            keyPoints: [
                {point: "Competency Evaluation", explanation: "Can the defendant understand proceedings and assist in their defense?"},
                {point: "Criminal Responsibility", explanation: "Did mental illness prevent understanding wrongfulness of actions?"},
                {point: "Risk Assessment", explanation: "Evaluating likelihood of future violence or recidivism"},
                {point: "Eyewitness Factors", explanation: "Understanding memory, stress, and suggestibility effects"}
            ],
            ethicalConsiderations: `Psychologists must remain objective despite retaining party. Risk assessments have high error rates. Profiling is controversial and not scientifically validated.`
        },

        'expert-testimony': {
            name: "Expert Witness Testimony",
            tagline: "Science in the courtroom",
            caseIntroduction: `A fingerprint examiner testifies to an 'absolute' identification. Under cross-examination, they admit there's no research establishing error rates for their method. The jury must weigh expert confidence against scientific limitations.`,
            definition: `Expert testimony allows qualified specialists to explain scientific findings to courts, but must meet legal standards for reliability and relevance.`,
            keyPoints: [
                {point: "Daubert Standard", explanation: "Federal standard requiring scientific validity: testing, peer review, error rates, acceptance"},
                {point: "Frye Standard", explanation: "General acceptance in relevant scientific community (some states still use)"},
                {point: "Role Boundaries", explanation: "Experts explain science but shouldn't usurp jury's fact-finding role"},
                {point: "Cognitive Bias", explanation: "Contextual information can unconsciously influence expert conclusions"}
            ],
            ethicalConsiderations: `Experts have duty to be impartial despite being hired by one side. Must acknowledge limitations and uncertainties. Should not overstate conclusions beyond what science supports. Conflicts of interest must be disclosed.`,
            socraticQuestions: [
                "What's the difference between explaining findings and advocating for a verdict?",
                "Should experts be allowed to state 'absolute certainty'?",
                "How can courts evaluate conflicting expert testimony?",
                "What's the danger of 'hired gun' experts?"
            ]
        }
    },

    // Case studies for practice
    caseStudies: [
        {
            id: 'case-001',
            title: 'The Missing Deposit',
            difficulty: 'beginner',
            concepts: ['locards-principle', 'chain-of-custody', 'fingerprint-analysis'],
            scenario: `A bank reports $5,000 missing from a deposit bag. Three employees had access. Security footage is inconclusive. The deposit bag is recovered from a trash bin with a torn corner.`,
            evidence: [
                'Deposit bag with torn corner',
                'Partial fingerprint on the bag',
                'Small fibers caught in the tear',
                'Security footage showing employees near the area'
            ],
            questions: [
                'What trace evidence should be collected based on Locard\'s Principle?',
                'How would you establish chain of custody for the deposit bag?',
                'What value do the fingerprints have if all employees legitimately handle deposit bags?',
                'What additional evidence would help narrow the suspects?'
            ]
        },
        {
            id: 'case-002',
            title: 'Digital Alibi',
            difficulty: 'intermediate',
            concepts: ['digital-forensics', 'chain-of-custody'],
            scenario: `A suspect claims they were home during a burglary, citing their computer activity logs showing online gaming from 8PM-10PM. The burglary occurred at 9PM, two miles from their home.`,
            evidence: [
                'Suspect\'s computer showing gaming logs',
                'Router logs from suspect\'s home',
                'Cell phone location data',
                'Gaming platform server records'
            ],
            questions: [
                'What could explain gaming activity if the suspect wasn\'t actually home?',
                'Which digital evidence would be most reliable and why?',
                'How would you ensure the computer evidence is admissible?',
                'What additional digital evidence would you seek?'
            ]
        },
        {
            id: 'case-003',
            title: 'The Serial Pattern',
            difficulty: 'advanced',
            concepts: ['modus-operandi', 'forensic-psychology'],
            scenario: `Five burglaries over three months share some characteristics but differ in others. All target single-family homes on corner lots, but entry methods vary: two via window, two via door, one via garage. Take patterns also differ.`,
            evidence: [
                'Crime scene reports from all five burglaries',
                'Neighborhood canvass interviews',
                'Property taken lists',
                'Entry/exit point photographs'
            ],
            questions: [
                'Which commonalities suggest a single offender?',
                'Which differences might indicate multiple offenders or evolving MO?',
                'What investigative steps would help link or separate these cases?',
                'What psychological factors might explain MO evolution?'
            ]
        }
    ],

    // Simulations for interactive practice
    simulations: [
        {
            id: 'sim-001',
            title: 'First Responder at Burglary Scene',
            difficulty: 'beginner',
            concept: 'crime-scene-management',
            description: 'You arrive first at a residential burglary. Make critical decisions about scene security and evidence preservation.',
            initialState: {
                scene: 'Front door is open, broken glass on floor, homeowner waiting outside',
                decisions: 0,
                score: 0
            }
        },
        {
            id: 'sim-002',
            title: 'Chain of Custody Challenge',
            difficulty: 'intermediate',
            concept: 'chain-of-custody',
            description: 'Track evidence from collection through analysis. Identify breaks in chain of custody.',
            initialState: {
                evidenceItems: 5,
                documentsComplete: 0,
                errors: 0
            }
        },
        {
            id: 'sim-003',
            title: 'Blood Spatter Reconstruction',
            difficulty: 'advanced',
            concept: 'bloodstain-pattern',
            description: 'Analyze blood spatter patterns to determine events and positions during an assault.',
            initialState: {
                patterns: 3,
                analyzed: 0,
                accuracy: 0
            }
        }
    ]
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ForensicKnowledge;
}
