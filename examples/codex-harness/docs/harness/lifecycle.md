# Engineering lifecycle

| State | Required artifact or evidence | Exit condition |
| --- | --- | --- |
| Intake | Request or issue with user problem | Outcome and owner are clear |
| Specify | Product spec or explicit acceptance criteria | Observable behavior and non-goals resolved |
| Design | Indexed design doc when system or feature design changes | Rationale, constraints, interfaces, alternatives, verification state, and related ADRs are explicit |
| Decide | ADR when architecture changes | Durable choice and consequences recorded |
| Plan | ExecPlan for complex work | Steps, decisions, verification, and recovery are actionable |
| Implement | Small scoped diff | Required behavior is present |
| Verify | Focused, full, runtime, and harness evidence as applicable | Each criterion has distinguishing evidence |
| Review | Evidence review against spec and repository standards | Blocking findings resolved or explicitly owned |
| Publish | Branch/PR under R2 authority | Remote state and target recorded |
| Merge/release | R3/R4 gates and recovery | Authorized outcome observed |
| Learn | Learning ledger entry for repeated friction | Durable change or decision not to encode recorded |
| Garden | Read-only freshness and drift scan | Findings triaged; approved fixes remain small |

The lifecycle is not a rigid waterfall. A failed verification returns to specification, decision, plan, or implementation according to the cause.
