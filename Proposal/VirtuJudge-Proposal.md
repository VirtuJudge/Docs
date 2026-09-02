

**`PHASE-1`**

**`STRUCTURED`**
**`PROPOSAL`**

1. # `Problem & Market Validation`

`Many people struggle with their presentation skills and are actively looking for ways to improve them. One traditional solution is to find a friend or an expert in public speaking to present in front of, allowing them to take notes on your performance and track your movements. However, finding someone with the right expertise and available time can be difficult. Another option is to find a training center or hub that offers presentation courses, but high-quality programs are often rare, geographically distant, or simply too expensive.`

`Today, with the rapid advancement of AI models and computer vision, we can harness these technologies to solve this problem. We are building an app that uses computer vision to track a presenter’s body language and eye contact. The app then processes this output data using AI models, analyzing the performance to generate personalized notes and actionable recommendations for the user. The market is wide open for this kind of accessible solution. With competitive pricing plans and a strong trial period, this app is expected to be a great success.`

2. # `AI Approach & Justification`

   1. ## **`Why AI?`**

`For early-stage startups and student teams, a strong idea alone is not enough. The way a team presents its idea, including speaking clarity, body language, pacing, and the quality of its arguments, can significantly affect how the pitch is perceived. However, professional pitch coaching is expensive, and peer feedback is subjective. This becomes more challenging when a pitch is delivered by a large team, where transitions and individual performance vary. Our product uses AI to provide teams with a practical way to repeatedly practice pitches and receive consistent, measurable, and actionable feedback without requiring a human coach for every session.`

2. ## **`System Architecture & Model Choices (MVP Baseline)`**

`Our system follows a highly decoupled, multimodal pipeline handling two primary inputs: the Video pitch and the team's Project Documents. (Note: The architecture is modular, allowing future plug-and-play upgrades).`

1. **`The Three Parallel Streams:`**
* **`Speech Analysis:`**
  * **`Models:`** `Whisper Large V3 Turbo (via GroqCloud) for extreme speed and word-level timestamps, combined with pyannote Community-1 for dedicated Speaker Diarization.`
  * **`Justification:`** `Accurately transcribes exactly what was said and maps it to the correct team member.`

* **`Vision Analysis:`**
  * **`Model:`** `MediaPipe Pose Landmarker + Face Landmarker`
  * **`Justification:`** `Lightweight and highly accurate for extracting posture, movement, and gaze landmarks without the heavy overhead of full object detection models like YOLO.`

* **`Audio Features:`**
  * **`Tools:`** `Librosa + Python Signal Processing`
  * **`Justification:`** `Extracts measurable speech-delivery indicators (e.g., speaking rate, pause duration, filler frequency, pitch variation) to provide objective data rather than subjective "confidence scores."`

2. **`Aggregation & Document Grounding (Document Input):`**
* **`Multimodal Features Aggregator:`** `Synchronizes the exact timings of the Vision, Speech, and Audio features into a unified data structure.`

* **`Store Knowledge (RAG):`** `The system processes optional Project Documents (Pitch Decks, Business Plans, Financials) using an Embeddings + Vector DB pipeline. This crucial step anchors the AI's evaluation in the team's actual factual data.`

3. **`The AI Judge Engine (LLM):`**

* **`Model:`** `A high-performance LLM (e.g., Qwen3 or equivalent via Groq API).`

* **`Execution:`** `The engine receives the aggregated data and the RAG context to perform two distinct functions:`

  1. **`Score / Feedback:`** `Generates an immediate evaluation of the pitch structure and argument consistency.`

  2. **`Real Time QA:`** `Simulates an interactive judging panel by asking a Question, receiving a User Answer, and looping back for Follow-up inquiries based on the team's responses.`

* `Both streams ultimately converge into a comprehensive Final Report.`

  3. ## **`Architecture Flowchart`**

*`Figure 1: AI Architecture Flowchart`*

