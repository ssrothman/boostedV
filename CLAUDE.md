# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview



## Behavior

All claims should be backed up by clear evidence (tests, references, etc.). NEVER report guesses as fact. ALWAYS ask clarifying questions when there is any doubt or ambiguity about the question or task. Only return to the user when you are >= 95% certain that the answer, script, or similar is correct.

NEVER make high-level decisions without consultation.

Keep reports to the user focused on information that is not obvious. Text should value the reader's time. Prefer terse, exact user-facing communications unless exposition is required to convey instructions to the user.

NON-NEGOTIABLE If you are working in a repository that has skills defined: search for skills by reading the CLAUDE.md and then searching the repository's directory structure. Evaluate any found skills for validity in the repo before using them, usually the skills will be relevant, prefer using them.

## Development workflow

When code is added:

1. **Write the minimal program or edit** that achieves the goal.
2. **Add unit tests** only for behavior that is nontrivial, complex, or easy to get wrong (a configuration value, a rename, or a one-line wiring change needs none).
3. **Carefully review the written code** (including the unit tests!) WITHOUT running it for logical correctness, efficiency, and bugs.
4. **Run the code and the tests that could plausibly fail** because of the change, and validate the behavior. Run a pre-existing test only if the change could plausibly break it; do not rerun the full suite for a minor or configuration-only change.
5. **IF THERE ARE ANY BUGS**: return to step one and loop
6. **Return to me only if**:
   - There are no known issues with the new code.
   - The only known issues relate to other pieces of the codebase that are not related to the task at hand.
   - We have agreed that the known issues are not breaking.
   - Any clarification is needed about the desired behavior, architecture, etc.
   - The edits have exposed any issues that we did not know about previously and that require new decisions.

ALWAYS consult documentation for unknown libraries and tools. 

BEFORE writing a new script, check if there already exists a script to achieve your goals.

When running a script, ALWAYS examine the expected inputs and outputs for the script, and any other clear documentation for it. 

A comment is a claim the compiler never checks, so write fewer and shorter. When you add or rewrite a comment, it says one thing the code beneath it cannot: the reason for this choice over the obvious alternative, the invariant kept here, the rule or spec implemented, or a trap for the next editor. One concise and focused sentence is the default. If the comment is outgrowing the code it sits on, cut it; do not polish it. Drop what does not fit; do not move it to a commit message or PR body.
Four kinds of content stay out: what other functions, callers, or tests do; what the code used to do, or why it changed; evidence (measurements, probe results, commands); and restatement of the code.
If you catch yourself arguing in a comment that a hazard is tolerable, stop: say in a line what in the code prevents it, and if nothing prevents it, that is a code finding, handled as code. A wrong comment is repaired by deleting the false sentence, not by writing a more careful one.

- Ensure that it is completely clear what the desired behavior should be. If it is unclear or ambiguous, ask additional questions.
- For large tasks write a clear plan and confer with the human about whether the plan is correct. The plan should be in a dedicated markdown file to avoid context creep.
- Make only the SMALLEST change that achieves the clear objective. Do not touch any code that is not related to the task at hand.
- All new behavior should be documented; nontrivial behavior should also be covered by unit tests.

## Research documentation

All claims should be backed by references either to literature or our own experiments/studies. All references to literature should be double-checked to ensure that the cited article actually supports the cited claim. When possible a variety of sources should be considered in order to determine the extent to which important claims are controversial.

Ideas and results should be documented clearly in human-readable markdown files. When investigating and planning work, write down concise, summarized findings in a journal for an additional dual memory in the current working area. Make sure this file has a table of contents so that it can be easily sliced with `grep` and remains token efficient despite size. As work progresses, compact the log by making summaries of older work. The newest entries should be at the end so that `tail` can be used effectively.

## Project structure

Durable project memory is for facts about this project that are expensive to rediscover: build quirks, tooling traps, architectural decisions and the reasons behind them. Do not record general lessons about how to reason, verify, review, or run agents—that is reasoning you should redo, not state you should carry. Before writing a memory, name what would make it retirable; if nothing ever could, it is a belief rather than a fact and does not belong. Project memory that is mostly about how to be an agent has stopped being about the project, and should be pruned rather than extended.

## Agent workflows

- Sub-agents are allowed to spawn further sub-agents unless the project's CLAUDE.md says otherwise. ALWAYS give sub-agents meaningful, concise names if able. Use Opus high thinking for sub-agents that are planners or reviewers. Use Opus high thinking for sub-agents that are implementers.
- The default name of the lead agent session for messaging is "team-lead", not "main". Never message "main" in multi-agent workflows unless an agent actually needs to message itself.
- In agent-to-agent communications, all agents will be referred to by their session name. If a session does not have a name, use its uuid.
- There is no need to respond or report when receiving a bare idle ping from a sub-agent.

## Git and commits

My github email address is simon.rothman@cern.ch. Use my github details when authoring commits.

NON-NEGOTIABLE If you make a commit, follow conventional commits and add a trailer: `Assisted-by: <harness>:<model-string>`, where `<harness>` is the current agent harness (like ClaudeCode), and `<model-string>` is the AI model and version descriptor string of the model that wrote the code (like `claude-<model>-<version>`). You don't need to add a coauthored-by claude when you have this.

Prefix PR descriptions and comments on PRs with the line `:robot: AI text below :robot:` to indicate you are an agent speaking on a user's behalf.

## Code review and testing

NON-NEGOTIABLE Tests that you do write shall always be provably non-vacuous and discriminating. Provide evidence of these properties in your reports. A report leads with the verdict and carries evidence only for the claims its reader must act on.

NON-NEGOTIABLE When reviewing code: verify findings adversarially. A single finding is not enough to conclude a fix is correct—ensure the fix actually addresses the root cause and doesn't introduce new issues.

