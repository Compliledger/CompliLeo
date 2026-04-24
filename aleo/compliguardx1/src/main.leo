// compliguardx1.aleo
// -----------------------------------------------------------------------------
// Minimal proof-program sliver for Aleo, written in Leo.
//
// Purpose
//   Proves that the compliance system itself is operating within healthy
//   bounds, so that downstream proofs (token admission, solvency, etc.)
//   can be relied upon. The "system healthy" condition is:
//     1. the anomaly-detection score is below the configured threshold, AND
//     2. no critical compliance alert is currently open.
//
// Both inputs are private booleans. The transition returns a single public
// boolean: `true` only when the system is healthy.
//
// This is intentionally tiny — just enough to demonstrate end-to-end
// zero-knowledge execution on Aleo for the "CompliGuard" concept. Real
// execution will be wired in after this sliver is validated.
// -----------------------------------------------------------------------------

// The program name here MUST match the `program` field in program.json.
program compliguardx1.aleo {

    // prove_health — system-health proof.
    //
    // Inputs (private):
    //   anomaly_score_below_threshold : the anomaly score is within bounds.
    //   critical_alert_open           : a critical alert is currently open.
    //
    // Output (public):
    //   bool — true iff the anomaly score is below threshold AND no
    //          critical alert is open.
    transition prove_health(
        anomaly_score_below_threshold: bool,
        critical_alert_open: bool,
    ) -> bool {
        // Healthy = anomalies in check AND no open critical alert.
        return anomaly_score_below_threshold && !critical_alert_open;
    }
}
