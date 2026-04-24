// solvencypx1.aleo
// -----------------------------------------------------------------------------
// Minimal proof-program sliver for Aleo, written in Leo.
//
// Purpose
//   Proves the reserve-adequacy property required by stablecoin and
//   tokenized-asset frameworks: that an entity's reserves are at least
//   as large as its liabilities, without revealing either figure.
//
// Both inputs are private u64 values. The transition returns a single
// public boolean: `true` when reserves cover liabilities.
//
// This is intentionally tiny — just enough to demonstrate end-to-end
// zero-knowledge execution on Aleo for the "SolvencyProof" concept.
// Real execution will be wired in after this sliver is validated.
// -----------------------------------------------------------------------------

// The program name here MUST match the `program` field in program.json.
program solvencypx1.aleo {

    // prove_solvency — reserve-adequacy proof.
    //
    // Inputs (private):
    //   reserves    : total reserves held, in the smallest accounting unit.
    //   liabilities : total outstanding liabilities, in the same unit.
    //
    // Output (public):
    //   bool — true iff reserves >= liabilities.
    transition prove_solvency(
        reserves: u64,
        liabilities: u64,
    ) -> bool {
        // Reserves must fully cover liabilities for the entity to be solvent.
        return reserves >= liabilities;
    }
}
