"""
Hybrid Domain Classifier for Phase 3.
Combines:
  1. High-precision rule & regex pattern engine (GAHAR, JCI, ICD-10, CPT, AOH, etc.)
  2. Vector space profiling (Cosine similarity against canonical domain profiles)
  3. Structured LLM assessment (Strict JSON schema output via Gemini/OpenAI with deterministic fallback)
"""

import json
import logging
import math
import os
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple
import requests

from config import Config
from domain_taxonomy import HEALTHCARE_DOMAINS, DomainDefinition

logger = logging.getLogger("HybridClassifier")


class RulePatternEngine:
    """Layer 1: Rule & Regex Pattern Matcher."""

    @classmethod
    def evaluate(cls, dossier_text: str, extracted_entities: List[str], repo_name: str) -> Dict[str, Dict[str, Any]]:
        text_lower = (dossier_text + " " + repo_name.replace("-", " ").replace("_", " ")).lower()
        results = {}

        for domain_name, defn in HEALTHCARE_DOMAINS.items():
            matches = 0
            detected_tokens = []
            detected_standards = []

            # Check high-precision regex tokens
            for token_pattern in defn.high_precision_tokens:
                found = re.findall(token_pattern, text_lower)
                if found:
                    count = len(found)
                    matches += count
                    clean_token = token_pattern.replace(r"\b", "").replace(r"-?", "-")
                    detected_tokens.append(f"{clean_token}({count})")

            # Check specialized standards (e.g. GAHAR, JCI, AOH, ICD-10)
            for std in defn.specialized_standards:
                std_pattern = r"\b" + re.escape(std.lower()) + r"\b"
                if re.search(std_pattern, text_lower):
                    detected_standards.append(std)
                    matches += 5  # Heavily weight explicit standards

            # Cross-check extracted entities
            for ent in extracted_entities:
                ent_clean = ent.lower()
                for token_pattern in defn.high_precision_tokens:
                    if re.search(token_pattern, ent_clean):
                        matches += 2

            results[domain_name] = {
                "score": matches,
                "detected_tokens": detected_tokens[:10],
                "detected_standards": detected_standards,
            }

        return results


class VectorSpaceProfiler:
    """Layer 2: Vector Space Profiling using Cosine Similarity."""

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

    @classmethod
    def compute_cosine_similarity(cls, text_a: str, text_b: str) -> float:
        words_a = cls._tokenize(text_a)
        words_b = cls._tokenize(text_b)
        if not words_a or not words_b:
            return 0.0

        vec_a = Counter(words_a)
        vec_b = Counter(words_b)

        intersection = set(vec_a.keys()) & set(vec_b.keys())
        numerator = sum([vec_a[x] * vec_b[x] for x in intersection])

        sum1 = sum([vec_a[x]**2 for x in vec_a.keys()])
        sum2 = sum([vec_b[x]**2 for x in vec_b.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    @classmethod
    def profile(cls, dossier_text: str) -> Dict[str, float]:
        scores = {}
        for domain_name, defn in HEALTHCARE_DOMAINS.items():
            sim = cls.compute_cosine_similarity(dossier_text, defn.semantic_profile_text)
            scores[domain_name] = round(sim, 4)
        return scores


class LLMAssessmentEngine:
    """Layer 3: Structured LLM Assessment (Gemini or OpenAI)."""

    SYSTEM_PROMPT = """You are an expert Chief Medical Information Officer (CMIO) and Healthcare Systems Architect.
Your task is to analyze the provided repository dossier and classify it into the 9 healthcare and operational domains:
1. Clinical Informatics
2. Clinical Governance
3. Medical Coding and Pricing
4. Human Resources
5. Academy and L&D
6. Pharmacy
7. Supply Chain
8. Finance
9. Construction

Guidelines:
- If a repo fits multiple domains, select the dominant one as 'primary_domain' and related ones in 'secondary_domains'.
- Provide a confidence score between 0.00 and 1.00.
- Highlight detected standards (e.g. GAHAR, JCI, ICD-10, CPT, AOH, FHIR, BOQ, LASA).
- Return ONLY valid JSON matching this schema:
{
  "repo_name": "...",
  "primary_domain": "...",
  "secondary_domains": ["..."],
  "confidence_score": 0.95,
  "domain_justification": "Detailed explanation of why this belongs to the domain.",
  "detected_standards": ["..."],
  "project_status": "Active / In Development | Production | Legacy | Prototype",
  "key_technologies": ["..."]
}"""

    @classmethod
    def call_gemini(cls, prompt_content: str, api_key: str, model: str = "gemini-1.5-pro") -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": cls.SYSTEM_PROMPT},
                        {"text": prompt_content}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=40)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_text)
            else:
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Gemini API invocation error: {e}")
        return None


