// solvencypx1.aleo
// Proves whether reserves are greater than or equal to liabilities.
//
// CompliLeo turns regulatory requirements from GENIUS, CLARITY, and
// SEC/CFTC tokenization frameworks into executable zero-knowledge proof
// programs on Aleo.

program solvencypx1.aleo {

    // check_solvency returns true when reserves >= liabilities, encoding
    // the reserve-adequacy requirement common to stablecoin and
    // tokenized-asset frameworks such as GENIUS and CLARITY.
    transition check_solvency(
        reserves: u64,
        liabilities: u64
    ) -> bool {
        return reserves >= liabilities;
    }
}
