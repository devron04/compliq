"""
CompliQ - From product to standard, instantly.
src/app.py

Gradio UI for the MSE owner.
Provides a simple interface to describe a product and get back relevant BIS standards.
"""

import os
import sys
import time
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import gradio as gr
except ImportError:
    print("gradio is required. Install via: pip install gradio", file=sys.stderr)
    sys.exit(1)

from src.pipeline import BISPipeline

print("Loading pipeline...", file=sys.stderr)
try:
    pipeline = BISPipeline(data_dir=os.path.join(os.path.dirname(__file__), '..', 'data'))
except Exception as e:
    print(f"Failed to load pipeline: {e}", file=sys.stderr)
    pipeline = None

CATEGORIES = ["All", "Cement", "Steel", "Concrete", "Aggregates", "Bricks", "Tiles", "Pipes", "Glass", "Timber", "Other"]

def predict(query, category):
    if not pipeline:
        return "### Error: Pipeline not loaded", "Latency: N/A"
        
    print(f"\n--- New Query: '{query}' [Category: {category}] ---", file=sys.stderr)
    start_time = time.perf_counter()
    
    if category and category != "All":
        enhanced_query = f"[{category}] {query}"
    else:
        enhanced_query = query
        
    try:
        print("1. Searching context (Hybrid Search)...", file=sys.stderr)
        results = pipeline.query(enhanced_query, return_full=True)
        print(f"2. Found {len(results)} standards.", file=sys.stderr)
    except Exception as e:
        print(f"ERROR during query: {e}", file=sys.stderr)
        return f"### Error: {e}", "Latency: N/A"
        
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    if not results:
        md_output = "### No results found.\nCould not find matching standards in the context."
    else:
        md_output = "## Recommended Standards\n\n"
        for idx, rec in enumerate(results):
            md_output += f"### {idx+1}. {rec.get('standard_id', 'N/A')}\n"
            md_output += f"**Title:** {rec.get('title', 'N/A')}\n\n"
            md_output += f"**Rationale:** {rec.get('rationale', 'N/A')}\n\n"
            md_output += "---\n\n"
            
    latency_str = f"⏱️ Query completed in {latency_ms:.0f} ms"
    print("3. Data sent to UI. Check browser!", file=sys.stderr)
    return md_output, latency_str

with gr.Blocks(title="CompliQ - BIS Standards Finder") as demo:
    gr.Markdown("# CompliQ")
    gr.Markdown("### From product to standard, instantly.")
    gr.Markdown("Describe your building material below to find the applicable Bureau of Indian Standards (BIS).")
    
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                lines=3, 
                placeholder="E.g., I manufacture high-strength deformed steel bars for concrete reinforcement...",
                label="Product Description"
            )
        with gr.Column(scale=1):
            category_dropdown = gr.Dropdown(
                choices=CATEGORIES,
                value="All",
                label="Filter by Category"
            )
            submit_btn = gr.Button("Find Standards", variant="primary")
            
    with gr.Row():
        latency_text = gr.Markdown("⏱️ Latency: -")

    # Simple Markdown output
    output_md = gr.Markdown("Results will appear here...")

    gr.Examples(
        examples=[
            ["I am making ordinary portland cement 53 grade.", "Cement"],
            ["Manufacturing coarse and fine aggregates from natural sources for concrete.", "Aggregates"],
            ["I produce high strength deformed steel bars for concrete reinforcement.", "Steel"]
        ],
        inputs=[query_input, category_dropdown]
    )

    submit_btn.click(
        fn=predict,
        inputs=[query_input, category_dropdown],
        outputs=[output_md, latency_text]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
