// tokenproofx1.aleo
// Proves whether a tokenized asset satisfies basic admission rules.
//
// CompliLeo turns regulatory requirements from GENIUS, CLARITY, and
// SEC/CFTC tokenization frameworks into executable zero-knowledge proof
// programs on Aleo.

program tokenproofx1.aleo {

    // check_token_admission returns true only when the issuer is approved
    // AND the asset type is supported — encoding the two fundamental
    // gatekeeping conditions required before a tokenized asset may be
    // admitted to a compliant ledger.
    transition check_token_admission(
        issuer_approved: bool,
        asset_type_supported: bool
    ) -> bool {
        return issuer_approved && asset_type_supported;
    }
}
