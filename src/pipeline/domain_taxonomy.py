"""
Healthcare & Operational Domain Taxonomy.
Defines canonical scopes, regex patterns, specialized standards, and semantic
profile texts for the 9 healthcare domains.
"""

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class DomainDefinition:
    name: str
    description: str
    high_precision_tokens: List[str]
    specialized_standards: List[str]
    semantic_profile_text: str


HEALTHCARE_DOMAINS: Dict[str, DomainDefinition] = {
    "Clinical Informatics": DomainDefinition(
        name="Clinical Informatics",
        description="The technology behind patient care, including the hospital information system (HIS), electronic medical records (EMR/EHR), clinical data accuracy, and how doctors and nurses use digital tools in daily work.",
        high_precision_tokens=[
            r"\bhis\b", r"\behr\b", r"\bemr\b", r"\bfhir\b", r"\bhl7\b", r"\bdicom\b",
            r"\bpacs\b", r"\bcpoe\b", r"\bpatient\b", r"\bencounter\b", r"\btriage\b",
            r"\bclinical_note\b", r"\bsoap\b", r"\bvital\b", r"\bdoctor_order\b",
            r"\bnursing_assessment\b", r"\btelemedicine\b", r"\be-prescription\b"
        ],
        specialized_standards=["FHIR", "HL7", "DICOM", "PACS", "CPOE", "HIS", "EMR"],
        semantic_profile_text="Hospital information systems HIS electronic medical records EMR EHR clinical workflow patient encounter vitals doctor nurse bedside triage medical notes computerized physician order entry CPOE FHIR HL7 interoperability digital health clinical documentation clinical decision support PACS DICOM radiology imaging."
    ),

    "Clinical Governance": DomainDefinition(
        name="Clinical Governance",
        description="The quality and safety of patient care, including clinical policies, accreditation (such as JCI and GAHAR), incident reporting, audits, infection control, and clinical outcome KPIs.",
        high_precision_tokens=[
            r"\bgahar\b", r"\bjci\b", r"\baccreditation\b", r"\bovr\b", r"\bincident_report\b",
            r"\bclinical_audit\b", r"\binfection_control\b", r"\bhand_hygiene\b",
            r"\badverse_event\b", r"\broot_cause\b", r"\bkpi\b", r"\bclinical_governance\b",
            r"\bmortality\b", r"\bmorbidity\b", r"\bpatient_safety\b", r"\bquality_improvement\b"
        ],
        specialized_standards=["GAHAR", "JCI", "OVR", "Patient Safety", "Clinical Audit", "Infection Control"],
        semantic_profile_text="Clinical governance patient safety healthcare quality accreditation GAHAR JCI Joint Commission international incident reporting occurrence variance report OVR clinical audits infection control hygiene clinical indicator KPI morbidity mortality review adverse events medical compliance."
    ),

    "Medical Coding and Pricing": DomainDefinition(
        name="Medical Coding and Pricing",
        description="Turning diagnoses and procedures into standard codes (ICD and CPT), setting service prices and packages, and making sure claims to insurers and contracted companies are accurate and get paid.",
        high_precision_tokens=[
            r"\bicd-?10\b", r"\bicd-?11\b", r"\bcpt\b", r"\bachi\b", r"\bdrg\b",
            r"\bclaim\b", r"\bclaims\b", r"\bpre-?auth\b", r"\bpreauthorization\b",
            r"\binsurance_tariff\b", r"\bprice_master\b", r"\bservice_package\b",
            r"\btpa\b", r"\brejection_code\b", r"\bpayer\b", r"\bdenial_management\b"
        ],
        specialized_standards=["ICD-10", "ICD-11", "CPT", "ACHI", "DRG", "TPA", "Pre-Auth"],
        semantic_profile_text="Medical coding clinical classification ICD-10 ICD-11 CPT procedure codes ACHI DRG diagnosis related groups insurance claims processing pre-authorization tariff price list service packages payer third-party administrator TPA claim denial rejection codes."
    ),

    "Human Resources": DomainDefinition(
        name="Human Resources",
        description="The workforce, including hiring doctors, nurses and staff, credentialing, payroll, performance management, retention, and staffing levels across the branches.",
        high_precision_tokens=[
            r"\bcredentialing\b", r"\bprivileging\b", r"\bmedical_license\b", r"\brota\b",
            r"\bdoctor_shift\b", r"\bnurse_shift\b", r"\bpayroll\b", r"\bemployee_master\b",
            r"\battendance\b", r"\bretention\b", r"\bstaffing_level\b", r"\bstaffing_ratio\b",
            r"\bhrms\b", r"\bonboarding_staff\b", r"\bcompensation\b"
        ],
        specialized_standards=["Credentialing", "Privileging", "HRMS", "Shift Rota", "Payroll"],
        semantic_profile_text="Human resources hospital workforce doctor nursing staff credentialing clinical privileging medical licensing payroll compensation shift scheduling rota attendance performance appraisal employee retention headcount staffing ratios."
    ),

    "Academy and L&D": DomainDefinition(
        name="Academy and L&D",
        description="Staff training and development, including clinical and non-clinical courses, onboarding, CME for doctors, nursing programs, certifications, and building future leaders.",
        high_precision_tokens=[
            r"\bcme\b", r"\bcpd\b", r"\bcontinuing_medical_education\b", r"\bresidency\b",
            r"\bfellowship\b", r"\bclinical_simulation\b", r"\blms\b", r"\btraining_program\b",
            r"\bnursing_competency\b", r"\bcertification\b", r"\bcurriculum\b",
            r"\bleadership_development\b", r"\blearning_management\b"
        ],
        specialized_standards=["CME", "CPD", "LMS", "Clinical Simulation", "Residency"],
        semantic_profile_text="Academy learning and development L&D continuing medical education CME CPD clinical simulation training hospital LMS learning management system residency fellowship nursing competency certifications doctor onboarding leadership programs."
    ),

    "Pharmacy": DomainDefinition(
        name="Pharmacy",
        description="Everything about medicines, including the formulary, drug stock, dispensing, medication safety, controlled drugs, and pharmacy revenue.",
        high_precision_tokens=[
            r"\bformulary\b", r"\bprescription\b", r"\brx\b", r"\bdispense\b",
            r"\bdispensing\b", r"\bunit_dose\b", r"\blasa\b", r"\bnarcotics?\b",
            r"\bcontrolled_drugs?\b", r"\badr\b", r"\badverse_drug\b", r"\bdrug_interaction\b",
            r"\bmedication_safety\b", r"\bpharmacovigilance\b", r"\bpharmacy_revenue\b"
        ],
        specialized_standards=["Formulary", "LASA", "Unit-Dose", "Controlled Substances", "Pharmacovigilance"],
        semantic_profile_text="Hospital pharmacy medication drugs hospital formulary pharmaceutical dispensing unit-dose medication safety Look-Alike Sound-Alike LASA high-alert medications controlled substances narcotics adverse drug reactions ADR drug interactions pharmacy revenue."
    ),

    "Supply Chain": DomainDefinition(
        name="Supply Chain",
        description="Getting the right items at the right cost, including procurement, vendor management, warehouses and inventory, and the availability of medical supplies and equipment.",
        high_precision_tokens=[
            r"\bprocurement\b", r"\brfp\b", r"\brfq\b", r"\bvendor_management\b",
            r"\bpurchase_orders?\b", r"\bpo_item\b", r"\bwarehouse\b", r"\bcentral_store\b",
            r"\bconsignment\b", r"\bbiomedical\b", r"\bcmms\b", r"\bcold_chain\b",
            r"\bsafety_stock\b", r"\bmedical_supplies\b", r"\bequipment_maintenance\b"
        ],
        specialized_standards=["Procurement", "CMMS", "Cold Chain", "Consignment", "PO Management"],
        semantic_profile_text="Supply chain procurement vendor management purchasing purchase orders warehouse inventory management medical supplies medical equipment biomedical engineering CMMS maintenance cold chain storage consignment stock stock depletion safety stock."
    ),

    "Finance": DomainDefinition(
        name="Finance",
        description="The company’s financial health, including revenue by hospital and department, costs, budgets, cash collection, insurance receivables, profitability, and financial reporting.",
        high_precision_tokens=[
            r"\brcm\b", r"\brevenue_cycle\b", r"\baccounts_receivable\b", r"\bar_aging\b",
            r"\bebitda\b", r"\bcost_center\b", r"\bgeneral_ledger\b", r"\bbilling\b",
            r"\bcash_collection\b", r"\bprofitability\b", r"\bunbilled_receivables\b",
            r"\bbudget_variance\b", r"\bfinancial_reporting\b", r"\bprofit_and_loss\b"
        ],
        specialized_standards=["RCM", "AR Aging", "General Ledger", "EBITDA", "Cost Accounting"],
        semantic_profile_text="Hospital finance revenue cycle management RCM accounts receivable AR aging cash collection insurance receivables hospital billing EBITDA cost centers budget variance general ledger financial reporting profitability balance sheet."
    ),

    "Construction": DomainDefinition(
        name="Construction",
        description="New buildings and expansions, such as the AOH hospital project. This covers project timelines, budgets, contractors, engineering packages, and long-lead equipment.",
        high_precision_tokens=[
            r"\baoh\b", r"\baoh_project\b", r"\baoh_hospital\b", r"\bboq\b",
            r"\bbill_of_quantities\b", r"\bcontractors?\b", r"\bsubcontractors?\b",
            r"\bmep\b", r"\blong_lead_equipment\b", r"\bhvac\b", r"\bcleanroom\b",
            r"\bbunkers?\b", r"\blinac\b", r"\bmri_suite\b", r"\bsite_milestones?\b",
            r"\bcivil_engineering\b", r"\barchitectural_package\b"
        ],
        specialized_standards=["AOH", "AOH Project", "BOQ", "MEP", "Long-Lead Equipment", "Cleanroom HVAC"],

        semantic_profile_text="Hospital construction expansion civil engineering architecture AOH hospital project bill of quantities BOQ contractors subcontractors MEP mechanical electrical plumbing long-lead equipment medical bunkers Linac MRI suite cleanrooms HVAC commissioning milestones."
    )
}
