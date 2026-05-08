"""
CompliQ - From product to standard, instantly.
src/app.py

Gradio UI for the MSE owner.
Provides a simple interface to describe a product and get back relevant BIS standards.
"""

import time
import sys
import os

try:
    import gradio as gr
except ImportError:
    print("gradio is required. Install via: pip install gradio", file=sys.stderr)
    sys.exit(1)

from pipeline import BISPipeline

print("Loading pipeline...", file=sys.stderr)
try:
    pipeline = BISPipeline(data_dir=os.path.join(os.path.dirname(__file__), '..', 'data'))
except Exception as e:
    print(f"Failed to load pipeline: {e}", file=sys.stderr)
    pipeline = None

CATEGORIES = ["All", "Cement", "Steel", "Concrete", "Aggregates", "Bricks", "Tiles", "Pipes", "Glass", "Timber", "Other"]

def predict(query, category):
    if not pipeline:
        return [["Error", "Pipeline not loaded", "", "Check logs"]], "Latency: N/A"
        
    start_time = time.perf_counter()
    
    # We can use the category filter by pre-filtering chunks, but for the MVP
    # and since the LLM takes care of relevance, we'll pass the query.
    # If a specific category is chosen, we prepend it to the query to guide the retrieval.
    if category and category != "All":
        enhanced_query = f"[{category}] {query}"
    else:
        enhanced_query = query
        
    try:
        results = pipeline.query(enhanced_query, return_full=True)
    except Exception as e:
        return [[f"Error: {e}", "", "", ""]], "Latency: N/A"
        
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    table_data = []
    if not results:
        table_data = [["No results", "Could not find matching standards in the context.", "", ""]]
    else:
        for idx, rec in enumerate(results):
            # Relevance Score logic (just a simple heuristic for UI)
            score = "High" if idx < 2 else "Medium"
            table_data.append([
                rec.get("standard_id", "N/A"),
                rec.get("title", "N/A"),
                score,
                rec.get("rationale", "N/A")
            ])
            
    latency_str = f"⏱️ Query completed in {latency_ms:.0f} ms"
    return table_data, latency_str

with gr.Blocks(title="CompliQ - BIS Standards Finder", theme=gr.themes.Soft(primary_hue="blue")) as demo:
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

    results_table = gr.Dataframe(
        headers=["IS Number", "Title", "Relevance Score", "Rationale"],
        datatype=["str", "str", "str", "str"],
        row_count=5,
        col_count=(4, "fixed"),
        label="Recommended Standards",
        wrap=True
    )

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
        outputs=[results_table, latency_text]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
