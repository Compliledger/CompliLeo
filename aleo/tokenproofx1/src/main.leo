// tokenproofx1.aleo
// Minimal proof-program sliver for Aleo.
//
// Proves whether a tokenized asset satisfies basic admission rules:
// the issuer must be approved AND the asset type must be supported.

program tokenproofx1.aleo {

    transition check_token_admission(
        issuer_approved: bool,
        asset_type_supported: bool,
    ) -> bool {
        return issuer_approved && asset_type_supported;
    }
}
