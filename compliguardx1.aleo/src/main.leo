// compliguardx1.aleo
// Proves whether the system is operating within defined health conditions.
//
// CompliLeo turns regulatory requirements from GENIUS, CLARITY, and
// SEC/CFTC tokenization frameworks into executable zero-knowledge proof
// programs on Aleo.

program compliguardx1.aleo {

    // check_system_health returns true only when the anomaly score is
    // below the configured threshold AND no critical alert is currently
    // open — ensuring the compliance system itself is operating within
    // acceptable bounds before any further proofs are relied upon.
    transition check_system_health(
        anomaly_score_below_threshold: bool,
        critical_alert_open: bool
    ) -> bool {
        return anomaly_score_below_threshold && !critical_alert_open;
    }
}
