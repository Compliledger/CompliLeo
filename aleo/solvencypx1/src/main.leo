// solvencypx1.aleo
// Minimal proof-program sliver for Aleo.
//
// Proves whether reserves are greater than or equal to liabilities,
// encoding the reserve-adequacy requirement common to stablecoin and
// tokenized-asset frameworks.

program solvencypx1.aleo {

    transition check_solvency(
        reserves: u64,
        liabilities: u64,
    ) -> bool {
        return reserves >= liabilities;
    }
}
