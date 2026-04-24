// tokenproofx1.aleo
// -----------------------------------------------------------------------------
// Minimal proof-program sliver for Aleo, written in Leo.
//
// Purpose
//   Proves that a tokenized asset satisfies the two basic admission rules
//   required before it can be admitted to a compliant ledger:
//     1. the issuer has been approved by a compliance authority, AND
//     2. the asset type is one of the supported categories.
//
// Both inputs are private booleans. The transition returns a single public
// boolean: `true` only when both gating conditions hold.
//
// This is intentionally tiny — just enough to demonstrate end-to-end
// zero-knowledge execution on Aleo for the "TokenProof" concept. Real
// execution will be wired in after this sliver is validated.
// -----------------------------------------------------------------------------

// The program name here MUST match the `program` field in program.json.
program tokenproofx1.aleo {

    // verify_token — token admission proof.
    //
    // Inputs (private):
    //   issuer_approved      : the issuer has cleared compliance review.
    //   asset_type_supported : the asset class is supported on the platform.
    //
    // Output (public):
    //   bool — true iff both inputs are true.
    transition verify_token(
        issuer_approved: bool,
        asset_type_supported: bool,
    ) -> bool {
        // Both gating conditions must hold for the token to be admitted.
        return issuer_approved && asset_type_supported;
    }
}
