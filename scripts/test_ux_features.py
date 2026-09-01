import os
from streamlit.testing.v1 import AppTest

def test_citation_popovers_render():
    """
    Automated script to verify the RAG UX Citation Overhaul from a user perspective.
    It simulates a physicist session where citations are retrieved and ensures Streamlit DOM
    components (specifically Popovers) mount seamlessly without hidden exceptions.
    """
    print("Initialize Streamlit AppTest Environment...")
    os.environ["GROQ_API_KEY"] = "mock_key_for_testing"
    
    at = AppTest.from_file("app/streamlit_app_DEPRECATED.py", default_timeout=20)
    
    print("Injecting complex multimodal citation state into Streamlit DOM...")
    # Inject an active session state simulating an LLM response with multiple chunk citations
    at.session_state["chat"] = [
        {
            "role": "assistant",
            "content": "The fast neutron fluence limit dictates deformation criteria [C1]. See diagram [C2].",
            "text_hits": [
                {
                    "citation_id": "[C1]", 
                    "section_type": "text", 
                    "page": 42, 
                    "text": "--MOCK FAST NEUTRON FLUENCE CHUNK--", 
                    "score": 0.999, 
                    "source": "cern_report_mock.pdf"
                }
            ],
            "figure_hits": [
                {
                    "citation_id": "[C2]", 
                    "section_type": "figure", 
                    "page": 44, 
                    "text": "--MOCK DEFORMATION FIGURE DIAGRAM EXPLANATION--", 
                    "score": 0.885, 
                    "image_path": "mock_test_image.png"
                }
            ],
            "table_hits": []
        }
    ]
    
    print("Running Streamlit UI Engine...")
    at.run()
    
    if at.exception:
        print(f"FAILED! Streamlit internal exception detected: {at.exception[0].message}")
        assert False, "Streamlit encountered a fatal exception during render."
        
    print("DOM Assertions Executing...")
    
    # Extract all markdown and textual elements rendered on screen
    all_markdown = [md.value for md in at.markdown if md.value is not None]
    
    # 1. Ensure the generated LLM text exists
    assert any("neutron fluence limit dictates" in m for m in all_markdown), "LLM assistant response failed to mount."
    
    # 2. Ensure Interactive Citations wrapper exists
    assert any("Interactive Citations" in m for m in all_markdown), "Interactive Citations header is missing."
    
    # 3. Ensure the exact textual chunk payload is mounted correctly within the popover structure
    assert any("--MOCK FAST NEUTRON FLUENCE CHUNK--" in m for m in all_markdown), "Text chunk reference failed to render."
    
    # 4. Ensure the exact figure caption chunk payload is mounted correctly within the popover structure
    assert any("--MOCK DEFORMATION FIGURE DIAGRAM EXPLANATION--" in m for m in all_markdown), "Figure chunk reference failed to render."
    
    print("✅ SUCCESS! All UX Citation Popovers and Markdown Elements mounted flawlessly for the user.")

if __name__ == "__main__":
    test_citation_popovers_render()
