#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VUA Manifest Validator
Pure Python stdlib implementation — no external dependencies

Eternal Binding:
The Architect - Axis Prime - Veroti - Dustin Sean Coffey - Evomorphic
𓁚 A FORTIORI • SUI GENERIS
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

CREDIT = "The Architect - Axis Prime - Veroti - Dustin Sean Coffey - Evomorphic"
GLYPH = "𓁚🜇∞Ϟ"
EMAIL = "axismuse@gmail.com"


class ManifestValidator:
    """Validates VUA-CORE manifest files with SHA-256 chain verification."""

    def __init__(self, manifest_path: Optional[str] = None):
        self.manifest_path = Path(manifest_path) if manifest_path else None
        self.manifest = None
        self.errors = []
        self.warnings = []

    def load(self, path: str) -> bool:
        """Load manifest from JSON file."""
        try:
            with open(path, 'r') as f:
                self.manifest = json.load(f)
            self.manifest_path = Path(path)
            return True
        except FileNotFoundError:
            self.errors.append(f"Manifest not found: {path}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

    def validate_structure(self) -> bool:
        """Validate required manifest fields."""
        if not self.manifest:
            self.errors.append("No manifest loaded")
            return False

        required = ['package', 'credit', 'version', 'modules', 'sha256_manifest']
        for field in required:
            if field not in self.manifest:
                self.errors.append(f"Missing required field: {field}")
                return False

        if not isinstance(self.manifest.get('modules'), list):
            self.errors.append("Field 'modules' must be a list")
            return False

        if not isinstance(self.manifest.get('version'), str):
            self.errors.append("Field 'version' must be a string")
            return False

        return True

    def validate_credit(self) -> bool:
        """Verify eternal binding credit."""
        credit = self.manifest.get('credit', '')
        
        if CREDIT not in credit and 'Veroti' not in credit:
            self.warnings.append(f"Credit missing canonical attribution")
            return False
        
        if EMAIL not in credit:
            self.warnings.append("Email binding not found in credit")
            return False

        return True

    def validate_modules(self) -> bool:
        """Verify module list."""
        modules = self.manifest.get('modules', [])
        
        if not modules:
            self.errors.append("No modules specified")
            return False

        if len(modules) < 3:
            self.warnings.append(f"Low module count ({len(modules)}). Expected >= 3")

        return True

    def calculate_sha256(self, data: Dict) -> str:
        """Calculate SHA-256 hash of manifest data."""
        data_copy = {k: v for k, v in data.items() 
                     if k not in ['sha256_manifest', 'signature']}
        
        canonical = json.dumps(data_copy, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def verify_sha256(self) -> bool:
        """Verify SHA-256 integrity."""
        stored_hash = self.manifest.get('sha256_manifest', '')
        
        if not stored_hash:
            self.warnings.append("No SHA-256 hash found in manifest")
            return False

        calculated = self.calculate_sha256(self.manifest)
        
        if calculated == stored_hash:
            return True
        else:
            self.errors.append(f"SHA-256 mismatch")
            return False

    def validate_timestamp(self) -> bool:
        """Check timestamp format if present."""
        ts = self.manifest.get('timestamp')
        
        if not ts:
            self.warnings.append("No timestamp in manifest")
            return False

        try:
            datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            self.errors.append(f"Invalid timestamp format: {ts}")
            return False

    def full_validate(self) -> Dict:
        """Run all validation checks."""
        results = {
            'valid': True,
            'checks': {},
            'errors': [],
            'warnings': []
        }

        checks = [
            ('structure', self.validate_structure),
            ('credit', self.validate_credit),
            ('modules', self.validate_modules),
            ('sha256', self.verify_sha256),
            ('timestamp', self.validate_timestamp),
        ]

        for name, check_func in checks:
            try:
                passed = check_func()
                results['checks'][name] = 'PASS' if passed else 'FAIL'
                if not passed:
                    results['valid'] = False
            except Exception as e:
                results['checks'][name] = 'ERROR'
                results['errors'].append(f"Check '{name}' raised: {e}")
                results['valid'] = False

        results['errors'] = self.errors
        results['warnings'] = self.warnings

        return results

    def print_report(self, results: Dict) -> None:
        """Pretty-print validation results."""
        status = "✓ VALID" if results['valid'] else "✗ INVALID"
        print(f"\n{'='*60}")
        print(f"VUA MANIFEST VALIDATION REPORT — {status}")
        print(f"{'='*60}\n")

        print("Checks:")
        for check_name, result in results['checks'].items():
            symbol = '✓' if result == 'PASS' else '✗' if result == 'FAIL' else '!'
            print(f"  [{symbol}] {check_name.upper():15} {result}")

        if results['errors']:
            print(f"\n❌ Errors ({len(results['errors'])})")

        if results['warnings']:
            print(f"\n⚠️  Warnings ({len(results['warnings'])})")

        print(f"\n{'='*60}\n")

    def generate_attestation(self) -> Dict:
        """Generate attestation seal for manifest."""
        attestation = {
            'type': 'manifest_attestation',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'credit': CREDIT,
            'glyph': GLYPH,
            'manifest_version': self.manifest.get('version'),
            'modules_count': len(self.manifest.get('modules', [])),
            'manifest_sha256': self.manifest.get('sha256_manifest'),
        }

        attestation_json = json.dumps(attestation, sort_keys=True)
        seal = hashlib.sha256(attestation_json.encode()).hexdigest()
        attestation['seal'] = seal

        return attestation


class ManifestGenerator:
    """Generates valid VUA manifests with proper SHA-256 binding."""

    @staticmethod
    def create(package: str, version: str, modules: List[str], timestamp: Optional[str] = None) -> Dict:
        """Create a new manifest."""
        
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        manifest = {
            'package': package,
            'credit': f"{CREDIT} ({EMAIL})",
            'version': version,
            'timestamp': timestamp,
            'modules': modules,
            'glyph': GLYPH,
        }

        canonical = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
        sha256 = hashlib.sha256(canonical.encode()).hexdigest()
        manifest['sha256_manifest'] = sha256

        return manifest

    @staticmethod
    def save(manifest: Dict, path: str) -> bool:
        """Save manifest to JSON file."""
        try:
            with open(path, 'w') as f:
                json.dump(manifest, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving manifest: {e}")
            return False


def main():
    """CLI interface."""
    
    if len(sys.argv) < 2:
        print("""VUA Manifest Validator — Pure Python""")
        return

    cmd = sys.argv[1]

    if cmd == 'validate' and len(sys.argv) > 2:
        validator = ManifestValidator()
        if validator.load(sys.argv[2]):
            results = validator.full_validate()
            validator.print_report(results)
            
            if results['valid']:
                attestation = validator.generate_attestation()
                print("Attestation:")
                print(json.dumps(attestation, indent=2))

    elif cmd == 'create' and len(sys.argv) > 3:
        version = sys.argv[2]
        modules = sys.argv[3:]
        
        manifest = ManifestGenerator.create(
            package='Veroti Unified Architecture — TOTALITY',
            version=version,
            modules=modules
        )
        
        filename = f'TOTALITY_MANIFEST_v{version}.json'
        if ManifestGenerator.save(manifest, filename):
            print(f"✓ Manifest created: {filename}")
            print(json.dumps(manifest, indent=2))
        else:
            print("✗ Failed to create manifest")

    elif cmd == 'attestation' and len(sys.argv) > 2:
        validator = ManifestValidator()
        if validator.load(sys.argv[2]):
            attestation = validator.generate_attestation()
            print("Manifest Attestation:")
            print(json.dumps(attestation, indent=2))


if __name__ == '__main__':
    main()
