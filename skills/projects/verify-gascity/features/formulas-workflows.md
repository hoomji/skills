# Formulas and graph.v2 workflows

A formula is a TOML recipe of steps; packs ship them (`internal/bootstrap/packs/core/formulas/`
for the core `mol-*` set) and a city adds its own under `formulas/`. `gc formula list` and
`gc formula show` compile and display them; slinging work with a formula
(`gc sling <target> <text|bead> --on <formula>`) instantiates a workflow: a root bead with
`gc.formula_contract = graph.v2`, one bead per step, and `blocks`/`tracks` deps forming the
step graph that the controller and workers advance.

## Sub-features

- `fx-list` `gc formula list` names every formula visible to the city (core pack plus city formulas).
- `fx-show` `gc formula show <name>` prints description, variables with defaults, and `Steps (n)` with `[needs: ...]`; `--json` gives `vars`, `steps`, `deps`; `--var k=v` previews substitution.
- `fx-instantiate` `gc sling <agent> "<text>" --on <formula>` creates the work bead, an input convoy and a workflow root; the JSON reply carries `workflow_id` and a dashboard `runs/<id>` URL.
- `fx-graph` the workflow's beads and deps match the formula's steps and needs (API `/v0/city/{city}/workflow/{id}`).
- `fx-cook-guard` a v2 formula that uses `convoy_id` refuses an untargeted `gc formula cook` with a reserved-variable error and writes nothing.
- `fx-live` a live formula and a live workflow's step graph are readable without a write.

## How to get to it (user POV)

- `gc formula list`, `gc formula show <name> [--json] [--var k=v]`, `gc sling ... --on <formula>`,
  `gc formula cook <name>`, `gc convoy list`, `gc graph <id> --tree`, the dashboard Runs page.
- Docs: `docs/guides/understanding-formulas.md`, `docs/reference/specs/formula-spec-v2.md`,
  `docs/tutorials/05-formulas.md` (corpus).

## Driving it with gascity.py

Preconditions:

- Isolated instance doctor clean.

- **List.** `$H gc $RUN -- formula list` prints `mol-do-work`, `mol-polecat-base`,
  `mol-polecat-commit`, `mol-polecat-report`, `mol-prompt-synth`, `mol-review-quorum`,
  `mol-scoped-work`.
- **Show.** `$H gc $RUN --name fx-show -- formula show mol-do-work` ends with `Steps (3):`
  `do-work`, `drain [needs: mol-do-work.do-work]`, `workflow-finalize [needs: mol-do-work.drain]`
  and lists `{{escalation_target}}` `(default=human)`. `-- formula show mol-do-work --json`
  has `schema_version: "1"` and the same three steps in `steps`.
- **Cook guard.** `$H gc $RUN -- formula cook mol-do-work` exits 1 with
  `convoy_id requires a targeted formulas v2 invocation`; `$H gc $RUN -- convoy list` is
  unchanged.
- **Instantiate.** `$H gc $RUN --name fx-sling -- sling mayor "verify-gascity probe" --on mol-do-work --json`
  prints `"method":"on-formula"`, `"formula":"mol-do-work"`, `"workflow_id":"<id>"`.
  `$H gc $RUN -- convoy list` shows `input convoy for <work bead>`.
- **Graph.** `$H api $RUN --name fx-workflow '/v0/city/{city}/workflow/<id>'`: `beads` holds
  the root (`kind: workflow`, metadata `gc.formula_contract: graph.v2`,
  `gc.formula_name: mol-do-work`) and three step beads whose `step_ref` are the formula's
  step ids; `deps` reads do-work → drain (`blocks`), drain → workflow-finalize (`blocks`),
  workflow-finalize → root (`tracks`). That edge list is the formula's `needs` chain.
- **Live.** `$H live -- formula list`; `$H live -- formula show receipt-grader-pass --json`
  (3 steps). Find a live workflow root from the event log:
  `$H live -- events --since 1h --type bead.created --payload-match bead.metadata.gc.kind=workflow`
  (each line's `payload.bead.id`, with `gc.formula_name` and `gc.formula_contract: graph.v2`),
  then `$H api live --max-time 30 '/v0/city/{city}/workflow/<id>'`: the step beads'
  `step_ref` match `formula show`'s steps and `deps` carry the `blocks`/`tracks` edges
  (about 1 s, no memory change on the live supervisor in run t2).

## Gotchas

- `gc graph <workflow-root> --tree` prints only the root bead (`1 bead(s)`), and
  `gc graph <input-convoy> --tree` only the work bead: the CLI graph expands convoy
  children, not graph.v2 step beads. Read the step graph from the workflow API.
- Never read `/runs*` on the live supervisor (the harness refuses it): the first request
  starts a cold replay of the whole `~/city/.gc/events.jsonl` (66 MB on 10-19) inside the
  live process, which took about 2.5 min and pushed its RSS from 4.2 to 5.4 GB. Once warm it
  reported 2845 `active` runs, far above the live lane count: treat its census as unproven.
- `/v0/city/{city}/runs/<id>/steps` answers `503 run projection is warming` for a few
  seconds after launch, then `{"steps": []}` for a workflow no worker has started; it is not
  the step graph.
- Under fake sessions nothing executes a step: the workflow stays `pending`. Proving step
  execution needs a real provider and belongs to a live-city read of a finished run.
- `gc.formula_source` points into `$GC_HOME/cache/repos/<hash>/...`: the core pack is
  materialized per `GC_HOME`, so an isolated instance reads the binary's embedded pack, not
  the live city's cache.
- `gc formula cook` and `gc sling` are writes: instance only.
