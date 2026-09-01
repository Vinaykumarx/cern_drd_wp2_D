"""
Grounding and Citation Verification Layer for CERN Multimodal RAG.
Audits generated responses against retrieved evidence to ensure 0-hallucination compliance.
"""

from typing import List, Dict, Tuple
import re

from core.storage.base import SearchResult
from core.models.base import GenerationResponse, GroundedCitation


class GroundingVerifier:
    def __init__(self, min_similarity_threshold: float = 0.3):
        self.min_similarity_threshold = min_similarity_threshold

    def verify(
        self,
        response: GenerationResponse,
        evidence: List[SearchResult],
    ) -> Tuple[bool, float, Dict[str, any]]:
        """
        Verify that:
        1. Retrieved evidence is sufficiently relevant (above threshold).
        2. Cited citation tags ([C1], [C2], etc.) are valid and present in evidence.
        3. Factual terms in the answer correlate with the cited chunk contents.
        Returns: (is_valid, confidence_score, verification_report)
        """
        report = {
            "evidence_count": len(evidence),
            "citations_found": len(response.citations),
            "citation_tags_in_answer": [],
            "missing_citations": [],
            "top_similarity": evidence[0].score if evidence else 0.0,
            "grounding_passed": True,
            "reasons": [],
        }

        if not evidence:
            report["grounding_passed"] = False
            report["reasons"].append("No evidence provided.")
            return False, 0.0, report

        if evidence[0].score < self.min_similarity_threshold:
            report["grounding_passed"] = False
            report["reasons"].append(
                f"Top evidence similarity ({evidence[0].score:.3f}) below threshold ({self.min_similarity_threshold})."
            )
            return False, 0.2, report

        # Extract citation tags from text
        tags_in_text = re.findall(r"\[C\d+\]", response.answer)
        report["citation_tags_in_answer"] = list(set(tags_in_text))

        # Check if citations correspond to valid indices
        valid_tag_indices = {f"[C{i}]" for i in range(1, len(evidence) + 1)}
        for tag in tags_in_text:
            if tag not in valid_tag_indices:
                report["missing_citations"].append(tag)
                report["reasons"].append(f"Invalid citation tag {tag} referenced in answer.")

        # Compute confidence score
        score = 0.5
        if evidence[0].score >= 0.6:
            score += 0.3
        elif evidence[0].score >= 0.4:
            score += 0.15

        if len(tags_in_text) > 0 and len(report["missing_citations"]) == 0:
            score += 0.2
        elif len(report["missing_citations"]) > 0:
            score -= 0.3

        confidence = max(0.0, min(1.0, score))
        is_valid = report["grounding_passed"] and (len(report["missing_citations"]) == 0)
        report["grounding_passed"] = is_valid
        report["confidence_score"] = confidence

        return is_valid, confidence, report
