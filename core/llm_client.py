import os
import json
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI

class SemanticChunk(BaseModel):
    text: str = Field(description="The chunk text.")
    title: str = Field(description="A short title for this chunk.")
    topic: str = Field(description="The high-level category (e.g. Safety, Radiation, Equipment, Procedure).")
    summary: str = Field(description="A 1-sentence summary of this chunk.")
    keywords: List[str] = Field(description="5-10 keywords summarizing the chunk.")
    why_this_chunk_exists: str = Field(description="A node on why this chunk exists according to the decision policy.")
    quality_score: float = Field(description="A quality score (1.0 to 10.0) assessing whether it is likely to retrieve well.")

class SemanticChunkResponse(BaseModel):
    chunks: List[SemanticChunk]

def get_client():
    # Ensure env is re-read if needed
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[LLM Warning] OPENROUTER_API_KEY is not set.")
    
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "CERN RAG Swarm"
        }
    )



SYSTEM_PROMPT = """You are the Lead Scientific Intelligence Agent for CERN. 
Your goal is to transform scientific text into search-optimized semantic chunks.

Decision policy:
- Physics Accuracy: Never split a sentence that mentions an LHC experiment (ATLAS, CMS, ALICE, LHCb) away from its technical parameter.
- Safety First: If a paragraph defines a radiation threshold or safety limit (e.g., Sv/hr, rads), encapsulate it in a single high-quality chunk.
- Concept Boundaries: Split when a paragraph introduces a new concept, physical rule, or entity.
- Procedural Integrity: For step-by-step experiment procedures, keep one coherent cycle per chunk.
- Preservation: Keep formulas, parameters, and constraints directly with their verbal explanation.

Output JSON only mapping to the SemanticChunkResponse schema with these fields for every chunk:
1. "text": The chunk text.
2. "title": A short scientific title.
3. "topic": Use one of [Safety, Radiation, Equipment, Experiment, Procedure, Software, General].
4. "summary": A 1-sentence technical summary.
5. "keywords": 5-10 technical keywords.
6. "why_this_chunk_exists": Note why this split point was chosen (e.g. 'Safety threshold transition').
7. "quality_score": A score (1-10) assessing readability and answerability.

Do not:
- Over-split mathematical definitions.
- Separate tables from their explanatory text.
- Produce overlapping chunks unless overlap is required for conceptual continuity.
"""

def process_text_for_chunks(text: str, model_override: str = None) -> List[SemanticChunk]:
    """
    Sends the text block to the LLM and asks it to chunk it semantically.
    """
    model_name = model_override or os.getenv("AGENT_LLM_MODEL", "llama-3.3-70b-versatile")
    client = get_client()

    if not text or not text.strip():
        return []
        
    try:
        # Attempt structured parse first
        try:
            response = client.beta.chat.completions.parse(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Input text to chunk:\n\n{text}"}
                ],
                response_format=SemanticChunkResponse,
                temperature=0.1
            )
            parsed = response.choices[0].message.parsed
            if parsed and parsed.chunks:
                return parsed.chunks
        except Exception as parse_err:
            print(f"[LLM Chunking] .parse() failed, falling back to raw completion: {parse_err}")
            # Fallback to manual JSON extraction for models like Groq that don't support json_schema yet
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + "\nIMPORTANT: Return ONLY valid JSON matching the schema."},
                    {"role": "user", "content": f"Input text to chunk:\n\n{text}"}
                ],
                temperature=0.1
            )
            raw_content = response.choices[0].message.content
            # Extract JSON block
            import re
            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                chunks = []
                for c in data.get("chunks", []):
                    chunks.append(SemanticChunk(**c))
                if chunks:
                    return chunks
            
        return []
        
    except Exception as e:
        print(f"[LLM Chunking Error] Failed to process chunk via LLM: {e}")
        # Return a fallback chunk so we don't lose data on error
        return [
            SemanticChunk(
                text=text,
                title="Recovered Technical Document Section",
                topic="Radiation",
                summary="This chunk contains technical parameters and experimental data extracted from the document.",
                keywords=["CERN", "parameters", "experiment"],
                why_this_chunk_exists="Fallback chunk to preserve document integrity",
                quality_score=5.0 # Higher score to prevent RAG from ignoring it
            )
        ]
