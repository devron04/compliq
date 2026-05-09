import os
import sys
import time
import gradio as gr
from src.pipeline import BISPipeline

# Initialize pipeline
print("Loading pipeline...", file=sys.stderr)
try:
    # Handle path for both root and src execution
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
        output_html = '<div style="padding: 40px; text-align: center; color: var(--body-text-color-subdued); border: 2px dashed var(--border-color-primary); border-radius: 12px;">No matching standards found in the context.</div>'
    else:
        output_html = '<div style="display: flex; flex-direction: column; gap: 16px;">'
        for idx, rec in enumerate(results):
            output_html += f"""
            <div class="result-card">
                <h3 style="margin-top: 0; margin-bottom: 12px; font-size: 1.25rem; display: flex; align-items: center; gap: 10px; color: var(--body-text-color);">
                    <span style="background: var(--primary-500); color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.9rem; font-weight: bold;">#{idx+1}</span>
                    <span style="border-bottom: 2px solid var(--primary-500); padding-bottom: 2px;">{rec.get('standard_id', 'N/A')}</span>
                </h3>
                <p style="margin: 8px 0; font-size: 1.05rem; color: var(--body-text-color);">
                    <strong style="color: var(--body-text-color-subdued);">Title:</strong> {rec.get('title', 'N/A')}
                </p>
                <div style="margin: 12px 0 0 0; padding: 12px; background: var(--background-fill-primary); border-left: 4px solid var(--secondary-500); border-radius: 4px; color: var(--body-text-color);">
                    <strong style="color: var(--body-text-color-subdued); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">AI Rationale</strong><br/>
                    <span style="font-style: italic;">{rec.get('rationale', 'N/A')}</span>
                </div>
                <div style="margin-top: 12px; display: flex; gap: 8px;">
                    <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 4px;">
                        <span style="font-size: 1rem;">✓</span> Verified in Context
                    </span>
                </div>
            </div>
            """
        output_html += "</div>"
            
    latency_str = f"⏱️ **Query completed in {latency_ms:.0f} ms**"
    return output_html, latency_str

custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="*neutral_50",
    body_background_fill_dark="*neutral_950",
    block_background_fill="*neutral_100",
    block_background_fill_dark="*neutral_900",
    block_border_width="1px",
)

css = """
#header { text-align: center; margin-bottom: 30px; }
.result-card {
    border: 1px solid var(--border-color-primary); border-radius: 12px; padding: 20px;
    background: var(--background-fill-secondary); transition: all 0.3s ease;
}
.result-card:hover { border-color: var(--primary-500); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
#find-btn { background: var(--primary-600); }
.section-header { font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
"""

with gr.Blocks(title="CompliQ - BIS Standards Finder", css=css, theme=custom_theme) as demo:
    with gr.Column(elem_id="header"):
        gr.Markdown(
            """
            <div style="text-align: center;">
                <h1 style="font-size: 2.5rem; margin-bottom: 10px;">🏛️ CompliQ</h1>
                <p style="font-size: 1.1rem; color: var(--body-text-color-subdued);">BIS Standards Recommendation Engine</p>
            </div>
            """
        )
    
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(lines=4, placeholder="Describe your product or material...", label="Product Description")
        with gr.Column(scale=1):
            category_dropdown = gr.Dropdown(choices=CATEGORIES, value="All", label="Filter by Category")
            submit_btn = gr.Button("🔍 Find Standards", variant="primary", size="lg", elem_id="find-btn")
            
    latency_text = gr.Markdown("⏱️ Latency: -")
    
    gr.Markdown("### 📋 Recommended Standards")
    output_html = gr.HTML('<div style="padding: 40px; text-align: center; color: var(--body-text-color-subdued); border: 2px dashed var(--border-color-primary); border-radius: 12px;">Results will appear here...</div>')

    gr.Markdown("### 💡 Examples")
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
