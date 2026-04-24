// compliguardx1.aleo
// Minimal proof-program sliver for Aleo.
//
// Proves whether the compliance system itself is healthy: the anomaly
// score is below the configured threshold AND no critical alert is open.

program compliguardx1.aleo {

    transition check_system_health(
        anomaly_score_below_threshold: bool,
        critical_alert_open: bool,
    ) -> bool {
        return anomaly_score_below_threshold && !critical_alert_open;
    }
}
