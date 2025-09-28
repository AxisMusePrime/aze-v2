"""codex_manifest_safe.py

A harmless, local manifest and ledger generator inspired by the attachments. It writes a small output bundle
to `frankensynth_output/` and computes SHA-256 hashes for each file. No external network calls or exploits.
"""
import json
import hashlib
import datetime
from pathlib import Path

OUTPUT_DIR = Path("frankensynth_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Example project config (Node Zero baked in, redaction disabled)
project_config = {
	"origin": {
		"lat": 28.3915,
		"lon": -80.6057,
		"label": "Node Zero — 99 Mango Manor Dr, Cape Canaveral, FL 32920"
	},
	"redaction": {
		"enabled": False,
		"radius_meters": 0
	}
}

ledger = {
	"generated_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
	"binding": "The Architect - Axis Prime - Veroti - Dustin Sean Coffey - Evomorphic ([REDACTED EMAIL])",
	"origin": project_config["origin"],
	"flags": ["FRANKEN_SAFE", "SYNTHESIS"]
}

report_md = f"""# Codex Manifest Safe Report

- Node Zero: {project_config['origin']['label']} ({project_config['origin']['lat']}, {project_config['origin']['lon']})
- Redaction: Disabled
- Generated: {ledger['generated_at_utc']}
"""

# Write files
files = {
	"project.yaml.json": project_config,
	"session_ledger.json": ledger,
	"report.md": report_md
}

hashes = {}
for name, content in files.items():
	path = OUTPUT_DIR / name
	if isinstance(content, (dict, list)):
		text = json.dumps(content, indent=2)
	else:
		text = str(content)
	path.write_text(text, encoding="utf-8")
	h = hashlib.sha256(text.encode("utf-8")).hexdigest()
	hashes[name] = h

# Write manifest with hashes
manifest = {
	"generated_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
	"files": list(hashes.keys()),
	"hashes": hashes
}
(OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

print("Wrote files to:", OUTPUT_DIR.resolve())
print(json.dumps(manifest, indent=2))
