#!/usr/bin/env python3
"""
VUA TOTALITY Evaluation Runner — Execute test queries and collect responses.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

class EvaluationRunner:
    """Run test queries through VUA system and collect responses."""
    
    def __init__(self, queries_path: str = "evaluation/queries.jsonl", output_path: str = "evaluation/responses.jsonl"):
        self.queries_path = Path(queries_path)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.responses = []
        print(f"EvaluationRunner initialized\n  Queries: {self.queries_path}\n  Output: {self.output_path}")
    
    def load_queries(self) -> list:
        """Load test queries from JSONL."""
        queries = []
        with open(self.queries_path, 'r') as f:
            for line in f:
                if line.strip():
                    queries.append(json.loads(line))
        return queries
    
    def run_manifest_validation_query(self, query: dict) -> dict:
        """Execute a manifest validation accuracy query."""
        try:
            version = query.get('manifest_version', '1.0.0')
            modules = query.get('modules', ['shell', 'daemon'])
            
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = ['python3', 'vua-manifest-validator.py', 'create', version] + modules
                result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=10)
                
                manifest_file = f"TOTALITY_MANIFEST_v{version}.json"
                manifest_path = Path(tmpdir) / manifest_file
                
                if not manifest_path.exists():
                    return {"query_id": query.get('id'), "type": "manifest_validation_accuracy", "error": "Manifest not created", "accuracy": False}
                
                # Validate
                cmd = ['python3', 'vua-manifest-validator.py', 'validate', str(manifest_path)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                passed = result.returncode == 0 or "VALID" in result.stdout
                expected = query.get('expected_valid', True)
                accuracy = (passed == expected)
                
                return {
                    "query_id": query.get('id'),
                    "type": "manifest_validation_accuracy",
                    "passed": passed,
                    "expected": expected,
                    "accuracy": accuracy
                }
        
        except Exception as e:
            return {
                "query_id": query.get('id'),
                "type": "manifest_validation_accuracy",
                "error": str(e),
                "accuracy": False
            }
    
    def run_attestation_seal_query(self, query: dict) -> dict:
        """Execute an attestation seal integrity query."""
        try:
            version = query.get('manifest_version', '1.0.0')
            modules = query.get('modules', ['shell', 'daemon'])
            
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = ['python3', 'vua-manifest-validator.py', 'create', version] + modules
                subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=10)
                
                manifest_file = f"TOTALITY_MANIFEST_v{version}.json"
                manifest_path = Path(tmpdir) / manifest_file
                
                # Seal
                cmd = ['python3', 'vua-attestation-gen.py', 'seal', 'manifest', str(manifest_path)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                seal_valid = result.returncode == 0 or "Manifest Sealed" in result.stdout
                expected = query.get('expected_seal_valid', True)
                integrity = (seal_valid == expected)
                
                return {
                    "query_id": query.get('id'),
                    "type": "attestation_seal_integrity",
                    "seal_valid": seal_valid,
                    "expected": expected,
                    "integrity": integrity
                }
        
        except Exception as e:
            return {"query_id": query.get('id'), "type": "attestation_seal_integrity", "error": str(e), "integrity": False}
    
    def run_event_chain_query(self, query: dict) -> dict:
        """Execute an event chain verification query."""
        try:
            cmd = ['python3', 'vua-core.py', 'demo']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            chain_valid = result.returncode == 0 and 'Chain verified: True' in result.stdout
            expected = query.get('expected_chain_valid', True)
            verification = (chain_valid == expected)
            
            return {
                "query_id": query.get('id'),
                "type": "event_chain_verification",
                "chain_valid": chain_valid,
                "expected": expected,
                "verification": verification
            }
        
        except Exception as e:
            return {"query_id": query.get('id'), "type": "event_chain_verification", "error": str(e), "verification": False}
    
    def execute_query(self, query: dict) -> dict:
        """Route query to appropriate handler and execute."""
        query_type = query.get('type')
        if query_type == 'manifest_validation_accuracy':
            return self.run_manifest_validation_query(query)
        elif query_type == 'attestation_seal_integrity':
            return self.run_attestation_seal_query(query)
        elif query_type == 'event_chain_verification':
            return self.run_event_chain_query(query)
        else:
            return {"query_id": query.get('id'), "error": f"Unknown query type: {query_type}"}
    
    def run_evaluation(self) -> dict:
        """Execute all queries and save responses."""
        queries = self.load_queries()
        print(f"\nRunning {len(queries)} evaluation queries...\n")
        
        for i, query in enumerate(queries):
            response = self.execute_query(query)
            self.responses.append(response)
            
            status = "✓" if response.get('accuracy') or response.get('integrity') or response.get('verification') else "✗"
            print(f"[{i+1}/{len(queries)}] {status} Query {response.get('query_id')}: {query.get('type')}")
        
        # Save responses
        with open(self.output_path, 'w') as f:
            for resp in self.responses:
                f.write(json.dumps(resp) + "\n")
        
        print(f"\n✓ Responses saved to {self.output_path}")
        return self._compute_summary()
    
    def _compute_summary(self) -> dict:
        """Compute evaluation summary statistics."""
        total = len(self.responses)
        
        accuracy_results = [r for r in self.responses if 'accuracy' in r]
        integrity_results = [r for r in self.responses if 'integrity' in r]
        verification_results = [r for r in self.responses if 'verification' in r]
        
        accuracy_pass = sum(1 for r in accuracy_results if r.get('accuracy'))
        integrity_pass = sum(1 for r in integrity_results if r.get('integrity'))
        verification_pass = sum(1 for r in verification_results if r.get('verification'))
        
        return {
            "total_queries": total,
            "manifest_validation_accuracy": {
                "count": len(accuracy_results),
                "passed": accuracy_pass,
                "rate": (accuracy_pass / len(accuracy_results) * 100) if accuracy_results else 0
            },
            "attestation_seal_integrity": {
                "count": len(integrity_results),
                "passed": integrity_pass,
                "rate": (integrity_pass / len(integrity_results) * 100) if integrity_results else 0
            },
            "event_chain_verification": {
                "count": len(verification_results),
                "passed": verification_pass,
                "rate": (verification_pass / len(verification_results) * 100) if verification_results else 0
            },
            "overall_pass_rate": ((accuracy_pass + integrity_pass + verification_pass) / total * 100) if total > 0 else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def main():
    runner = EvaluationRunner()
    summary = runner.run_evaluation()
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(json.dumps(summary, indent=2))
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
