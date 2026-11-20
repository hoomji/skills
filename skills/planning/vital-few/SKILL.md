---
name: vital-few
description: Cut a plan to its vital few, the stories that carry most of its outcome, and park the rest behind a close-out line. Use when starting an initiative or epic, when a plan holds more stories than will ship, when an initiative stays open though most of its value has landed, or when asked for an 80/20 cut.
---

# Vital few

A plan lists everything worth doing; its **outcome** rides on a few **lines**. The cut weighs the lines, finds the **thin path** of stories that makes each one true, and draws a **close-out line** where 80 of 100 points are covered. Stories past the line are **parked**: kept, reasoned, and tied to the event that brings them back.

Any plan works: a BMad initiative or epic, a bead convoy, a PRD, a task list. A *story* is the plan's smallest tracked unit of work. Read stories and their status from the plan's own store. The cut sheet recommends; moving tickets goes through that store's own door.

Three words carry the method:

- A **line** is an observable state the plan promises. Lines earn points.
- A **guard** is a condition the outcome may not ship without, whatever its share of the signal: law, consent, privacy, safety, or a decision the owner has recorded. Guards earn no points and ride the lines they protect.
- A **gate** is a story that builds nothing and approves, polishes, sweeps or releases other stories. A gate takes the class of what it gates.

## Steps

1. **Outcome.** Write one sentence a user or operator of the result could confirm, and the signal that shows it. Take both from the plan's top level; where the plan states none, infer them and mark them *inferred*. Then hold the plan's done-when lines against the signal: a line the signal leaves out is *outside the signal*, either a sign the signal is narrow or a later outcome riding in this plan.

   Done when each clause of the sentence cites the plan text it came from, and every done-when line is marked inside or outside the signal.

2. **Lines.** List the plan's top-level done-when lines, acceptance criteria or goals, falling back to requirements where those are missing or name no observable state. Split a line where its parts can be observed true one without the other. A line that covers a set (providers, pages, doors, screens) splits into a thin line and a rest line where the plan or its data names the few members that carry most of the use. Mark each guard.

   Done when every done-when line and requirement of the plan maps to a line or a guard.

3. **Weigh.** Share 100 points across the lines by how much of the signal each delivers. Weigh by the signal alone: a line's effort, size and place in the plan carry no points. Test each line by removal: at close-out with this line missing, does the outcome sentence still hold? Answer *breaks*, *partly* or *holds*; every *breaks* line outweighs every *partly*, and every *partly* every *holds*. A line outside the signal is weighed as the plan's text reads, and its points are the first candidate for the swing.

   Done when the points sum to 100 and every line carries its removal answer and a one-clause reason from the plan.

4. **Thin path.** For each line, find the fewest stories that make it observably true. A dependency edge is a lead and the removal test decides: a prerequisite joins the path only when the line cannot be observed true without it. A guard's stories join the path of every line the guard protects. Cost each story: 0 when done, 1 when an agent can finish it, 3 when it waits on a human act (a ruling, an approval, counsel, a credential, a production promotion, an acceptance). Read the story's text for the human act; a store's flag undercounts them.

   Done when every line has a path, and every story on a path fails the line when removed.

5. **Cut.** Take lines greedily: each time, the line with the most points per added cost, counting only stories no taken path already holds. A line with no added cost is taken at once; ties go to more points. Stop when taken points reach 80. Stories on taken paths are the **vital few**. Each gate is then vital when a story it gates is vital, counted once. Every other story is parked.

   Done when every story of the plan is vital or parked, every story a vital story waits on is vital too, and the sheet reports three ratios: vital stories over all stories, vital cost over all cost, vital human acts over all human acts.

   A cut that takes more than 40% of the stories is a **finding** about the plan. Name which: one long shared prerequisite chain, lines too coarse to split, an outcome that is several outcomes, or a plan that is thin already. For a thin plan, report the close-out line and the human acts and leave the parking out.

6. **Park.** Group the parked stories by reason. Give each group its reason in a clause and its **re-entry**: the observable event that would make it vital (a customer asks, a metric crosses a number, a later phase opens). Flag as **long lead** any parked human act whose wait outlasts the run-up to its re-entry: it is asked for now and stays parked.

   Done when every parked story sits in a group that has a re-entry.

7. **Close-out line.** Write the evidence that closes the plan: each taken line and how it is observed true. Give the build order: the tracer bullet first (the cheapest path that runs end to end), then lines in the order they were taken. Give the human acts as their own list, asked for on day one, longest wait first. Name the **swing**: the one reading or weight the plan's owner could change that moves the most stories across the line, with the stories it moves in each direction. A done-when line outside the signal is the swing unless another moves more.

   Done when the cut sheet below is filled.

## Cut sheet

```markdown
# Vital few: <plan>

Outcome: <sentence>. Signal: <signal>.
Cut: <v> of <n> stories (<p>%), <c>% of cost, <h> of <H> human acts, <pts> of 100 points.
Finding: <only when step 5 names one>

## Swing
<the reading or weight, and the stories that cross the line each way>

## Lines
| Line | Points | Without it | Reason | Added cost | Taken |

## Guards
| Guard | Rides | Stories |

## Vital few, in build order
| Ref | Story | Line |

## Human acts, day one
| Ref | Act | Who | Line |

## Parked
| Group | Refs | Reason | Re-entry | Long lead |

## Close-out line
<each taken line and the evidence that shows it true>
```

## Holding the line

- A story added after the cut starts parked. It joins a path only when a taken line cannot be observed true without it; the sheet's ratios are then restated.
- The plan closes when its taken lines are observed true. Parked stories move to a follow-up plan, so the closed plan holds no open work.
- Re-cut when a re-entry event fires or the owner moves the swing.
