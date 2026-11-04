# Andalusia-Data-Science-Team — Healthcare AI Portfolio Analysis Report

> **Organisation:** [Andalusia-Data-Science-Team](https://github.com/Andalusia-Data-Science-Team)  
> **Analysis Date:** October 29, 2026  
> **Total Repositories Analysed:** 156  
> **Taxonomy:** 17-Domain Strict Healthcare Framework  
> **Methodology:** Phase 1-4 pipeline — REST discovery, tree-hash extraction, hybrid classifier, portfolio synthesis

---

## 1. Executive Summary

### Portfolio Overview

| Metric | Value |
|---|---|
| Total repositories analysed | **156** |
| **In-scope** (maps to ≥1 domain) | **96** |
| **Out-of-scope** (excluded) | **61** |
| Dual-domain repositories | **37** |
| Production / Live | **7** |
| Active Development | **89** |
| Domains with zero coverage | **3** |

### Domain Distribution

| # | Domain | Repos | Group |
|---|---|---|---|
| 1 | Clinical Informatics | 32 | Clinical & Medical  |
| 2 | Clinical Governance | 3 | Clinical & Medical  |
| 3 | Medical | 4 | Clinical & Medical  |
| 4 | Pharmacy | 4 | Clinical & Medical  |
| 5 | Medical Coding and Pricing | 16 | Coding, Pricing & Insurance  |
| 6 | Pricing | 1 | Coding, Pricing & Insurance  |
| 7 | Insurance | 7 | Coding, Pricing & Insurance  |
| 8 | Strategy | 5 | Business & Customer  |
| 9 | BD | 0 | Business & Customer ⚪ Gap |
| 10 | CRM | 4 | Business & Customer  |
| 11 | Call Center | 7 | Business & Customer  |
| 12 | Supply Chain | 7 | Operations & Support  |
| 13 | Construction | 0 | Operations & Support ⚪ Gap |
| 14 | Finance | 1 | Operations & Support  |
| 15 | HR | 5 | People  |
| 16 | L&D / Academy | 0 | People ⚪ Gap |

> [!IMPORTANT]
> The organisation's AI/data investment is heavily concentrated in **Clinical Informatics** and **Medical Coding & Insurance** domains, reflecting the strategic priorities of a digitally maturing hospital group. Notable gaps exist in **Construction**, **BD**, and **L&D/Academy**.

---

## 2. Domain-by-Domain Analysis

### 2.1 Clinical & Medical

### Clinical Informatics

**32 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `AI-In-PACS` | 🔵 Active Dev | — | AI-powered image analysis on PACS/DICOM; radiology decision-support layer on HIS. |
| `MedSearch` | 🔵 Active Dev | — | Semantic EMR search engine; indexes clinical notes and patient records for rapid retrieval. |
| `MedSearch_Postgress` | 🔵 Active Dev | — | PostgreSQL-backed variant of MedSearch with pgvector embeddings. |
| `MedSearch_DoseForm` | 🔵 Active Dev | Pharmacy | MedSearch extension scoped to dose-form lookup; bridges EMR search with formulary. |
| `ClinicalNotes2Features` | 🔵 Active Dev | — | SOAP → structured EMR pipeline; extracts clinical features from free-text notes. |
| `radiology-dictation-app` | 🔵 Active Dev | — | Voice dictation application for radiologists; integrates with PACS/RIS. |
| `radiology-voice-system` | 🔵 Active Dev | — | Acoustic model and ASR engine backing radiology dictation; domain-specific language model. |
| `Voice_for_Clinics` | 🔵 Active Dev | — | Ambient clinical scribe capturing physician-patient conversations in real time. |
| `Medvoice_longterm` | 🔵 Active Dev | — | Long-form dictation pipeline optimised for lengthy clinical encounters. |
| `MedVoice` | 🔵 Active Dev | — | Core MedVoice service orchestrating voice-to-text for clinical documentation. |
| `Medical_voice_FAPI` | 🔵 Active Dev | — | FastAPI microservice wrapper exposing Medical Voice ASR endpoints. |
| `medical_voice_recognition` | 🔵 Active Dev | — | Clinical ASR model with medical vocabulary; feeds dictation pipeline. |
| `Medical_voice_assistant` | 🔵 Active Dev | — | End-to-end conversational assistant for hands-free clinical data entry. |
| `AI-Powered-Collaborative-Documentation-Assistant` | 🔵 Active Dev | Medical Coding and Pricing | LLM-driven documentation assistant (Fireworks AI + LangChain) that drafts and codes clinical notes simultaneously. |
| `OPD_ClinicalNotes_Analyzer` | 🔵 Active Dev | Medical Coding and Pricing | Analyses OPD free-text notes → extracts ICD-10 coding suggestions and clinical features. |
| `Clinical_Notes` | 🔵 Active Dev | Medical Coding and Pricing | General-purpose clinical note structuring and auto-coding engine. |
| `Patients-No-Show` | 🔵 Active Dev | — | Predictive model for appointment no-shows; enables proactive rescheduling. |
| `no_show` | 🔵 Active Dev | — | Earlier iteration of the no-show prediction model / experimental variant. |
| `Walk-In` | 🔵 Active Dev | — | Walk-in patient flow optimisation; models queue dynamics and waiting times. |
| `Online_Cancellation_Flow` | 🔵 Active Dev | — | Automated cancellation workflow with patient-reachout and slot release logic. |
| `ER-Suspected-Diagnosis` | 🔵 Active Dev | Clinical Governance | ER triage aide suggesting suspected diagnoses from chief complaint and vitals. |
| `CHI` | 🔵 Active Dev | — | Clinical Health Intelligence dashboard aggregating real-time clinical KPIs. |
| `ScreeningProject` | 🔵 Active Dev | — | Patient screening pipeline for chronic-disease and preventive-care programmes. |
| `ScreeningTrials` | 🔵 Active Dev | — | Trial/experimental branch of the screening project (kept — contains production-grade models). |
| `Health-Care` | 🔵 Active Dev | — | General healthcare analytics platform consolidating operational and clinical metrics. |
| `HJH_Utilization` | 🔵 Active Dev | — | Hospital bed/resource utilisation analytics for the HJH facility. |
| `V99` | 🔵 Active Dev | — | V99 code processing engine — handles unspecified ICD codes in clinical workflows. |
| `V99-GUI` | 🔵 Active Dev | — | Desktop GUI for the V99 coding engine; used by clinical coders. |
| `Ai-server-manager` | 🔵 Active Dev | — | Internal AI model-serving manager for clinical ML microservices. |
| `drug_search_engine` | 🔵 Active Dev | Pharmacy | Clinical drug search engine linking EMR prescriptions to formulary and dosing data. |
| `Medical-Approval-Checker` | 🔵 Active Dev | Insurance | Pre-authorization approval checker integrating payer rules with clinical data. |
| `Smart-Care-API` | 🔵 Active Dev | — | Unified smart-care API gateway for clinical AI services. |


### Clinical Governance

**3 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `MOH_Automation` | 🔵 Active Dev | — | Automates Ministry of Health (MOH) reporting, compliance data collection and submission. |
| `MOH_Automation_V4` | 🔵 Active Dev | — | V4 of MOH Automation with enhanced ETL and multi-facility reporting. |
| `MOH` | 🔵 Active Dev | — | MOH compliance repository — quality indicators, patient safety metrics, and Ministry reporting requirements. |


### Medical

**4 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Master-Doctor` | 🟢 Production | — | Physician master index — unified doctor profiles, specialties, credentials, and scheduling metadata. |
| `Medical_prediction` | 🔵 Active Dev | Clinical Informatics | Clinical prediction models for disease progression, readmission, and length of stay. |
| `Transition-Patients` | 🔵 Active Dev | Clinical Informatics | Care-transition management tool tracking patients from inpatient to follow-up. |
| `medical-screening` | 🔵 Active Dev | Clinical Informatics | Clinical patient screening workflows for high-risk population identification. |


### Pharmacy

**4 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Drug-Database` | 🟢 Production | — | Comprehensive drug formulary and reference database underpinning prescribing workflows. |
| `drug-database-dosing` | 🟢 Production | — | Dosing rules engine (weight, renal/hepatic adjustments) integrated with Drug-Database. |
| `AHBS_AIServices` | 🔵 Active Dev | Medical Coding and Pricing | AI services for the AHBS hospital billing and pharmacy system — auto-codes drug charges and validates prescriptions. |
| `sfda-scraper` | 🔵 Active Dev | — | Scrapes the Saudi FDA (SFDA) drug registry to keep formulary data current and regulatory-compliant. |


### 2.2 Coding, Pricing & Insurance

### Medical Coding and Pricing

**16 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `nphies-ad-engine` | 🟢 Production | Insurance | NPHIES adjudication engine — processes FHIR-based insurance claims with ICD-10/CPT/DRG coding for the Saudi national payer platform. |
| `Nphies_Simulator` | 🔵 Active Dev | Insurance | FHIR NPHIES claim validation sandbox — tests coding accuracy and payer rule compliance before production submission. |
| `Upcoding` | 🔵 Active Dev | — | Revenue integrity tool detecting and preventing code upcoding/unbundling across ICD-10 and CPT claims. |
| `Diagnosis-Mapping` | 🔵 Active Dev | — | NLP mapper translating free-text diagnoses to ICD-10 codes with confidence scoring. |
| `Final-Diagnosis-Project-` | 🔵 Active Dev | — | End-to-end ICD-10 final-diagnosis assignment pipeline for discharge summaries. |
| `CodingSystem` | 🔵 Active Dev | — | Internal coding workbench for clinical coders — rules, workflows, and QA tooling. |
| `claims-prep` | 🔵 Active Dev | Insurance | Claim preparation pipeline — normalises, validates, and enriches claim data before payer submission. |
| `Lab_Prediction` | 🔵 Active Dev | Clinical Informatics | Predicts required lab orders from clinical context; supports auto-coding of lab charges. |
| `Claims_Rejection` | 🔵 Active Dev | Insurance | Analytics engine identifying patterns in payer claim rejections to drive denial prevention. |
| `XplainClaims` | 🔵 Active Dev | Insurance | Explainable AI model surfacing the root cause of claim approvals/denials to coders and finance teams. |
| `Claims-pdf-Extraction` | 🔵 Active Dev | Insurance | OCR + NLP pipeline extracting structured data from payer remittance PDFs. |
| `RAG` | 🔵 Active Dev | Clinical Informatics | Retrieval-Augmented Generation system for clinical coding Q&A and policy lookup. |
| `diagnosis-integration` | 🔵 Active Dev | — | Integration layer connecting diagnosis systems with coding engines and HIS. |
| `claims-api` | 🔵 Active Dev | Insurance | REST API exposing claim submission, status check, and rejection retrieval endpoints. |
| `Claims_Deployment` | 🟢 Production | Insurance | Production deployment infrastructure (Docker, CI/CD) for the claims processing stack. |
| `BigBrother` | 🔵 Active Dev | — | Claims monitoring and anomaly-detection watchdog across all payer channels. |


### Pricing

**1 repository in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Service-Packaging` | 🔵 Active Dev | — | Bundled service package builder — groups procedures and services with calculated pricing. |


### Insurance

**7 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `eligbility_api` | 🔵 Active Dev | Clinical Informatics | API exposing payer eligibility checks; called from HIS at point of registration. |
| `Coverage_Rejections` | 🔵 Active Dev | — | Dedicated coverage-rejection analytics — maps rejection codes to payer-specific rules and appeal routes. |
| `Insurance-Rejection-Cliams` | 🔵 Active Dev | Medical Coding and Pricing | TPA rejection mining — identifies TPA-specific claim rejection trends and patterns. |
| `Insurance-Policy-Uploader` | 🔵 Active Dev | — | Ingests and parses insurance policy PDFs into structured eligibility and benefit rules. |
| `Resubmission-Copilot` | 🔵 Active Dev | Medical Coding and Pricing | AI copilot guiding coders through the claim denial management and resubmission workflow. |
| `eligibility-etl-airflow` | 🟢 Production | Medical Coding and Pricing | Airflow-orchestrated ETL pipeline synchronising payer eligibility data into the HIS database daily. |
| `Eligibilty_api_schedule` | 🟢 Production | — | Scheduled microservice polling payer eligibility endpoints and caching results for real-time queries. |


### 2.3 Business & Customer

### Strategy

**5 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Patient_Segmentation` | 🔵 Active Dev | — | Patient cohort segmentation for strategic planning — identifies high-value, high-risk, and under-served populations. |
| `Clinic_Utilization` | 🔵 Active Dev | — | Clinic capacity and utilisation analytics driving strategic resource allocation decisions. |
| `OPD_segmentation` | 🔵 Active Dev | — | Outpatient department segmentation model used in growth planning and specialty expansion. |
| `Platform-Performance-Optimization-Budget-Impact-Simulation` | 🔵 Active Dev | Finance | Budget-impact simulation modelling platform performance vs. investment scenarios for executive decisions. |
| `Ceo-Summarization` | 🔵 Active Dev | Finance | Executive KPI summarisation tool — digests operational and financial data into CEO-level briefs. |


### BD

> ⚪ **No repositories found.** This domain is currently unaddressed — see Gap Analysis.


### CRM

**4 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `CRM` | 🔵 Active Dev | — | Core patient CRM system — profiles, appointment history, follow-up campaigns, and loyalty tracking. |
| `Chatbot` | 🔵 Active Dev | Call Center | Patient-facing chatbot handling appointment booking, FAQs, and complaint intake; feeds CRM records. |
| `CRM_Call_Results` | 🔵 Active Dev | Call Center | Enriches CRM records with call-centre outcomes — resolution status, follow-up flags, and quality scores. |
| `Chatbot-Auditor` | 🔵 Active Dev | Call Center | Audits chatbot conversation quality — flags off-script responses and tracks patient satisfaction. |


### Call Center

**7 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Contact-center-voice-agent` | 🔵 Active Dev | Clinical Informatics | AI voice agent handling inbound clinical calls — triage, booking, and clinical info routing. |
| `contact-center-chatbot` | 🔵 Active Dev | CRM | Call-centre chatbot for patient-facing text channels; integrates with ticketing and CRM. |
| `IVR-confirmation-outbound` | 🔵 Active Dev | — | Outbound IVR system confirming appointments and collecting pre-visit information automatically. |
| `QA-for-call-center` | 🔵 Active Dev | — | Quality assurance tool evaluating call-centre agent performance using speech analytics and scoring rubrics. |
| `KGraph-non-voice-call-center-` | 🔵 Active Dev | — | Knowledge-graph backend for non-voice call-centre channels (web chat, email); powers intent routing. |
| `Complaint-System` | 🔵 Active Dev | CRM | Patient complaint intake, tracking, escalation, and resolution management system. |
| `Service-Hub-Chatbot` | 🔵 Active Dev | CRM | Omni-channel service hub chatbot integrating patient self-service across web, app, and social channels. |


### 2.4 Operations & Support

### Supply Chain

**7 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Bed-Management` | 🔵 Active Dev | — | Inpatient bed allocation and management system — tracks availability, turnover, and cleaning status. |
| `bedManagement` | 🔵 Active Dev | — | Backend service variant of Bed-Management; exposes REST API for bed status and reservation. |
| `SC-consumption-rate-prediction` | 🔵 Active Dev | — | Predicts medical supply consumption rates to optimise reorder points and prevent stockouts. |
| `Supply_Chain_Consumption_Rate` | 🔵 Active Dev | — | Analytics dashboard tracking supply consumption trends across departments and facilities. |
| `smart_orders_server` | 🔵 Active Dev | — | Smart ordering server that auto-generates purchase orders based on consumption predictions. |
| `smart_order_client` | 🔵 Active Dev | — | Client application for clinical staff to review and approve AI-generated supply orders. |
| `smart_order_client__jar` | 🔵 Active Dev | — | Packaged JAR distribution of the smart order client for legacy HIS integration. |


### Construction

> ⚪ **No repositories found.** This domain is currently unaddressed — see Gap Analysis.


### Finance

**1 repository in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Bank-Automation` | 🔵 Active Dev | — | Automated bank reconciliation tool matching HIS payment records against bank statement transactions. |


### 2.5 People

### HR

**5 repositories in scope**

| Repository | Status | Cross-Domain | Summary |
|---|---|---|---|
| `Doctor-Performance-in-Medical` | 🔵 Active Dev | Clinical Informatics | Physician productivity and performance dashboard for medical specialties — KPIs, patients per session, outcomes. |
| `Doctor-Performance-in-Dental` | 🔵 Active Dev | Clinical Informatics | Dental specialty physician performance dashboard — chair utilisation, production per dentist. |
| `Doctor-Specialty-Performance` | 🔵 Active Dev | — | Cross-specialty physician benchmarking — normalised performance scores across all medical departments. |
| `CV-Ranking` | 🔵 Active Dev | — | AI-powered CV ranking tool for clinical recruitment — scores applicants against specialty-specific criteria. |
| `Integrated-CV-Ranker-Chatbot` | 🔵 Active Dev | — | Conversational extension of CV-Ranking — chatbot UI for HR teams to query ranked candidates. |


### L&D / Academy

> ⚪ **No repositories found.** This domain is currently unaddressed — see Gap Analysis.


---

## 3. Cross-Domain Repositories

These repositories deliver value across **two or more domains** simultaneously and represent the organisation's most strategically important AI assets.

| Repository | Primary Domain | Secondary Domain(s) | Strategic Significance |
|---|---|---|---|
| `MedSearch_DoseForm` | Clinical Informatics | Pharmacy | MedSearch extension scoped to dose-form lookup; bridges EMR search with formulary.… |
| `AI-Powered-Collaborative-Documentation-Assistant` | Clinical Informatics | Medical Coding and Pricing | LLM-driven documentation assistant (Fireworks AI + LangChain) that drafts and codes clinical notes s… |
| `OPD_ClinicalNotes_Analyzer` | Clinical Informatics | Medical Coding and Pricing | Analyses OPD free-text notes → extracts ICD-10 coding suggestions and clinical features.… |
| `Clinical_Notes` | Clinical Informatics | Medical Coding and Pricing | General-purpose clinical note structuring and auto-coding engine.… |
| `ER-Suspected-Diagnosis` | Clinical Informatics | Clinical Governance | ER triage aide suggesting suspected diagnoses from chief complaint and vitals.… |
| `drug_search_engine` | Clinical Informatics | Pharmacy | Clinical drug search engine linking EMR prescriptions to formulary and dosing data.… |
| `Medical-Approval-Checker` | Clinical Informatics | Insurance | Pre-authorization approval checker integrating payer rules with clinical data.… |
| `eligbility_api` | Insurance | Clinical Informatics | API exposing payer eligibility checks; called from HIS at point of registration.… |
| `Medical_prediction` | Medical | Clinical Informatics | Clinical prediction models for disease progression, readmission, and length of stay.… |
| `Transition-Patients` | Medical | Clinical Informatics | Care-transition management tool tracking patients from inpatient to follow-up.… |
| `medical-screening` | Medical | Clinical Informatics | Clinical patient screening workflows for high-risk population identification.… |
| `AHBS_AIServices` | Pharmacy | Medical Coding and Pricing | AI services for the AHBS hospital billing and pharmacy system — auto-codes drug charges and validate… |
| `nphies-ad-engine` | Medical Coding and Pricing | Insurance | NPHIES adjudication engine — processes FHIR-based insurance claims with ICD-10/CPT/DRG coding for th… |
| `Nphies_Simulator` | Medical Coding and Pricing | Insurance | FHIR NPHIES claim validation sandbox — tests coding accuracy and payer rule compliance before produc… |
| `claims-prep` | Medical Coding and Pricing | Insurance | Claim preparation pipeline — normalises, validates, and enriches claim data before payer submission.… |
| `Lab_Prediction` | Medical Coding and Pricing | Clinical Informatics | Predicts required lab orders from clinical context; supports auto-coding of lab charges.… |
| `Claims_Rejection` | Medical Coding and Pricing | Insurance | Analytics engine identifying patterns in payer claim rejections to drive denial prevention.… |
| `XplainClaims` | Medical Coding and Pricing | Insurance | Explainable AI model surfacing the root cause of claim approvals/denials to coders and finance teams… |
| `Claims-pdf-Extraction` | Medical Coding and Pricing | Insurance | OCR + NLP pipeline extracting structured data from payer remittance PDFs.… |
| `RAG` | Medical Coding and Pricing | Clinical Informatics | Retrieval-Augmented Generation system for clinical coding Q&A and policy lookup.… |
| `claims-api` | Medical Coding and Pricing | Insurance | REST API exposing claim submission, status check, and rejection retrieval endpoints.… |
| `Claims_Deployment` | Medical Coding and Pricing | Insurance | Production deployment infrastructure (Docker, CI/CD) for the claims processing stack.… |
| `MedSearch_Postgress` | Medical Coding and Pricing | Clinical Informatics | Also classified here due to code-linkage search features; see Clinical Informatics.… |
| `Insurance-Rejection-Cliams` | Insurance | Medical Coding and Pricing | TPA rejection mining — identifies TPA-specific claim rejection trends and patterns.… |
| `Resubmission-Copilot` | Insurance | Medical Coding and Pricing | AI copilot guiding coders through the claim denial management and resubmission workflow.… |
| `eligibility-etl-airflow` | Insurance | Medical Coding and Pricing | Airflow-orchestrated ETL pipeline synchronising payer eligibility data into the HIS database daily.… |
| `Platform-Performance-Optimization-Budget-Impact-Simulation` | Strategy | Finance | Budget-impact simulation modelling platform performance vs. investment scenarios for executive decis… |
| `Ceo-Summarization` | Strategy | Finance | Executive KPI summarisation tool — digests operational and financial data into CEO-level briefs.… |
| `Chatbot` | CRM | Call Center | Patient-facing chatbot handling appointment booking, FAQs, and complaint intake; feeds CRM records.… |
| `CRM_Call_Results` | CRM | Call Center | Enriches CRM records with call-centre outcomes — resolution status, follow-up flags, and quality sco… |
| `Chatbot-Auditor` | CRM | Call Center | Audits chatbot conversation quality — flags off-script responses and tracks patient satisfaction.… |
| `Contact-center-voice-agent` | Call Center | Clinical Informatics | AI voice agent handling inbound clinical calls — triage, booking, and clinical info routing.… |
| `contact-center-chatbot` | Call Center | CRM | Call-centre chatbot for patient-facing text channels; integrates with ticketing and CRM.… |
| `Complaint-System` | Call Center | CRM | Patient complaint intake, tracking, escalation, and resolution management system.… |
| `Service-Hub-Chatbot` | Call Center | CRM | Omni-channel service hub chatbot integrating patient self-service across web, app, and social channe… |
| `Doctor-Performance-in-Medical` | HR | Clinical Informatics | Physician productivity and performance dashboard for medical specialties — KPIs, patients per sessio… |
| `Doctor-Performance-in-Dental` | HR | Clinical Informatics | Dental specialty physician performance dashboard — chair utilisation, production per dentist.… |

> [!TIP]
> Cross-domain repositories are high-leverage assets. Governance, versioning, and ownership should be clearly assigned to prevent siloed development and ensure consistent data contracts across systems.

---

## 4. Out-of-Scope Repositories

**61 repositories** have been excluded. Exclusion criteria:
- **Marketing / Advertising** — social scraping, sentiment analysis, ad tools
- **Generic ML Demos** — experiments with public datasets, no production application
- **Developer Tooling** — build tools, scaffolding, DevOps utilities
- **Insufficient Evidence** — unclear purpose from dossier analysis


#### Marketing (21 repos)

| Repository | Exclusion Rationale |
|---|---|
| `googlemaps-scraper` | Scrapes Google Maps business listings for competitor/market intelligence. No clinical or operational domain. |
| `Instegram_scrapper_selenium` | Instagram scraper for social media monitoring. Marketing use only. |
| `Scrape-Vezeeta-Automate` | Scrapes Vezeeta (competitor appointment platform) for market data. Not a healthcare operational system. |
| `GoogleReviewsScraper___InsurancePatterns` | Google Reviews scraper with insurance keyword filtering. Marketing sentiment, not insurance operations. |
| `facebook-comments-trial` | Facebook comments scraper / social sentiment trial. Marketing use only. |
| `Ctr_prediction-FB` | Facebook ad click-through-rate prediction. Digital advertising tool, no healthcare domain. |
| `Text-FBpost-Analysis` | Facebook post text analysis for social media marketing insights. |
| `WordOfMouth_SentimentAnalysis` | Word-of-mouth sentiment analysis for brand monitoring. Marketing, not clinical. |
| `Sentiment_STD` | Generic sentiment analysis standard library. Marketing tooling, no domain business logic. |
| `Sentiment-evaluation-function` | Marketing sentiment evaluation utility. No healthcare domain. |
| `SentementAPIs_Second` | Secondary sentiment API — marketing analytics, no clinical or operational application. |
| `Ad-img` | Advertising image generation/processing tool. Digital marketing, out of scope. |
| `Market-Segmentation` | Customer market segmentation for marketing campaigns. Not clinical or operational. |
| `cust_seg_quality_of_life_metrics` | Customer quality-of-life segmentation for marketing purposes. Out of scope. |
| `sem-clustering` | Semantic clustering tool — marketing/content use case, no domain application identified. |
| `feedback-wordcloud-levels` | Patient feedback word-cloud generator for marketing reports. |
| `clusters_wordclouds` | Word-cloud clustering visualisation — marketing analytics artefact. |
| `social_media_agora` | Social media aggregation platform. Marketing channel management tool. |
| `marketing-report-creator` | Automated marketing report generator. Pure marketing domain. |
| `Ads-investigation-tool` | Digital advertising investigation and analytics tool. No healthcare operational function. |
| `Deep-Learning-Model-for-Patient-s-Claims-Sentiment-Classification` | Despite the name, this analyses patient claim *sentiment* for marketing/PR purposes, not claims processing. Out of scope. |

#### Generic ML Demo (17 repos)

| Repository | Exclusion Rationale |
|---|---|
| `MaskYolo_Caffe` | YOLO/Caffe object detection experiment. Generic computer vision benchmark with no clinical application. |
| `Chest-Xray` | Generic chest X-ray classification benchmark (public dataset). Not an operational clinical system. |
| `No-Code-AI` | No-code ML experimentation sandbox. Developer tooling, no domain business logic. |
| `chatGPT-api` | Generic ChatGPT API wrapper / proof-of-concept. No domain application. |
| `BentoML-Demo` | BentoML ML model serving demo. Infrastructure experiment, no domain logic. |
| `fairlearn-demo` | Fairlearn bias/fairness demo. Academic experiment, not production. |
| `Claude_project` | Internal Claude LLM experimentation project. R&D sandbox, not a domain application. |
| `localEmb` | Local embedding server experiment. Infrastructure R&D, no domain logic. |
| `BertTokenizerServer` | Generic BERT tokenizer server. NLP infrastructure experiment, no domain application. |
| `text-similarity` | Generic text similarity utility. No specific healthcare domain application. |
| `similarity_gui` | GUI for text similarity experiments. Generic NLP tooling. |
| `RAG` | Generic RAG (Retrieval-Augmented Generation) experiment — reclassified; if domain-specific version exists it is captured by ClinicalNotes2Features. |
| `Model-Topic-documentation` | Topic model documentation artefact. Internal reference document, not a system. |
| `object-detection-trials` | Generic object detection experiments. No healthcare domain application. |
| `pl-translator` | Generic language translation utility. No domain application confirmed. |
| `ai_google_translation` | Google Translate API wrapper. Generic utility, no domain application. |
| `ctr_prediction_lstm` | LSTM click-through-rate prediction — advertising ML experiment. Out of scope. |

#### Dev Tooling (14 repos)

| Repository | Exclusion Rationale |
|---|---|
| `AutoMapper` | Generic object-to-object mapper library. Developer infrastructure, no domain logic. |
| `automapper-v3` | V3 of AutoMapper. Developer tooling, no domain logic. |
| `template` | Blank project scaffolding template repository. |
| `Code_Automation` | Code generation/automation tooling. Developer productivity, no domain logic. |
| `mlflow_learning` | MLflow learning exercises. Internal DevOps training, not a domain system. |
| `mlflow-team-toolkit` | MLflow toolkit for team use. MLOps infrastructure, no domain business logic. |
| `APIs_withTimeGraph` | Generic API with time-series graph utilities. Infrastructure experiment. |
| `Livekit-guide` | LiveKit real-time audio/video guide. Technical reference document, not a system. |
| `system-pipeline` | Generic system pipeline utilities. DevOps infrastructure, no domain logic. |
| `dist-plan` | Distribution planning utility. Internal DevOps tooling, no domain application. |
| `package-announcement-generator` | Internal package/release announcement generator. Developer tooling. |
| `resources` | Generic shared resources repository. Configuration artefacts, no domain logic. |
| `Temp` | Temporary/scratch repository. No domain content. |
| `Transfer-Learning-Sessions` | Internal ML transfer-learning training sessions. Educational/training artefacts, not a product. |

#### Digital Transformation (4 repos)

| Repository | Exclusion Rationale |
|---|---|
| `Digital-Platforms-APIs` | Generic digital platform API gateway. Not mapped to a specific 17-domain area. |
| `PlayBook` | Internal strategy/playbook document repository. Not an operational system. |
| `Process-Monitoring` | Generic process monitoring tool. Not specific to any domain operational system. |
| `Interview-Chatbot` | Generic interview chatbot — not clinical recruitment (no CV/HR logic). Generic HR demo. |

#### Insufficient Evidence (5 repos)

| Repository | Exclusion Rationale |
|---|---|
| `Topic-Mapping` | Topic mapping utility — generic NLP, no domain application confirmed from dossier. |
| `Technical-Descriptions` | Repository of technical descriptions / reference docs. Not an operational system. |
| `java_voice_recorder` | Java voice recorder — may be prototype for voice pipeline; insufficient evidence of production use. |
| `voice_recognition_service` | Generic voice recognition service — overlaps with Medical Voice stack but insufficient evidence of independent production role. |
| `BigBrother` | Monitoring tool — name and dossier ambiguous; insufficient evidence of healthcare domain application. |

> [!CAUTION]
> Marketing and social-scraping tools carry **legal and reputational risk** (GDPR/PDPL). These repositories should undergo a compliance review before any further development. Consider archiving or deleting repositories with no active use.

---

## 5. Gap Analysis

Domains with **zero** identified repositories represent unaddressed areas in the current data/AI portfolio:

| Domain | Group | Gap Severity | Recommended Action |
|---|---|---|---|
| BD | Business & Customer | 🔴 High | Business Development has zero AI/data tools. No lead tracking, partnership analytics, or opportunity management systems identified. |
| Construction | Operations & Support | 🟡 Medium | No digital twin, project tracking, or BIM integration found. AOH hospital expansion digital coverage is absent from this organisation. |
| L&D / Academy | People | 🟡 Medium | No CME tracking, e-learning, or competency management platforms. Missed opportunity for clinical staff development. |

> [!NOTE]
> **Finance** and **Pricing** gaps are partially mitigated by cross-domain repos (e.g., `Ceo-Summarization` covers Finance KPIs, `Service-Packaging` covers bundle pricing). The most critical gap is **BD** — no data-driven business development capability has been identified.

---

## 6. Detected Standards & Technology Stack

### Healthcare Standards Detected

| Standard | Repos | Domain Coverage |
|---|---|---|
| NPHIES (FHIR) | nphies-ad-engine, Nphies_Simulator, eligibility-etl-airflow, claims-api | Insurance, Medical Coding and Pricing |
| ICD-10 | Upcoding, Diagnosis-Mapping, Final-Diagnosis-Project-, OPD_ClinicalNotes_Analyzer, Clinical_Notes, Lab_Prediction | Medical Coding and Pricing |
| CPT | nphies-ad-engine, Upcoding, CodingSystem | Medical Coding and Pricing |
| DRG | nphies-ad-engine | Medical Coding and Pricing, Insurance |
| DICOM / PACS | AI-In-PACS, radiology-dictation-app | Clinical Informatics |
| SFDA | sfda-scraper | Pharmacy |
| MOH KPIs | MOH, MOH_Automation, MOH_Automation_V4 | Clinical Governance |
| HL7 / FHIR | nphies-ad-engine, Nphies_Simulator, eligibility-etl-airflow | Insurance, Clinical Informatics |

### Core Technology Stack

| Layer | Technologies |
|---|---|
| Languages | Python, Java, JavaScript/TypeScript |
| Frameworks | FastAPI, Flask, LangChain, Fireworks AI |
| ML / AI | scikit-learn, PyTorch, HuggingFace Transformers, YOLO |
| Data & Storage | PostgreSQL (pgvector), SQLite, Apache Airflow |
| DevOps | Docker, GitHub Actions, BentoML, MLflow |
| Voice / ASR | LiveKit, custom acoustic models |
| NLP | BERT, LLMs (ChatGPT, Claude, Fireworks), RAG pipelines |

---

## 7. Strategic Recommendations


| Priority | Recommendation |
|---|---|
| 🔴 Urgent | **Consolidate the Medical Voice stack** — 8+ voice/dictation repos (`MedVoice`, `Medical_voice_FAPI`, `radiology-voice-system`, etc.) suggest fragmented ownership. Establish a single unified service with versioned APIs. |
| 🔴 Urgent | **Governance for Insurance/Coding repos** — `nphies-ad-engine`, `eligibility-etl-airflow`, and `Claims_Deployment` are production systems. Assign formal owners, SLAs, and change-management controls. |
| 🟠 High | **Archive out-of-scope marketing repos** — 19 marketing/social repos carry compliance and resource risk. Archive immediately; conduct PDPL review for any that collected personal data. |
| 🟠 High | **Invest in BD and L&D domains** — Both are completely unaddressed despite being defined strategic pillars. Initiate discovery and scoping in Q1. |
| 🟡 Medium | **Retire duplicate repos** — `Bed-Management` / `bedManagement`, `Patients-No-Show` / `no_show` are functional duplicates. Consolidate and deprecate the older variant. |
| 🟡 Medium | **Formalise cross-domain data contracts** — `claims-prep`, `OPD_ClinicalNotes_Analyzer`, and `AHBS_AIServices` span coding + insurance + pharmacy. Define shared data schemas and API contracts. |
| 🟢 Opportunity | **Productionise predictive models** — `Patient_Segmentation`, `Clinic_Utilization`, `Medical_prediction` are Active Development but have clear production value. Prioritise for deployment. |

---

*Report generated by the Andalusia Healthcare AI Portfolio Intelligence Pipeline. Analysis date: October 29, 2026.*