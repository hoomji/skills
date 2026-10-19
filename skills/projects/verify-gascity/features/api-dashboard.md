# API and dashboard

The supervisor serves a typed HTTP + SSE API (OpenAPI 3.1, `docs/reference/schema/openapi.json`)
and, on the same listener, the embedded single-page dashboard. Port and bind come from
`$GC_HOME/supervisor.toml` (`[supervisor] port`, default 8372, bind `127.0.0.1`).
`gc dashboard --no-open` / `gc dashboard serve` print the URL. Mutations need the
`X-GC-Request` header; this skill sends GETs only.

## Sub-features

- `api-health` `GET /health` returns `status: ok`, `version`, `build_id`, `uptime_sec`, `cities_running`, `startup.phase`.
- `api-cities` `GET /v0/cities` lists registered cities with `running`.
- `api-city` `GET /v0/city/{city}` and `/v0/city/{city}/status` reflect the city (suspended, agents, sessions).
- `api-reads` `GET` on `/sessions`, `/orders`, `/orders/history`, `/formulas`, `/formula/{name}`, `/events`, `/runs`, `/workflow/{id}` return JSON; errors are RFC 9457 problem bodies with a `code`.
- `api-headers` every response carries `X-GC-Request-Id`.
- `dash-serve` `GET /` and client routes such as `/city/{city}/runs` return the SPA HTML; `gc dashboard serve` prints the same origin.

## How to get to it (user POV)

- Browser at `http://127.0.0.1:<port>/`; `gc dashboard` opens it, `--no-open` prints it.
- `curl http://127.0.0.1:<port>/v0/...`; the generated clients; `gc --city-url`.
- Docs: `docs/reference/api.md`, `docs/getting-started/dashboard.md` (corpus).

## Driving it with gascity.py

Preconditions:

- Isolated instance doctor clean; `jq .api /tmp/vgc-$RUN/instance.json` is the origin.

- **Health.** `$H api $RUN --name health /health`: 200, `status: "ok"`, `cities_running: 1`,
  `startup.ready: true`; `build_id` equals the commit in `instance.json` `version`.
- **Cities.** `$H api $RUN /v0/cities`: one item `vgc-<run>`, `running: true`, matching
  `$H gc $RUN -- cities`.
- **City.** `$H api $RUN '/v0/city/{city}'` and `'/v0/city/{city}/status'`: compare
  `suspended` and the agent list with `$H gc $RUN -- status --json`.
- **Reads.** `$H api $RUN '/v0/city/{city}/sessions'`, `'/v0/city/{city}/orders'`,
  `'/v0/city/{city}/formulas'`, `'/v0/city/{city}/events'`: each 200 JSON; the order and
  formula names equal `gc order list` / `gc formula list`.
- **Errors.** `$H api $RUN --name not-found '/v0/city/{city}/workflow/nope-1'`: a 4xx
  `application/problem+json` body with `type: urn:gascity:error:...` and a `code`; the
  transcript shows `X-GC-Request-Id`.
- **Dashboard.** `$H api $RUN --name dash /` and `'/city/{city}/runs'`: 200 `text/html`
  starting `<!doctype html>`. `$H gc $RUN -- dashboard serve` prints
  `The dashboard is served by the gc supervisor at http://127.0.0.1:<port>`. For a visual
  proof, open that URL in a browser (claude-in-chrome) and screenshot the city switcher;
  isolated only.
- **Live (GET only).** `$H api live /health`, `$H api live /v0/cities`,
  `$H api live '/v0/city/{city}/status'`, `$H live -- dashboard serve`. Never POST, PATCH,
  DELETE or open an SSE `.../stream` without `--max-time`.

## Gotchas

- The static `<title>` of the dashboard is `gas city · ds-research`
  (`internal/api/dashboardspa/web/frontend/index.html:6`, nothing sets `document.title`);
  do not treat the tab title as identifying the city.
- `/v0/city/{city}/orders/check` is a GET but evaluates order triggers, and `/runs*` makes
  the live supervisor cold-replay its whole event log (see the formulas feature): the
  harness refuses `/runs`, `/stream` and `/orders/check` on `api live` (`LIVE_API_DENY`).
  Run them on the isolated instance.
- `gc dashboard` without `--no-open` launches a browser on the host; the live allowlist
  only admits `dashboard serve` or `--no-open`.
- SSE routes (`/events/stream`, `/session/{id}/stream`) never end on their own; the
  harness's `--max-time` (default 10 s) bounds them and records a status-0 timeout.
- The live supervisor logs every API request to `~/.gc/supervisor.log`
  (`api: GET ... req_id=`): a live read is visible there, which is also how to prove it
  happened.