class HybridClassifier:
    """Orchestrates Rule Engine + Vector Space + LLM Assessment."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_key = gemini_api_key or Config.GEMINI_API_KEY

    def classify(self, dossier: Dict[str, Any], force_offline: bool = False) -> Dict[str, Any]:
        repo_name = dossier.get("repo_name", "unknown")
        name_with_owner = dossier.get("name_with_owner", repo_name)
        dossier_text = dossier.get("dossier_markdown", "")
        entities = dossier.get("extracted_entities", [])
        dependencies = dossier.get("extracted_dependencies", [])
        apis = dossier.get("extracted_apis", [])

        # 1. Rule Pattern Matcher
        rule_results = RulePatternEngine.evaluate(dossier_text, entities, repo_name)

        # 2. Vector Space Profiler
        vector_scores = VectorSpaceProfiler.profile(dossier_text)

        # Combine rule and vector signals into candidate ranks
        combined_scores = {}
        all_detected_standards = set()

        for d_name in HEALTHCARE_DOMAINS.keys():
            r_score = rule_results[d_name]["score"]
            v_score = vector_scores[d_name]
            # Normalized hybrid weight
            combined = (r_score * 0.65) + (v_score * 100 * 0.35)
            combined_scores[d_name] = round(combined, 2)
            all_detected_standards.update(rule_results[d_name]["detected_standards"])

        # Sort candidate domains
        ranked_candidates = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_domain = ranked_candidates[0][0]
        top_score = ranked_candidates[0][1]

        # 3. LLM Assessment (if key present and not offline)
        if not force_offline and self.gemini_key:
            prompt_content = f"""
Analyze and classify this repository:
Repository: {name_with_owner}
Rule-based Scores: {json.dumps({k: v for k, v in ranked_candidates[:4]})}
Detected Standards: {list(all_detected_standards)}
Discovered Entities: {entities[:25]}
Dependencies: {dependencies[:15]}

Dossier Summary:
{dossier_text[:15000]}
"""
            llm_result = LLMAssessmentEngine.call_gemini(
                prompt_content=prompt_content,
                api_key=self.gemini_key,
                model=Config.GEMINI_MODEL or "gemini-1.5-pro"
            )
            if llm_result and "primary_domain" in llm_result:
                llm_result["repo_name"] = repo_name
                llm_result["name_with_owner"] = name_with_owner
                return llm_result

        # 4. Deterministic Fallback Engine (Zero crash guaranteed)
        # Identify secondary domains with meaningful signal
        secondaries = []
        for d_name, sc in ranked_candidates[1:3]:
            if sc > (top_score * 0.40) and sc > 2.0:
                secondaries.append(d_name)

        # Calculate confidence metric
        confidence = 0.50
        if top_score > 25:
            confidence = 0.95
        elif top_score > 15:
            confidence = 0.88
        elif top_score > 5:
            confidence = 0.78
        elif top_score > 1:
            confidence = 0.65

        # Key technologies
        key_tech = []
        for dep in dependencies[:8]:
            key_tech.append(dep.split("/")[-1].replace("service:", "").replace("image:", ""))

        justification = (
            f"Repository '{name_with_owner}' matches primary domain '{top_domain}' with hybrid score {top_score}. "
            f"Identified domain signatures: {list(all_detected_standards) or 'heuristic patterns'}."
        )

        return {
            "repo_name": repo_name,
            "name_with_owner": name_with_owner,
            "primary_domain": top_domain,
            "secondary_domains": secondaries,
            "confidence_score": round(confidence, 2),
            "domain_justification": justification,
            "detected_standards": sorted(list(all_detected_standards)),
            "project_status": "Active / In Development",
            "key_technologies": key_tech[:6] or ["Codebase"]
        }

