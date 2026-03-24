import os
import re
import json
import markdown

README_FILE = 'index.md'
OUTPUT_FILE = 'index.html'
BASE_DIR = 'chonglang'

def subreddit_index():
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found.")
        return

    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Flowchart and Replace with Placeholder
    flow_match = re.search(r'```mermaid\s+(flowchart.*?)```', content, re.DOTALL)
    mermaid_flow = ""
    node_list = []
    if flow_match:
        mermaid_flow = flow_match.group(1).strip()
        # Find node IDs (e.g., Bagabondo)
        node_list = re.findall(r'^\s*([a-zA-Z0-9_]+)\["', mermaid_flow, re.MULTILINE)
        flow_div = '<div class="scroll-container flow-window"><div id="flow-output"></div></div>'
        content = content.replace(flow_match.group(0), flow_div)

    # 2. Extract Gantt and Replace with Placeholder
    gantt_match = re.search(r'```mermaid\s+(gantt.*?)```', content, re.DOTALL)
    mermaid_gantt = gantt_match.group(1).strip() if gantt_match else ""
    if gantt_match:
        gantt_div = '<div class="scroll-container gantt-window"><div id="gantt-output"></div></div>'
        content = content.replace(gantt_match.group(0), gantt_div)

    html_body = markdown.markdown(content, extensions=['extra', 'nl2br', 'toc'])
    
    safe_flow = json.dumps(mermaid_flow)
    safe_gantt = json.dumps(mermaid_gantt)
    safe_nodes = json.dumps(node_list)

    full_html = fr'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>红迪流浪史 - Archive Index</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown-light.min.css">
    <style>
        body {{ box-sizing: border-box; margin: 0 auto; padding: 30px; background: #fff; }}
        
        /* The "Window" that stays fixed on screen */
        .scroll-container {{
            border: 1px solid #d0d7de;
            border-radius: 6px;
            background: #f6f8fa;
            margin: 20px 0 40px 0;
            overflow: auto; /* Enables the scrollbars */
            position: relative;
        }}

        /* The "Canvas" that holds the actual SVG */
        #flow-output, #gantt-output {{
            padding: 30px;
            box-sizing: border-box;
            display: inline-block; /* Crucial: allows width to expand beyond 100% parent */
        }}

        /* MINIMUM WIDTHS: Adjust these based on your specific graph complexity */
        #flow-output {{ min-width: 1200px; }}
        #gantt-output {{ min-width: 1600px; }}

        /* Ensure the SVG fills its min-width canvas but doesn't shrink smaller */
        #flow-output svg, #gantt-output svg {{
            width: 100% !important;
            height: auto !important;
            display: block;
        }}

        .clickable-link, .activeText, .doneText, .taskText {{ 
            fill: #0366d6 !important; 
            color: #0366d6 !important;
            cursor: pointer !important; 
            text-decoration: underline !important;
            font-weight: bold !important;
        }}

        #flow-output svg rect, #flow-output svg polygon, #flow-output svg path {{
            pointer-events: none !important;
        }}
        
        .nodeLabel, text {{ pointer-events: auto !important; }}
    </style>
</head>
<body class="markdown-body">
    {html_body}

    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

        const flowCode = {safe_flow};
        const ganttCode = {safe_gantt};
        const validNodes = {safe_nodes};

        mermaid.initialize({{ 
            startOnLoad: false, 
            securityLevel: 'loose', 
            theme: 'default',
            /* 'useMaxWidth: false' is better here to respect our CSS min-widths */
            flowchart: {{ useMaxWidth: false, htmlLabels: true }},
            gantt: {{ useMaxWidth: false, leftMargin: 150 }}
        }});

        function processFlowchartLinks() {{
            const labels = document.querySelectorAll('#flow-output .nodeLabel');
            labels.forEach(label => {{
                let lines = label.innerText.split('\n').map(s => s.trim());
                let firstLine = lines[0];
                let subName = firstLine.replace(/^r\//, '');

                if (validNodes.includes(subName)) {{
                    let remainingText = lines.slice(1).join('<br>');
                    label.innerHTML = `<span class="clickable-link">${{firstLine}}</span>` + 
                                     (remainingText ? `<br>${{remainingText}}` : '');
                    
                    label.querySelector('.clickable-link').addEventListener('click', (e) => {{
                        e.stopPropagation();
                        window.open(`./{BASE_DIR}/` + subName + '.html', '_blank');
                    }});
                }}
            }});
        }}

        function processGanttLinks() {{
            const texts = document.querySelectorAll('#gantt-output text');
            texts.forEach(t => {{
                const content = t.textContent.trim();
                if (validNodes.includes(content)) {{
                    t.classList.add('clickable-link');
                    t.addEventListener('click', () => {{
                        window.open(`./{BASE_DIR}/` + content + '.html', '_blank');
                    }});
                }}
            }});
        }}

        if (flowCode) {{
            mermaid.render('flow-svg', flowCode).then(({{svg}}) => {{
                document.getElementById('flow-output').innerHTML = svg;
                setTimeout(processFlowchartLinks, 300);
            }});
        }}

        if (ganttCode) {{
            mermaid.render('gantt-svg', ganttCode).then(({{svg}}) => {{
                document.getElementById('gantt-output').innerHTML = svg;
                setTimeout(processGanttLinks, 300);
            }});
        }}
    </script>
</body>
</html>'''

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Generated Index: Flowchart is capped vertically; both graphs support horizontal scrolling.")
    return node_list

if __name__ == "__main__":
    sub_list = subreddit_index()
