#!/usr/bin/env python3
"""
VUA TOTALITY Evaluation Harness — Compute evaluation metrics.

Custom code-based evaluators for:
1. Manifest Validation Accuracy
2. Attestation Seal Integrity
3. Event Chain Verification
"""

import json
from pathlib import Path
from typing import Dict, Any


class ManifestValidationAccuracyEvaluator:
    """Evaluate manifest validation accuracy."""
    
    def __call__(self, *, passed: bool, expected: bool, **kwargs) -> Dict[str, Any]:
        """
        Score manifest validation accuracy.
        
        Args:
            passed: Whether the system correctly validated/invalidated the manifest
            expected: What the validation result should have been
        
        Returns:
            Dict with accuracy score and reasoning
        """
        accuracy = 1.0 if (passed == expected) else 0.0
        
        reasoning = (
            f"Manifest validation {'passed' if passed else 'failed'} (expected: {'pass' if expected else 'fail'}). "
            f"{'Correct' if accuracy == 1.0 else 'Incorrect'} detection."
        )
        
        return {
            "manifest_validation_accuracy": accuracy,
            "reasoning": reasoning
        }


class AttestationSealIntegrityEvaluator:
    """Evaluate attestation seal integrity."""
    
    def __call__(self, *, seal_valid: bool, expected: bool, **kwargs) -> Dict[str, Any]:
        """
        Score attestation seal integrity.
        
        Args:
            seal_valid: Whether the seal was valid
            expected: Whether the seal should be valid
        
        Returns:
            Dict with integrity score and reasoning
        """
        integrity = 1.0 if (seal_valid == expected) else 0.0
        
        reasoning = (
            f"Attestation seal {'valid' if seal_valid else 'invalid'} (expected: {'valid' if expected else 'invalid'}). "
            f"{'Correct' if integrity == 1.0 else 'Incorrect'} seal integrity detection."
        )
        
        return {
            "attestation_seal_integrity": integrity,
            "reasoning": reasoning
        }


class EventChainVerificationEvaluator:
    """Evaluate event chain verification."""
    
    def __call__(self, *, chain_valid: bool, expected: bool, **kwargs) -> Dict[str, Any]:
        """
        Score event chain verification.
        
        Args:
            chain_valid: Whether the event chain is valid
            expected: Whether the chain should be valid
        
        Returns:
            Dict with verification score and reasoning
        """
        verification = 1.0 if (chain_valid == expected) else 0.0
        
        reasoning = (
            f"Event chain {'valid' if chain_valid else 'invalid'} (expected: {'valid' if expected else 'invalid'}). "
            f"{'Correct' if verification == 1.0 else 'Incorrect'} chain integrity verification."
        )
        
        return {
            "event_chain_verification": verification,
            "reasoning": reasoning
        }


