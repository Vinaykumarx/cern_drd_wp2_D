import sys
import os

# Append project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import process_text_for_chunks

SAMPLE_TEXT = """
Retrieval-Augmented Generation (RAG) is an AI framework that improves the quality of language model responses by grounding them in external sources of knowledge.
The RAG architecture typically consists of two main components: a retriever and a generator.
The retriever searches a knowledge base (often a vector database) for relevant documents based on the user's query.
It uses embedding models to convert text into numerical vectors that capture semantic meaning.
Once the relevant documents are retrieved, they are appended to the user's prompt.
The generator, which is usually a Large Language Model (LLM), then reads this augmented prompt and produces a final answer.
One of the major challenges in RAG is chunking the documents effectively. If chunks are too small, they lose context. If they are too large, they dilute the semantic match and exceed token limits.
"""

def run_test():
    print("Sending sample text to local Agentic Semantic Chunker (Ollama/vLLM)...\n")
    print(f"Sample Text:\n{SAMPLE_TEXT}\n")
    print("-" * 50)
    
    try:
        chunks = process_text_for_chunks(SAMPLE_TEXT)
        if not chunks:
            print("No chunks returned. Check if your LLM is running properly.")
            return
            
        for i, chunk in enumerate(chunks):
            print(f"CHUNK {i+1}:")
            print(f"  Title    : {chunk.title}")
            print(f"  Summary  : {chunk.summary}")
            print(f"  Keywords : {chunk.keywords}")
            print(f"  Score    : {chunk.quality_score}")
            print(f"  Why      : {chunk.why_this_chunk_exists}")
            print(f"  Content  : {chunk.text}\n")
            
        print("Success! Agentic Chunking works.")
    except Exception as e:
        print(f"Error during chunking: {e}")
        print("Make sure Ollama or vLLM is running on localhost:11434 and 'llama3.1' (or your target model) is pulled.")

if __name__ == "__main__":
    run_test()
