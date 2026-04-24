# CompliLeo — Regulatory Mapping

> High-level engineering mapping from current U.S. digital asset
> regulatory frameworks to the three CompliLeo proof modules.
>
> **This is engineering context, not legal advice.** Specific
> compliance obligations depend on jurisdiction, entity type, asset
> type, and counsel guidance. CompliLeo provides a ZK proof execution
> layer; it does not substitute for a regulated entity's compliance
> program.

---

## Why This Mapping Exists

Regulators across the U.S. digital asset stack are converging on three
recurring questions for tokenized markets:

1. *Who is allowed to issue, and what is allowed to be issued?*
2. *Are outstanding tokens fully backed?*
3. *Is the system that enforces the above operating with integrity?*

CompliLeo encodes each of those as a separate, minimal Leo program, so
that the answer can be produced as a **public ZK proof result** while
the underlying private financial data stays with the issuer.

---

## GENIUS Act → SolvencyProof / Reserve Backing

**Framework.** The GENIUS Act (*Guiding and Establishing National
Innovation for U.S. Stablecoins*) targets payment stablecoins. Among
other things, it focuses on:

- approved / permissioned issuers, and
- adequate reserves backing outstanding stablecoin liabilities.

**Mapping.**

| GENIUS area | CompliLeo response |
|---|---|
| Reserve adequacy | **SolvencyProof** (`solvencypx1.aleo :: prove_solvency`) proves `reserves >= liabilities` without revealing either figure. |
| Permissioned issuance | Reinforces **TokenProof**'s `issuer_approved` gate (see CLARITY mapping below). |

**What the proof says.** "Reserves are at least equal to liabilities at
the moment this proof was produced." Reserve composition, liability
totals, customer balances, and counterparty identities are not in the
proof.

**What it does not say.** It does not classify the reserve assets,
audit their custody, or attest to historical reserve adequacy.

---

## CLARITY Act → TokenProof / Asset Classification and Market Structure

**Framework.** The CLARITY Act (*Digital Asset Market Clarity Act*)
addresses the market-structure side of digital assets — most visibly
asset classification and which assets are eligible for which venues.

**Mapping.**

| CLARITY area | CompliLeo response |
|---|---|
| Asset classification + supported-asset gating | **TokenProof** (`tokenproofx1.aleo :: verify_token`) proves the candidate asset's `asset_type_supported` flag is true. |
| Permissioned issuer gating | TokenProof also proves `issuer_approved` is true, complementing GENIUS-style issuer requirements. |

**What the proof says.** "This asset cleared issuer approval AND
asset-type gating per this system's CLARITY-aligned policy." The
identity of the issuer, the underlying classification rationale, and
internal whitelists are not in the proof.

**What it does not say.** It does not opine on which legal
classification the asset belongs to — that judgement is upstream of
the proof and is encoded into the `asset_type_supported` input.

---

## SEC / CFTC Tokenization Framework → TokenProof + CompliGuard / Tokenized Market Lifecycle Assurance

**Framework.** The SEC and the CFTC are both producing guidance on
tokenized markets. Themes include market integrity, operational
resilience, and ongoing monitoring across the tokenized-asset
lifecycle (issuance → trading → settlement → custody → reporting).

**Mapping.**

| SEC / CFTC tokenization area | CompliLeo response |
|---|---|
| Lifecycle admission controls | **TokenProof** at the issuance / admission stage. |
| Operational integrity + ongoing monitoring | **CompliGuard** (`compliguardx1.aleo :: prove_health`) proves the compliance system itself is healthy: anomaly score within bounds AND no critical alert open. |
| Repeatable, machine-checkable assurance | The deterministic CompliLeo **proof bundle** lets regulators, auditors, and counterparties consume a hash-anchored result on a recurring cadence. |

**What the proofs say.** Together: "this asset belongs in this market,
and the compliance system enforcing that judgment is operating within
defined bounds right now."

**What they do not say.** They do not replace continuous market
surveillance, trade-level enforcement, or supervisory examination.
They make the compliance posture machine-verifiable.

---

## Composite View

| Regulatory anchor | CompliLeo module | Public proof result |
|---|---|---|
| GENIUS Act — reserve backing | **SolvencyProof** | `solvent: bool` |
| GENIUS Act — issuer approval | **TokenProof** (`issuer_approved` gate) | `valid: bool` |
| CLARITY Act — asset classification gating | **TokenProof** (`asset_type_supported` gate) | `valid: bool` |
| SEC / CFTC tokenization framework — operational integrity | **CompliGuard** | `healthy: bool` |
| SEC / CFTC tokenization framework — lifecycle assurance | **Combined proof bundle** | hash-anchored aggregate |

A single recurring run of the three modules + bundle gives a regulated
private stablecoin or tokenized-asset system a **privacy-preserving
compliance posture** that is checkable by any third party using only
the public bundle.

---

## Status of This Mapping

- This mapping is intended to track the *intent* of the named
  frameworks, not specific clauses, and will evolve as the frameworks
  themselves do.
- The CompliLeo MVP encodes the simplest defensible boolean form of
  each requirement. Richer rule shapes (thresholds, weighted scores,
  composite conditions) are an explicit future-phase item — see
  [`roadmap.md`](./roadmap.md).
- Nothing in this document is legal advice. Regulated entities should
  consult qualified counsel before relying on any specific compliance
  posture.
