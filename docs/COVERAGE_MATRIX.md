# Stage 2 coverage matrix and proposed synthetic parameters

## Corpus status

The repository currently contains two official-looking DTU documents supplied by the user, not the three-document minimum in the build specification. `policy.pdf` is text-extractable. `Notice_Studnt_O26_240826.pdf` is image-only in the supplied PDF; the user supplied a companion transcription at `data/documents/Notice_Studnt_O26_240826.transcript.txt`. The transcription is treated as an extraction aid for the same document, not as a third source.

This limitation is recorded rather than hidden. The later system must not claim full compliance with the real-corpus minimum unless a third independently sourced DTU document is added and verified.

## Verified sources

| Source ID | Evidence used | Document status |
|---|---|---|
| `DTU-TP-2025-26` | `policy.pdf`, pages 1-7, clauses 1-33 and closing exception | User-provided DTU placement policy PDF; text-extractable |
| `DTU-EXAM-2026-08-24` | `Notice_Studnt_O26_240826.pdf`, page 1, paragraphs (a)-(e), using the supplied companion transcription | User-provided DTU Examination Branch notice; original PDF is scanned/image-only |

## Topic coverage

| Topic | Classification | Verified references | Interpretation boundary |
|---|---|---|---|
| Minimum attendance percentage for examination eligibility | `PARTIALLY_SUPPORTED_BY_REAL_SOURCE` | `DTU-EXAM-2026-08-24#p1`, paragraph (c); `DTU-TP-2025-26#31`, p6 | Sources require fulfillment of attendance criteria but do not state a numeric threshold or condonation rule. |
| Exam/course registration eligibility | `SUPPORTED_BY_REAL_SOURCE` | `DTU-EXAM-2026-08-24#p1`, paragraphs (a)-(e) | Supports registered-course and admit-card conditions. |
| Pass marks | `NOT_COVERED_BY_REAL_SOURCES` | None | No total-mark or external-mark pass threshold found in the two supplied sources. |
| Supplementary examination eligibility and procedure | `NOT_COVERED_BY_REAL_SOURCES` | None | No supplementary-examination rule found. |
| Placement eligibility | `PARTIALLY_SUPPORTED_BY_REAL_SOURCE` | `DTU-TP-2025-26#15`, p4; `DTU-TP-2025-26#1-2`, p1; `DTU-TP-2025-26#31`, p6 | Real source describes company-specific CGPA criteria and placement conditions, but does not define a universal CGPA/backlog/detained threshold. |
| Condonation and exceptions | `PARTIALLY_SUPPORTED_BY_REAL_SOURCE` | `DTU-TP-2025-26#2`, p1; `DTU-TP-2025-26#7-8`, pp1-2; closing exception, p7 | Real source includes placement exceptions and a general VC exception, but not an academic attendance condonation procedure. |

## Proposed fictional parameters for approval

These values are proposed for the two-document synthetic policy layer only. They are not DTU policy and must never be presented as official university rules.

| Parameter | Baseline S1 proposal | Amendment S2 proposal | Proposed superseded references | Rationale |
|---|---:|---:|---|---|
| `attendance_min_exam_pct` | 75 | 80 effective 2026-09-01 | `DTU-EXAM-2026-08-24#p1`; `DTU-TP-2025-26#31` | Demonstrates explicit amendment resolution while the real sources remain qualitative. |
| `attendance_condonation_lower_pct` | 65 | 65 | `DTU-EXAM-2026-08-24#p1` | Demonstrates a lower-bound exception; subject to the baseline attendance rule. |
| `attendance_condonation_max_courses` | 2 | 2 | `DTU-EXAM-2026-08-24#p1` | Fictional bounded exception for deterministic testing. |
| `pass_total_min_marks` | 40 / 100 | 40 / 100 | None; `NOT_COVERED_BY_REAL_SOURCES` | Creates a clearly synthetic rule where no real threshold exists. |
| `pass_external_min_marks` | 24 / 60 | 24 / 60 | None; `NOT_COVERED_BY_REAL_SOURCES` | Creates a clearly synthetic rule where no real threshold exists. |
| `supplementary_allowed_results` | FAIL, ABSENT; not DETAINED | unchanged | None; `NOT_COVERED_BY_REAL_SOURCES` | Enables deterministic tool and edge-case coverage. |
| `supplementary_max_courses` | 2 | 2 | None; `NOT_COVERED_BY_REAL_SOURCES` | Bounded fictional eligibility rule. |
| `placement_min_cgpa` | 7.0 | 7.0 | `DTU-TP-2025-26#15` (demo precedence only) | The real source leaves CGPA to company directives; the synthetic value is a fictional demo threshold, not an official override. |
| `placement_max_active_backlogs` | 2 | 2 | None; `NOT_COVERED_BY_REAL_SOURCES` | No universal backlog threshold appears in the real sources. |
| `placement_no_detained` | true | true | None; `NOT_COVERED_BY_REAL_SOURCES` | No detained-result rule appears in the real sources. |

## Approval gate

Before Stage 3, approve or revise the proposed values and the amendment effective date. The synthetic documents, rules, and student records must not be generated until approval is explicit. A third verified DTU document remains a compliance blocker for the original full specification, even if the demo proceeds with this documented two-source limitation.