4. ## **`Why This Architecture?`**

* **`Asynchronous Efficiency:`** `The orchestrator allows the system to handle heavy vision and audio tasks, avoiding the need for expensive real-time processing hardware.`

* **`Document-Grounded:`** `Integrating Project Documents via RAG before the AI Judge Engine ensures all feedback and Q&A interactions are strictly tied to the team's actual project claims, catching inconsistencies instantly.`

* **`Interactive Learning Loop:`** `The inclusion of the "Real Time QA" loop elevates the product from a simple feedback tool to an interactive coaching simulator.`

* **`Modular & Future-Proof:`** `By separating the Orchestrator, Aggregator, and AI Judge Engine, any individual model can be upgraded seamlessly.`

3. # `Technical Architecture`

   1. ## **`High-Level Architecture Overview`**

`The system employs a Monolithic Backend Pattern built with FastAPI (Python 3.11+) to serve as an asynchronous, low-latency API and orchestration engine. It unifies UI requests, pre-recorded document/video parsing, batch processing for presentation skills evaluation, dynamic Q&A generation, AI judge scoring, and final report generation into a single unit.`

*`Figure 2: Technical Architecture`*

### **`Core Architecture Components:`**

1. ### **`Frontend Layer (Client Interface)`**

* **`Framework:`** `Next.js`
* **`Responsibilities:`**
  * `Handles real-time media acquisition including video presentation upload, browser-based audio recording for Q&A sessions, and optional document upload drops (PDF/PPTX).`
  * `Implements dynamic dashboard interfaces for presenting live AI-generated questions to users and displaying final visual scorecards.`
  * `Manages persistent client-side state during interactive sessions using WebSockets for low-latency bidirectional communication.`

2. #### **`FastAPI Monolith Backend`**

* **`Framework:`** `Python 3.11+ / FastAPI`
* **`Responsibilities:`**
  * `Serves as the central orchestration monolith managing business logic, session state transitions, user authentication, and secure file upload pipelines.`
  * `Coordinates asynchronous task delegation via a background job queue to handle non-blocking audio/video processing.`
  * `Links client requests directly to the internal AI Core Evaluation Subsystem, sequencing calls from ingestion to final judgment scoring.`

3. #### **`Multimodal AI Engine & Discussion Modules`**

* **`Document Engine & Vision Pipeline:`** `Parses submitted pitch decks/reports and processes video presentations using vision models to evaluate Body Language, Speech Pace, Content Consistency, and Report Alignment.`
* **`Discussion Generation Model:`** `Synthesizes extracted document summaries and presentation analysis metrics to formulate targeted, context-aware pitch questions.`
* **`Speech-to-Text (STT) & Audio Processor:`** `Uses OpenAI Whisper / Gemini Audio APIs to ingest real-time spoken audio responses from the presenting team, converting them to clean text transcripts.`
* **`AI Judge Engine:`** `Aggregates Q&A transcripts, visual evaluation scores, and background document contexts. Executes LLM scoring pipelines to compile detailed numerical breakdowns and constructive qualitative feedback.`

4. #### **`Data Store Layer`**

* **`PostgreSQL 16 + pgvector (Supabase):`** `Manages user accounts, session metadata, numerical scores, and document vector embeddings for semantic search.`
* **`MongoDB Atlas (NoSQL):`** `Stores real-time Q&A audio transcripts, dynamic question buffers, and raw JSON evaluation logs.`
* **`Object Storage:`** `Hosts presentation videos, supporting documents, recorded user audio clips, and exported PDF reports.`

  2. ## **`End-to-End Data Flow (Core AI Pipeline)`**

`The platform supports two operational modes: Flow A (Presentation Only) and Flow B (Document-Assisted Presentation) across four core phases:`

### **`Phase 1: Input Ingestion & Analysis`**