class UnifiedEvaluationHarness:
    """Unified evaluation harness combining all three metrics."""
    
    def __init__(self, responses_path: str = "evaluation/responses.jsonl"):
        self.responses_path = Path(responses_path)
        self.accuracy_evaluator = ManifestValidationAccuracyEvaluator()
        self.integrity_evaluator = AttestationSealIntegrityEvaluator()
        self.verification_evaluator = EventChainVerificationEvaluator()
    
    def load_responses(self) -> list:
        """Load evaluation responses from JSONL."""
        responses = []
        with open(self.responses_path, 'r') as f:
            for line in f:
                if line.strip():
                    responses.append(json.loads(line))
        return responses
    
    def evaluate(self) -> Dict[str, Any]:
        """Execute evaluation across all metrics."""
        responses = self.load_responses()
        
        evaluated = []
        
        for response in responses:
            response_type = response.get('type')
            
            if response_type == 'manifest_validation_accuracy':
                scores = self.accuracy_evaluator(
                    passed=response.get('passed', False),
                    expected=response.get('expected', True)
                )
            elif response_type == 'attestation_seal_integrity':
                scores = self.integrity_evaluator(
                    seal_valid=response.get('seal_valid', False),
                    expected=response.get('expected', True)
                )
            elif response_type == 'event_chain_verification':
                scores = self.verification_evaluator(
                    chain_valid=response.get('chain_valid', False),
                    expected=response.get('expected', True)
                )
            else:
                scores = {}
            
            # Merge response with scores
            evaluated_item = {**response, **scores}
            evaluated.append(evaluated_item)
        
        # Compute aggregate metrics
        aggregate = self._compute_aggregate(evaluated)
        
        return {
            "evaluated_responses": evaluated,
            "aggregate_metrics": aggregate,
            "total_responses": len(evaluated)
        }
    
    def _compute_aggregate(self, evaluated: list) -> Dict[str, Any]:
        """Compute aggregate statistics."""
        total = len(evaluated)
        
        accuracy_scores = [e.get('manifest_validation_accuracy', 0) for e in evaluated if 'manifest_validation_accuracy' in e]
        integrity_scores = [e.get('attestation_seal_integrity', 0) for e in evaluated if 'attestation_seal_integrity' in e]
        verification_scores = [e.get('event_chain_verification', 0) for e in evaluated if 'event_chain_verification' in e]
        
        return {
            "manifest_validation_accuracy": {
                "count": len(accuracy_scores),
                "average": sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
                "min": min(accuracy_scores) if accuracy_scores else 0,
                "max": max(accuracy_scores) if accuracy_scores else 0,
                "pass_rate": sum(1 for s in accuracy_scores if s >= 0.5) / len(accuracy_scores) * 100 if accuracy_scores else 0
            },
            "attestation_seal_integrity": {
                "count": len(integrity_scores),
                "average": sum(integrity_scores) / len(integrity_scores) if integrity_scores else 0,
                "min": min(integrity_scores) if integrity_scores else 0,
                "max": max(integrity_scores) if integrity_scores else 0,
                "pass_rate": sum(1 for s in integrity_scores if s >= 0.5) / len(integrity_scores) * 100 if integrity_scores else 0
            },
            "event_chain_verification": {
                "count": len(verification_scores),
                "average": sum(verification_scores) / len(verification_scores) if verification_scores else 0,
                "min": min(verification_scores) if verification_scores else 0,
                "max": max(verification_scores) if verification_scores else 0,
                "pass_rate": sum(1 for s in verification_scores if s >= 0.5) / len(verification_scores) * 100 if verification_scores else 0
            },
            "overall": {
                "total_evaluated": total,
                "overall_average": (
                    (sum(accuracy_scores) + sum(integrity_scores) + sum(verification_scores)) /
                    (len(accuracy_scores) + len(integrity_scores) + len(verification_scores))
                ) if (accuracy_scores + integrity_scores + verification_scores) else 0
            }
        }


def main():
    """Run the unified evaluation harness."""
    print("\n" + "="*80)
    print("VUA TOTALITY EVALUATION HARNESS")
    print("="*80 + "\n")
    
    harness = UnifiedEvaluationHarness()
    results = harness.evaluate()
    
    # Print aggregate metrics
    print("AGGREGATE METRICS")
    print("-"*80)
    aggregate = results['aggregate_metrics']
    
    for metric_name, metric_data in aggregate.items():
        if metric_name == 'overall':
            print(f"\nOverall Performance:")
            print(f"  Total Evaluated: {metric_data['total_evaluated']}")
            print(f"  Overall Average Score: {metric_data['overall_average']:.2%}")
        else:
            print(f"\n{metric_name.replace('_', ' ').title()}:")
            print(f"  Count: {metric_data['count']}")
            print(f"  Average Score: {metric_data['average']:.2%}")
            print(f"  Pass Rate: {metric_data['pass_rate']:.1f}%")
    
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80 + "\n")
    
    for i, item in enumerate(results['evaluated_responses'], 1):
        print(f"[{i}] Query {item.get('query_id')} ({item.get('type')})")
        for key in ['manifest_validation_accuracy', 'attestation_seal_integrity', 'event_chain_verification']:
            if key in item:
                print(f"  {key}: {item[key]:.2%}")
        if 'reasoning' in item:
            print(f"  Reasoning: {item['reasoning']}")
        print()
    
    # Save detailed results
    output_path = Path("evaluation/evaluation_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")


if __name__ == '__main__':
    main()
