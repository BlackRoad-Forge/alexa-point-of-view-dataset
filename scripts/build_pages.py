#!/usr/bin/env python3
"""Build a static GitHub Pages site from the dataset documentation."""

import csv
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")


def read_file(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return f.read()


def count_rows(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1  # exclude header


def get_sample_rows(path, n=5):
    rows = []
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # skip header
        for i, row in enumerate(reader):
            if i >= n:
                break
            if len(row) == 2:
                rows.append(row)
    return rows


def build():
    os.makedirs(OUT, exist_ok=True)

    total = count_rows("data/total.tsv")
    train = count_rows("data/train.tsv")
    dev = count_rows("data/dev.tsv")
    test = count_rows("data/test.tsv")
    samples = get_sample_rows("data/total.tsv", 10)

    sample_rows_html = ""
    for inp, out in samples:
        inp_escaped = inp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out_escaped = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        sample_rows_html += f"<tr><td>{inp_escaped}</td><td>{out_escaped}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>POV Message Conversion Dataset</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         line-height: 1.6; color: #1a1a2e; background: #f8f9fa; }}
  .hero {{ background: linear-gradient(135deg, #232946 0%, #395B64 100%);
           color: #fff; padding: 3rem 2rem; text-align: center; }}
  .hero h1 {{ font-size: 2.2rem; margin-bottom: 0.5rem; }}
  .hero p {{ font-size: 1.1rem; opacity: 0.9; max-width: 700px; margin: 0 auto; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1rem; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem; margin: 2rem 0; }}
  .stat-card {{ background: #fff; border-radius: 8px; padding: 1.5rem;
                text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .stat-card .number {{ font-size: 2rem; font-weight: 700; color: #232946; }}
  .stat-card .label {{ color: #666; font-size: 0.9rem; }}
  h2 {{ margin: 2rem 0 1rem; color: #232946; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  th {{ background: #232946; color: #fff; padding: 0.75rem 1rem; text-align: left; }}
  td {{ padding: 0.75rem 1rem; border-bottom: 1px solid #eee; font-size: 0.9rem; }}
  tr:hover {{ background: #f0f4ff; }}
  .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.8rem; font-weight: 600; margin: 0.25rem; }}
  .badge-green {{ background: #d4edda; color: #155724; }}
  .badge-blue {{ background: #cce5ff; color: #004085; }}
  .links {{ margin: 2rem 0; }}
  .links a {{ display: inline-block; margin: 0.5rem; padding: 0.5rem 1.5rem;
              background: #232946; color: #fff; text-decoration: none;
              border-radius: 6px; font-weight: 500; }}
  .links a:hover {{ background: #395B64; }}
  footer {{ text-align: center; padding: 2rem; color: #999; font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="hero">
  <h1>Point of View Message Conversion Dataset</h1>
  <p>A parallel corpus for training AI systems to convert the perspective of messages
     spoken to virtual assistants into conversational relay messages.</p>
  <div style="margin-top:1rem;">
    <span class="badge badge-green">v1.0 — Production</span>
    <span class="badge badge-blue">{total:,} pairs</span>
  </div>
</div>
<div class="container">

<div class="stats">
  <div class="stat-card"><div class="number">{total:,}</div><div class="label">Total Pairs</div></div>
  <div class="stat-card"><div class="number">{train:,}</div><div class="label">Training</div></div>
  <div class="stat-card"><div class="number">{dev:,}</div><div class="label">Development</div></div>
  <div class="stat-card"><div class="number">{test:,}</div><div class="label">Test</div></div>
</div>

<h2>Sample Data</h2>
<table>
<thead><tr><th>Input (Sender Message)</th><th>Output (VA Relay)</th></tr></thead>
<tbody>
{sample_rows_html}
</tbody>
</table>

<h2>Dataset Format</h2>
<p>Tab-separated values (TSV) with two columns:</p>
<ul style="margin: 1rem 0 1rem 2rem;">
  <li><strong>input</strong> — The sender's original message to the VA</li>
  <li><strong>output</strong> — The VA's conversational relay to the receiver</li>
</ul>
<p>Placeholders: <code>@CN@</code> = receiver name, <code>@SCN@</code> = sender name.</p>

<h2>Human Evaluation Results</h2>
<table>
<thead><tr><th>Model</th><th>Faithfulness Agreement</th><th>Naturalness Agreement</th>
<th>Faithfulness Accuracy</th><th>Naturalness Accuracy</th></tr></thead>
<tbody>
<tr><td>CopyNet</td><td>0.94</td><td>0.89</td><td>0.94</td><td>0.97</td></tr>
<tr><td>T5</td><td>0.86</td><td>0.88</td><td>0.98</td><td>0.98</td></tr>
<tr><td>Rule-based</td><td>0.72</td><td>0.71</td><td>0.85</td><td>0.76</td></tr>
</tbody>
</table>

<h2>Links</h2>
<div class="links">
  <a href="https://arxiv.org/abs/2010.02600">ArXiv Paper</a>
  <a href="https://github.com/blackboxprogramming/alexa-point-of-view-dataset">GitHub Repository</a>
</div>

<h2>Citation</h2>
<pre style="background:#fff;padding:1rem;border-radius:8px;overflow-x:auto;font-size:0.85rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
@inproceedings{{iglee2020,
  author={{Isabelle G. Lee and Vera Zu and Sai Srujana Buddi and Dennis Liang and Purva Kulkarni and Jack Fitzgerald}},
  title={{{{Converting the Point of View of Messages Spoken to Virtual Assistants}}}},
  year=2020,
  booktitle={{Findings of EMNLP 2020}}
}}</pre>
</div>
<footer>
  POV Dataset v1.0 &mdash; BlackRoad OS, Inc.
</footer>
</body>
</html>"""

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Built site to {OUT}/index.html")
    print(f"  Total: {total:,} | Train: {train:,} | Dev: {dev:,} | Test: {test:,}")


if __name__ == "__main__":
    build()