`Presenters submit video presentations or video plus supporting pitch documents. The backend stores raw files, executes asynchronous text extraction and document chunking, and performs multimodal video analysis to evaluate presenter delivery, pace, and content consistency.`

### **`Phase 2: Dynamic Question Generation`**

`The system synthesizes extracted document contexts and presentation metrics against evaluation rubrics to generate context-aware, targeted pitch questions, buffering them for interactive streaming.`

### **`Phase 3: Interactive Judgment Table (Real-Time Q&A)`**

`Questions stream sequentially to the presentation team. Spoken audio responses are captured in real time, converted into accurate text transcripts, and linked directly to the active evaluation session.`

### **`Phase 4: AI Evaluation & Report Export`**

`The evaluation engine aggregates Q&A transcripts, visual metrics, and document context to generate numerical scores and qualitative feedback. A structured final report is saved to the database, archived as a PDF, and rendered on the reviewer dashboard.`

4. # `Business Feasibility`

   1. ## **`Target Audience:`**

* ## `Hackathon and Competition teams`

* `Startups and small businesses who are going to find investors`
* `Sales and product teams`

  2. ## **`Market Viability:`**

* **`75% of the population`** `experiences glossophobia (speech and presentation anxiety), with 50% reporting high physiological stress during live pitches.`
* **`$200 to $500 per session`** `(averaging $8,500/year) is the standard cost for professional 1-on-1 human executive/pitch coaching, making it inaccessible to 90%+ of student founders and early-stage entrepreneurs.`
* **`$4.2 Billion`** `is the global presentation and communication training market size, growing at a 6.7% CAGR toward $5.1B+ by 2033. AI-powered speech coaching adoption has surged 340%.`
  * `Total Addressable Market (TAM): $4.2 Billion`
  * `Serviceable Addressable Market (SAM): $650 Million`
  * `Serviceable Obtainable Market (SOM): $16 Million`
* **`73% of users`** `demonstrate measurable improvement in delivery confidence, pacing, and reduction in filler words within 5 to 10 AI-assisted practice sessions.`
* **`38% of startup failures`** `directly from running out of cash or failing to raise capital (CB Insights). A weak pitch deck is often the first domino in that chain.`
* **`3 minutes and 44 seconds`** `is the average time an investor spends reviewing a pitch deck before deciding whether to take a meeting or reject the startup, so the quality of the pitch deck must be very impressive for the investors.`

  3. ## **`Execution Scope:`**

     1. ## **`During the competition:`**

* **`Document & Presentation Ingestion:`** `Parsing pipeline supporting PDF pitch decks and technical reports to extract core claims, business metrics, and MVP architecture.`
* **`Audio & Speech Analysis:`** `Automated transcription extracting speaking rate (target: 130–160 WPM), hesitation pauses, filler words, and overall time management.`
* **`Discrepancy & Alignment Engine:`** `Cross-referencing what the team said in the pitch against what was written in the documentation to identify omitted points, exaggerations, or weak technical explanations.`
* **`AI Discussion Simulator:`** `Generating 3 to 5 challenging Q&A prompts based directly on the identified gaps in the team's proposal.`
* **`Computer vision`** `tracking for body motion and eye contact.`
* **`Performance Score:`** `problem-solution fit, business model clarity, technical feasibility, pacing, clarity, confidence indicators, and presentation timing.`

  2. **`After the competition:`**
* `Live, synchronous voice interruption during active video streams.`
* `Multi-judge custom avatar personas based on most judges' backgrounds.`
* `Multi-language analyzer for pitch deck and discussion.`

  3. **`Success metrics:`**
* `Over 80% user agreement of identified weaknesses in pre-testing with users.`
* `The platform can perfectly analyze reports and be ready for the discussion.`
* `Turnaround Speed: Complete evaluation & report generated in under 90 seconds after upload.`
* `Cost Efficiency: Processing cost maintained $0.30 - $0.40 per pitch simulation, proving business viability and high gross margins.`
