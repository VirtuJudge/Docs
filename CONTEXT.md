# VirtuJudge domain language

VirtuJudge models a team's pitch-practice attempt from uploaded evidence through analysis, Q&A, and feedback. These terms are shared across the frontend, backend, AI/ML runtime, contracts, and documentation.

## People and ownership

**User**:
A person with a VirtuJudge identity.
_Avoid_: Account, presenter

**Team**:
A group of users who own projects and practise together.
_Avoid_: Workspace, tenant, organization

**Team Membership**:
The relationship that gives a user an owner or member role in a team.
_Avoid_: Seat, team user

**Team Owner**:
A team member who may manage membership, retention, and destructive operations.
_Avoid_: Admin, superuser

**Team Member**:
A team participant who may create projects and sessions, answer questions, and view the team's reports.
_Avoid_: Collaborator, regular user

## Pitch material

**Project**:
The startup, product, proposal, or idea that a team is pitching.
_Avoid_: Presentation, workspace

**Asset**:
A stored file with an immutable version, checksum, media type, and ownership record.
_Avoid_: Blob, attachment, upload

**Presentation**:
The video asset containing the pitch for one practice session.
_Avoid_: Pitch, recording, session

**Supporting Document**:
A versioned PDF or PPTX asset used to ground questions and feedback.
_Avoid_: Knowledge file, source file

**Session Manifest**:
The immutable list of exact asset versions used by a practice session.
_Avoid_: Upload list, input bundle

## Practice and evaluation

**Practice Session**:
One complete pitch attempt containing a presentation, optional supporting documents, analysis, Q&A, and a report.
_Avoid_: Judge session, simulation, evaluation session

**Analysis Attempt**:
A numbered execution of the AI/ML pipeline for a practice session. A retry creates a new attempt rather than replacing a failed one.
_Avoid_: Run, job

**Evaluation**:
The versioned scores, evidence, and findings produced for an analysis attempt.
_Avoid_: Analysis, result

**Rubric**:
A versioned set of evaluation dimensions, weights, scoring rules, and descriptors.
_Avoid_: Score template, criteria list

**Evidence**:
A reference to an observable source that supports a question, score, or finding.
_Avoid_: Proof, citation

**Mapped Speaker**:
A diarized speaker label that a user has explicitly associated with a team member.
_Avoid_: Detected person, identified speaker

## Questions and feedback

**Q&A Round**:
The ordered set of primary questions, follow-up questions, and submitted or skipped answers in a practice session.
_Avoid_: Discussion, interview

**Primary Question**:
One of three grounded questions generated after presentation analysis.
_Avoid_: Base question, judge prompt

**Follow-up Question**:
One of up to two questions generated from an earlier submitted answer.
_Avoid_: Dynamic prompt, sub-question

**Answer**:
A submitted, skipped, or draft response to one question. A submitted spoken answer points to an audio asset and transcript.
_Avoid_: Response message, reply

**Report**:
The user-facing record containing team feedback, feedback for every mapped member, evidence, scores, recommendations, limitations, and processing metadata.
_Avoid_: Evaluation, scorecard

## Processing language

**Stage**:
A named, observable part of an analysis attempt, such as speech, vision, audio features, grounding, or report assembly.
_Avoid_: Service, model

**Derived Artifact**:
Versioned machine-produced data such as a transcript, landmarks, embeddings, or synchronized features.
_Avoid_: Result, output file

**Provider Adapter**:
A replaceable implementation that connects a pipeline port to a model, hosted API, mail server, object store, or broker.
_Avoid_: Integration helper, vendor client
