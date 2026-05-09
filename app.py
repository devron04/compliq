import os
import sys
import time
import gradio as gr
from src.pipeline import BISPipeline

# Initialize pipeline
print("Loading pipeline...", file=sys.stderr)
try:
    data_path = os.path.join(os.path.dirname(__file__), 'data') if os.path.exists(os.path.join(os.path.dirname(__file__), 'data')) else os.path.join(os.path.dirname(__file__), '..', 'data')
    pipeline = BISPipeline(data_dir=data_path)
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
        output_html = '<div style="padding: 40px; text-align: center; color: #9ca3af; border: 2px dashed #374151; border-radius: 12px;">Results will appear here...</div>'
    else:
        output_html = '<div style="display: flex; flex-direction: column; gap: 16px;">'
        for idx, rec in enumerate(results):
            output_html += f"""
            <div class="result-card">
                <h3 style="margin: 0 0 12px 0; font-size: 1.2rem; display: flex; align-items: center; gap: 10px; color: #ffffff;">
                    <span style="background: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">#{idx+1}</span>
                    <span style="color: #3b82f6; text-decoration: underline;">{rec.get('standard_id', 'N/A')}</span>
                </h3>
                <p style="margin: 8px 0; font-size: 1rem; color: #e5e7eb;">
                    <strong style="color: #9ca3af;">Title:</strong> {rec.get('title', 'N/A')}
                </p>
                <div style="margin: 12px 0 0 0; padding: 12px; background: #0f172a; border-radius: 6px;">
                    <strong style="color: #3b82f6; font-size: 0.8rem; text-transform: uppercase;">AI Rationale</strong><br/>
                    <span style="font-style: italic; color: #d1d5db; font-size: 0.95rem;">{rec.get('rationale', 'N/A')}</span>
                </div>
                <div style="margin-top: 12px;">
                    <span style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.2);">
                        ✓ Verified in Context
                    </span>
                </div>
            </div>
            """
        output_html += "</div>"
            
    return output_html, f"⏱️ Query completed in {latency_ms:.0f} ms"

css = """
.gradio-container { background-color: #030712 !important; color: white !important; }
.result-card {
    border: 1px solid #1f2937; border-radius: 8px; padding: 20px;
    background: #111827;
}
.section-header { font-size: 1rem; font-weight: 600; color: white; margin: 20px 0 10px 0; }
#find-btn { background: #2563eb !important; border: none !important; }
#find-btn:hover { background: #3b82f6 !important; }
label span { 
    background: #2563eb !important; 
    color: white !important; 
    padding: 2px 8px !important; 
    border-radius: 4px 4px 0 0 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}
.dark .bg-white { background-color: #1f2937 !important; }
"""

with gr.Blocks(title="CompliQ", css=css, theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"), fill_width=True) as demo:
    with gr.Column(elem_id="header"):
        gr.HTML(
            """
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 2.5rem; margin-bottom: 5px; color: #3b82f6; font-weight: bold;">🏛️ CompliQ</h1>
                <p style="font-size: 1rem; color: #9ca3af; margin-bottom: 15px;">From product to standard, instantly.</p>
                <p style="font-size: 1rem; color: #ffffff; max-width: 800px; margin: 0 auto; line-height: 1.5;">
                    Describe your building material below to find the applicable <strong>Bureau of Indian Standards (BIS)</strong> 
                    regulations using our high-speed, hallucination-free AI pipeline.
                </p>
            </div>
            """
        )
    
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(lines=4, placeholder="Manufacturing coarse and fine aggregates from natural sources for concrete.", label="Product Description")
        with gr.Column(scale=1):
            category_dropdown = gr.Dropdown(choices=CATEGORIES, value="All", label="Filter by Category")
            submit_btn = gr.Button("🔍 Find Standards", variant="primary", size="lg", elem_id="find-btn")
            
    latency_text = gr.Markdown("⏱️ Latency: -")
    
    gr.HTML("<div class='section-header'>Recommended Standards</div>")
    output_html = gr.HTML('<div style="padding: 40px; text-align: center; color: #9ca3af; border: 2px dashed #374151; border-radius: 12px;">Results will appear here...</div>')

    gr.HTML("<div class='section-header'>Examples</div>")
    gr.Examples(
        examples=[
            ["I am making ordinary portland cement 53 grade.", "Cement"],
            ["Manufacturing coarse and fine aggregates from natural sources for concrete.", "Aggregates"],
            ["I produce high strength deformed steel bars for concrete reinforcement.", "Steel"]
        ],
        inputs=[query_input, category_dropdown]
    )

    submit_btn.click(fn=predict, inputs=[query_input, category_dropdown], outputs=[output_html, latency_text])

if __name__ == "__main__":
    demo.launch()
