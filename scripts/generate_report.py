import os
import yaml
import pandas as pd
from jinja2 import Template
from fetch_data import fetch_and_calculate

def load_config(path="config/default.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_report(data, template_path="template.md"):
    with open(template_path, "r", encoding="utf-8") as f:
        tmpl = Template(f.read())
    return tmpl.render(**data)

def main():
    config = load_config()
    out_dir = config['output']['directory']
    os.makedirs(out_dir, exist_ok=True)

    for ticker in config['tickers']:
        sym = ticker['symbol']
        print(f"🔄 正在分析 {sym}...")
        try:
            data = fetch_and_calculate(sym, config)
            report_md = render_report(data)
            filename = f"{sym}_{config['output']['date_format']}.md".replace("-", "")
            # 修正檔名格式
            from datetime import datetime
            filename = f"{sym}_{datetime.now().strftime('%Y%m%d')}.md"
            
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_md)
            print(f"✅ 報告已生成: {filepath}")
        except Exception as e:
            print(f"❌ {sym} 分析失敗: {e}")

if __name__ == "__main__":
    main()
