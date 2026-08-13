"""Pure status-summary domain model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Literal, Mapping

CheckState = Literal["pass", "fail", "unknown"]
AggregateState = Literal["healthy", "degraded", "unknown"]
ALLOWED_STATES = frozenset({"pass", "fail", "unknown"})


@dataclass(frozen=True)
class CheckResult:
    name: str
    state: CheckState

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("check result name must be non-empty")
        if self.state not in ALLOWED_STATES:
            accepted = ", ".join(sorted(ALLOWED_STATES))
            raise ValueError(
                f"unsupported check state {self.state!r}; expected one of: {accepted}"
            )


@dataclass(frozen=True)
class StatusSummary:
    aggregate_state: AggregateState
    total: int
    passed: int
    failed: int
    unknown: int
    failed_checks: tuple[str, ...]
    unknown_checks: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["failed_checks"] = list(self.failed_checks)
        value["unknown_checks"] = list(self.unknown_checks)
        return value


def parse_check_results(items: Iterable[Mapping[str, object]]) -> tuple[CheckResult, ...]:
    results: list[CheckResult] = []
    for index, item in enumerate(items):
        name = item.get("name")
        state = item.get("state")
        if not isinstance(name, str):
            raise ValueError(f"check result at index {index} must have a string name")
        if not isinstance(state, str):
            raise ValueError(f"check result at index {index} must have a string state")
        results.append(CheckResult(name=name, state=state))  # type: ignore[arg-type]
    return tuple(results)


def summarize(results: Iterable[CheckResult]) -> StatusSummary:
    ordered = tuple(results)
    failed_checks = tuple(result.name for result in ordered if result.state == "fail")
    unknown_checks = tuple(
        result.name for result in ordered if result.state == "unknown"
    )
    passed = sum(result.state == "pass" for result in ordered)

    if failed_checks:
        aggregate_state: AggregateState = "degraded"
    elif unknown_checks or not ordered:
        aggregate_state = "unknown"
    else:
        aggregate_state = "healthy"

    return StatusSummary(
        aggregate_state=aggregate_state,
        total=len(ordered),
        passed=passed,
        failed=len(failed_checks),
        unknown=len(unknown_checks),
        failed_checks=failed_checks,
        unknown_checks=unknown_checks,
    )
