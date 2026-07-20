# Prompting Glossary

Canonical language for this workspace. Terms are added once Henry can use them
correctly — this is a record of compressed understanding, not a dictionary to
read cold. Adhere to these terms in every lesson.

## Terms

**Prompt**:
The full input a model conditions on for one turn — in agentic settings this includes the system prompt, tools, files, and conversation history, not just the last message you typed.
_Avoid_: "the question", "the command"

**Explicitness**:
Stating the requirements a model would otherwise have to guess — scope, format, constraints, what "done" means. Models do not reliably infer unstated intent.
_Avoid_: "being detailed", "being specific" (too vague)

**Intent (context / the "why")**:
The underlying goal behind a request. Supplying it lets the model generalize correctly to cases you didn't spell out, instead of pattern-matching the literal words.
_Avoid_: "background", "explanation"

**Decision frame**:
Intent sharpened to the point of action: the choice you're making and what counts as a win. It's what lets the model tailor an answer to your actual decision instead of producing a neutral survey.
_Avoid_: "goal", "objective" (too broad)

**Altitude**:
The level of abstraction you hand off at — dictating method (low) vs stating the outcome and letting the model find the method (high). The default is to constrain outcome and load-bearing constraints while leaving method to the model; the stronger the model, the higher you fly.
_Avoid_: "detail level", "specificity"

**Few-shot (multishot)**:
Steering by including worked input→output examples of the task before the real one. The examples become the pattern the model generalizes from — so they must be representative (cover the hard cases) and free of accidental regularities.
_Avoid_: "giving examples" (imprecise), "one-shot" (that's exactly one example)
