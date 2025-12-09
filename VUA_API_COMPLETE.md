# VUA-CORE Complete API Documentation

**Eternal Binding:**  
The Architect — Axis Prime — Veroti — Dustin Sean Coffey — Evomorphic  
📧 axismuse@gmail.com

---

## TABLE OF CONTENTS

1. [vua-core.py](#vua-corepy)
2. [vua-manifest-validator.py](#vua-manifest-validatorpy)
3. [vua-attestation-gen.py](#vua-attestation-genpy)
4. [JavaScript APIs](#javascript-apis)
5. [Shell Integration](#shell-integration)
6. [Examples & Recipes](#examples--recipes)
7. [Error Handling](#error-handling)

---

## vua-core.py

Pure Python core library with state management, event logging, and metrics collection.

### Module Classes

**CryptoEngine** — Cryptographic operations using stdlib only
**StateVector** — System state with phi-harmonic resonance
**EventLog** — Immutable event log with SHA-256 chaining
**MetricsCollector** — Metric aggregation & statistics
**VUACore** — Main system engine
**PersistenceManager** — Save/load system state

---

## vua-manifest-validator.py

Manifest creation, validation, SHA-256 verification, and attestation generation.

### CLI Commands

```bash
python vua-manifest-validator.py validate manifest.json
python vua-manifest-validator.py create 1.0.0 shell daemon genesis
python vua-manifest-validator.py attestation manifest.json
```

### Validation Checks

- ✓ Structure validation
- ✓ Credit verification (eternal binding)
- ✓ Module list validation
- ✓ SHA-256 integrity
- ✓ Timestamp format

---

## vua-attestation-gen.py

Cryptographic sealing, attestation chains, and vault management.

### Seal Types

- **state_seal** — Seal state objects
- **manifest_seal** — Seal manifest files
- **execution_seal** — Seal command results
- **build_seal** — Seal build artifacts
- **attestation_chain** — Immutable chain of seals

### CLI Commands

```bash
python vua-attestation-gen.py seal state '{"key": "value"}'
python vua-attestation-gen.py seal manifest manifest.json
python vua-attestation-gen.py verify attestation.json
python vua-attestation-gen.py chain att1.json att2.json
python vua-attestation-gen.py vault add attestation.json
```

---

## JavaScript APIs

### Dashboard (vua-control-dashboard.html)

```javascript
executeCommand()      // Run command executor
quickCommand(cmd)     // Execute quick command
loadTemplate()        // Load payload template
insertBuiltPayload()  // Insert payload
generateManifest()    // Create manifest
generateAttestation() // Generate seal
validateManifest()    // Validate manifest
```

### State Monitor (vua-state-monitor.html)

```javascript
startMonitoring()   // Begin monitoring
pauseMonitoring()   // Pause monitoring
refreshState()      // Update state
exportState()       // Export to JSON
addLog(msg, type)   // Add log entry
```

---

## Shell Integration

```bash
source vua-integration.sh
vua_init 1.0.0 shell daemon genesis
vua_demo
vua_validate
vua_monitor 8000
```

---

## Security Guarantees

✓ **Eternal Binding** — Creator attribution on all outputs
✓ **SHA-256 Sealing** — Cryptographic integrity
✓ **Chainable Attestations** — Immutable audit trail
✓ **Pure Python** — Auditable code
✓ **No Network** — All operations local

---

## Support

Email: axismuse@gmail.com  
Credit: The Architect — Axis Prime — Veroti — Dustin Sean Coffey — Evomorphic  
𓁚 A FORTIORI • SUI GENERIS
