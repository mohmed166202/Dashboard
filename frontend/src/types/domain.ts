export interface HealthcareDomain {
  id: string;
  name: string;
  description: string;
  standards: string[];
  tokenCount: number;
  coveragePercentage: number;
}

export const HEALTHCARE_DOMAINS: HealthcareDomain[] = [
  {
    id: "clinical-informatics",
    name: "Clinical Informatics",
    description: "HIS, EMR/EHR systems, clinical workflows, triage, notes, and doctor/nurse order entry.",
    standards: ["FHIR", "HL7", "DICOM", "PACS", "CPOE", "HIS", "EMR"],
    tokenCount: 18,
    coveragePercentage: 94.2,
  },
  {
    id: "clinical-governance",
    name: "Clinical Governance",
    description: "Quality & safety of patient care, policies, JCI/GAHAR accreditation, incident reporting & audits.",
    standards: ["GAHAR", "JCI", "OVR", "Patient Safety", "Clinical Audit"],
    tokenCount: 15,
    coveragePercentage: 88.5,
  },
  {
    id: "medical-coding-pricing",
    name: "Medical Coding and Pricing",
    description: "ICD and CPT coding, tariff schedules, fee sheets, insurance claims, and billing rules.",
    standards: ["ICD-10", "CPT", "DRG", "Claims", "Tariff"],
    tokenCount: 14,
    coveragePercentage: 91.0,
  },
  {
    id: "patient-access",
    name: "Patient Access & Front Office",
    description: "Scheduling, registration, call center, eligibility checks, admission, and front-desk workflows.",
    standards: ["Eligibility", "Appointments", "CRM", "Kiosk", "FrontDesk"],
    tokenCount: 12,
    coveragePercentage: 86.4,
  },
  {
    id: "pharmacy-medication",
    name: "Pharmacy & Medication",
    description: "Inpatient/outpatient dispensing, formulary, medication reconciliation, e-prescribing, inventory.",
    standards: ["ATC", "RxNorm", "Formulary", "Dispensing", "ePrescription"],
    tokenCount: 16,
    coveragePercentage: 93.8,
  },
  {
    id: "laboratory-pathology",
    name: "Laboratory & Pathology",
    description: "LIS analyzers, specimen collection, test results, microbiology, blood bank, reference ranges.",
    standards: ["LOINC", "LIS", "Analyzers", "Pathology", "BloodBank"],
    tokenCount: 14,
    coveragePercentage: 89.1,
  },
  {
    id: "radiology-imaging",
    name: "Radiology & Imaging",
    description: "RIS/PACS systems, modality worklists, imaging protocols, radiologist reporting, DICOM routing.",
    standards: ["DICOM", "RIS", "PACS", "Modality", "PeerReview"],
    tokenCount: 13,
    coveragePercentage: 95.0,
  },
  {
    id: "nursing-inpatient",
    name: "Nursing & Inpatient Operations",
    description: "Bed management, shift handover, nursing care plans, MAR, vital signs charting, ward rounding.",
    standards: ["MAR", "Kardex", "BedBoard", "ShiftHandover", "VitalSigns"],
    tokenCount: 15,
    coveragePercentage: 87.6,
  },
  {
    id: "revenue-cycle",
    name: "Revenue Cycle & Billing",
    description: "Pre-auth, denial management, financial clearance, insurance reconciliation, revenue integrity.",
    standards: ["837/835 EDI", "PriorAuth", "Denials", "Clearinghouse"],
    tokenCount: 17,
    coveragePercentage: 92.4,
  },
];

export interface DashboardMetrics {
  totalDomains: number;
  totalTokens: number;
  matrixCoverage: number;
  activeRepositories: number;
  changeRate: number;
}

export const INITIAL_METRICS: DashboardMetrics = {
  totalDomains: 9,
  totalTokens: 134,
  matrixCoverage: 91.8,
  activeRepositories: 42,
  changeRate: +4.8,
};

