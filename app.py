import os
import sys
import time
import gradio as gr
from src.pipeline import BISPipeline

# Initialize pipeline
print("Loading pipeline...", file=sys.stderr)
try:
    pipeline = BISPipeline(data_dir=os.path.join(os.path.dirname(__file__), 'data'))
except Exception as e:
    print(f"Failed to load pipeline: {e}", file=sys.stderr)
    pipeline = None

CATEGORIES = ["All", "Cement", "Steel", "Concrete", "Aggregates", "Bricks", "Tiles", "Pipes", "Glass", "Timber", "Other"]

def predict(query, category):
    if not pipeline: return "### Error: Pipeline not loaded", "Latency: N/A"
    start_time = time.perf_counter()
    enhanced_query = f"[{category}] {query}" if category and category != "All" else query
    try:
        results = pipeline.query(enhanced_query, return_full=True)
    except Exception as e:
        return f"### Error: {e}", "Latency: N/A"
    latency_ms = (time.perf_counter() - start_time) * 1000
    if not results:
        output_html = '<div style="padding: 20px; text-align: center;">No matching standards found.</div>'
    else:
        output_html = '<div style="display: flex; flex-direction: column; gap: 16px;">'
        for idx, rec in enumerate(results):
            output_html += f"""
            <div class="result-card">
                <h3 style="margin: 0 0 12px 0; display: flex; align-items: center; gap: 10px;">
                    <span style="background: #2563eb; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.9rem;">#{idx+1}</span>
                    <span style="border-bottom: 2px solid #2563eb;">{rec.get('standard_id', 'N/A')}</span>
                </h3>
                <p><strong>Title:</strong> {rec.get('title', 'N/A')}</p>
                <div style="margin-top: 12px; padding: 12px; background: rgba(0,0,0,0.05); border-left: 4px solid #4f46e5; border-radius: 4px;">
                    <strong style="font-size: 0.8rem; text-transform: uppercase;">AI Rationale</strong><br/>
                    <span style="font-style: italic;">{rec.get('rationale', 'N/A')}</span>
                </div>
            </div>
            """
        output_html += "</div>"
    return output_html, f"⏱️ Query completed in {latency_ms:.0f} ms"

css = """
.result-card { border: 1px solid #ddd; border-radius: 12px; padding: 20px; transition: all 0.3s; }
.result-card:hover { transform: translateY(-5px); border-color: #2563eb; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
"""

with gr.Blocks(css=css, title="CompliQ") as demo:
    gr.HTML("<div style='text-align: center;'><h1>🏛️ CompliQ</h1><p>Find BIS Standards Instantly</p></div>")
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(lines=3, label="Product Description")
        with gr.Column(scale=1):
            category_dropdown = gr.Dropdown(choices=CATEGORIES, value="All", label="Category")
            submit_btn = gr.Button("🔍 Find Standards", variant="primary")
    latency_text = gr.Markdown("⏱️ Latency: -")
    output_html = gr.HTML("Results will appear here...")
    submit_btn.click(fn=predict, inputs=[query_input, category_dropdown], outputs=[output_html, latency_text])

if __name__ == "__main__":
    demo.launch()
