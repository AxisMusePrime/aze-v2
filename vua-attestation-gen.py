#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VUA Attestation Generator
Cryptographic binding & sealing for TOTALITY systems

Eternal Binding:
The Architect - Axis Prime - Veroti - Dustin Sean Coffey - Evomorphic
𓁚 A FORTIORI • SUI GENERIS
"""

import json
import hashlib
import time
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional


CREDIT = "The Architect - Axis Prime - Veroti - Dustin Sean Coffey - Evomorphic"
EMAIL = "axismuse@gmail.com"
GLYPH = "𓁚🜇∞Ϟ"


class AttestationGenerator:
    """Generates cryptographic attestations for VUA systems with eternal binding."""

    def __init__(self, name: str = "TOTALITY"):
        self.name = name
        self.attestations = []

    def seal_state(self, state_data: Dict) -> Dict:
        """Create an attestation seal for a state object."""
        entry = {
            'type': 'state_seal',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'credit': CREDIT,
            'email': EMAIL,
            'glyph': GLYPH,
            'data_hash': self._hash_object(state_data),
            'system': self.name,
        }

        entry['seal'] = self._generate_seal(entry)
        entry['checksum'] = self._checksum(entry['seal'])

        self.attestations.append(entry)
        return entry

    def seal_manifest(self, manifest_path: str) -> Dict:
        """Seal a manifest file with cryptographic binding."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except FileNotFoundError:
            return {'error': f'Manifest not found: {manifest_path}'}

        entry = {
            'type': 'manifest_seal',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'credit': CREDIT,
            'email': EMAIL,
            'glyph': GLYPH,
            'manifest_file': manifest_path,
            'manifest_sha256': manifest.get('sha256_manifest', 'N/A'),
            'manifest_version': manifest.get('version', 'N/A'),
            'modules_count': len(manifest.get('modules', [])),
        }

        entry['seal'] = self._generate_seal(entry)
        entry['checksum'] = self._checksum(entry['seal'])

        self.attestations.append(entry)
        return entry

    def seal_execution(self, command: str, result: Dict) -> Dict:
        """Seal an execution result with eternal binding."""
        entry = {
            'type': 'execution_seal',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'credit': CREDIT,
            'email': EMAIL,
            'glyph': GLYPH,
            'command': command,
            'result_hash': self._hash_object(result),
            'system': self.name,
        }

        entry['seal'] = self._generate_seal(entry)
        entry['checksum'] = self._checksum(entry['seal'])

        self.attestations.append(entry)
        return entry

    def seal_build(self, build_info: Dict) -> Dict:
        """Seal a build manifest with eternal binding."""
        entry = {
            'type': 'build_seal',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'credit': CREDIT,
            'email': EMAIL,
            'glyph': GLYPH,
            'build_hash': self._hash_object(build_info),
            'system': self.name,
            'build_info': build_info,
        }

        entry['seal'] = self._generate_seal(entry)
        entry['checksum'] = self._checksum(entry['seal'])

        self.attestations.append(entry)
        return entry

    def create_chain(self) -> Dict:
        """Create a chain of attestations (like a blockchain)."""
        if not self.attestations:
            return {'error': 'No attestations to chain'}

        chain = {
            'type': 'attestation_chain',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'credit': CREDIT,
            'email': EMAIL,
            'glyph': GLYPH,
            'system': self.name,
            'count': len(self.attestations),
            'attestations': self.attestations,
        }

        chain['chain_hash'] = self._create_chain_hash(self.attestations)

        return chain

    def verify_seal(self, sealed_object: Dict) -> bool:
        """Verify a seal's integrity."""
        if 'seal' not in sealed_object or 'checksum' not in sealed_object:
            return False

        stored_seal = sealed_object['seal']
        stored_checksum = sealed_object['checksum']

        verify_data = {k: v for k, v in sealed_object.items() 
                      if k not in ['seal', 'checksum']}
        
        recalc_seal = self._generate_seal(verify_data)
        recalc_checksum = self._checksum(recalc_seal)

        return recalc_seal == stored_seal and recalc_checksum == stored_checksum

    # Internal helpers

    def _hash_object(self, obj: Dict) -> str:
        """Hash an object with SHA-256."""
        canonical = json.dumps(obj, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _generate_seal(self, data: Dict) -> str:
        """Generate a cryptographic seal."""
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        seal_input = canonical + CREDIT + str(int(time.time()))
        return hashlib.sha256(seal_input.encode()).hexdigest()

    def _checksum(self, seal: str) -> str:
        """Generate a checksum of a seal."""
        return hashlib.sha256(seal.encode()).hexdigest()[:16]

    def _create_chain_hash(self, attestations: list) -> str:
        """Create a chain hash from attestations."""
        chain_str = ''.join([a['seal'] for a in attestations])
        return hashlib.sha256(chain_str.encode()).hexdigest()


class AttestationVault:
    """Stores and manages attestations in JSON format."""

    def __init__(self, vault_path: str = "attestations.json"):
        self.vault_path = Path(vault_path)
        self.vault = self._load_vault()

    def _load_vault(self) -> Dict:
        """Load existing vault or create new one."""
        if self.vault_path.exists():
            try:
                with open(self.vault_path, 'r') as f:
                    return json.load(f)
            except:
                return {'attestations': []}
        return {'attestations': []}

    def add_attestation(self, attestation: Dict) -> bool:
        """Add attestation to vault."""
        if 'attestations' not in self.vault:
            self.vault['attestations'] = []

        self.vault['attestations'].append(attestation)
        self.vault['last_updated'] = datetime.now(timezone.utc).isoformat()

        return self.save()

    def add_chain(self, chain: Dict) -> bool:
        """Add attestation chain to vault."""
        if 'chains' not in self.vault:
            self.vault['chains'] = []

        self.vault['chains'].append(chain)
        self.vault['last_updated'] = datetime.now(timezone.utc).isoformat()

        return self.save()

    def save(self) -> bool:
        """Save vault to disk."""
        try:
            with open(self.vault_path, 'w') as f:
                json.dump(self.vault, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving vault: {e}")
            return False

    def get_attestations(self) -> list:
        """Get all attestations."""
        return self.vault.get('attestations', [])

    def get_chains(self) -> list:
        """Get all chains."""
        return self.vault.get('chains', [])

    def count(self) -> Dict:
        """Get counts of attestations and chains."""
        return {
            'attestations': len(self.vault.get('attestations', [])),
            'chains': len(self.vault.get('chains', [])),
        }


def main():
    """CLI interface."""
    
    if len(sys.argv) < 2:
        print("VUA Attestation Generator — Eternal Binding Sealer")
        return

    cmd = sys.argv[1]
    gen = AttestationGenerator()

    if cmd == 'seal' and len(sys.argv) > 2:
        seal_type = sys.argv[2]

        if seal_type == 'state' and len(sys.argv) > 3:
            try:
                state_data = json.loads(sys.argv[3])
                attestation = gen.seal_state(state_data)
                print("State Sealed:")
                print(json.dumps(attestation, indent=2))
            except json.JSONDecodeError:
                print("Invalid JSON for state data")

        elif seal_type == 'manifest' and len(sys.argv) > 3:
            attestation = gen.seal_manifest(sys.argv[3])
            print("Manifest Sealed:")
            print(json.dumps(attestation, indent=2))

        elif seal_type == 'execution' and len(sys.argv) > 4:
            command = sys.argv[3]
            try:
                result = json.loads(sys.argv[4])
                attestation = gen.seal_execution(command, result)
                print("Execution Sealed:")
                print(json.dumps(attestation, indent=2))
            except json.JSONDecodeError:
                print("Invalid JSON for result")

        elif seal_type == 'build' and len(sys.argv) > 3:
            try:
                build_info = json.loads(sys.argv[3])
                attestation = gen.seal_build(build_info)
                print("Build Sealed:")
                print(json.dumps(attestation, indent=2))
            except json.JSONDecodeError:
                print("Invalid JSON for build info")

    elif cmd == 'chain':
        attestations = []
        for filepath in sys.argv[2:]:
            try:
                with open(filepath, 'r') as f:
                    attestations.append(json.load(f))
            except:
                print(f"Could not load: {filepath}")

        if attestations:
            gen.attestations = attestations
            chain = gen.create_chain()
            print("Attestation Chain Created:")
            print(json.dumps(chain, indent=2))

    elif cmd == 'verify' and len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'r') as f:
                sealed = json.load(f)
            
            if gen.verify_seal(sealed):
                print("✓ Attestation verified — Seal integrity confirmed")
            else:
                print("✗ Attestation invalid — Seal mismatch")
        except:
            print(f"Could not load attestation file: {sys.argv[2]}")

    elif cmd == 'vault':
        vault = AttestationVault()

        if len(sys.argv) > 2:
            if sys.argv[2] == 'add' and len(sys.argv) > 3:
                try:
                    with open(sys.argv[3], 'r') as f:
                        attestation = json.load(f)
                    if vault.add_attestation(attestation):
                        print(f"✓ Added to vault: {sys.argv[3]}")
                    else:
                        print("✗ Failed to add to vault")
                except:
                    print(f"Could not load file: {sys.argv[3]}")

            elif sys.argv[2] == 'list':
                attestations = vault.get_attestations()
                print(f"Attestations in vault ({len(attestations)}):")
                for att in attestations:
                    print(f"  • {att['type']} @ {att['timestamp']}")

            elif sys.argv[2] == 'count':
                counts = vault.count()
                print(f"Vault counts:")
                print(f"  Attestations: {counts['attestations']}")
                print(f"  Chains: {counts['chains']}")


if __name__ == '__main__':
    main()
