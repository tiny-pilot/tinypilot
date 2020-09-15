Explanation of the changes, what they achieve, and any design decisions that are worth mentioning.

Fixes #XX (if there's no associated Github issue, delete this line)

**Delete this line and everything after before submitting your PR**

---

## How to get your PR merged quickly

* Give a clear, one-line title to your PR.
  * Good: `Fix dropped keystrokes on Firefox`
  * Bad: `Fix issue`
* Title your PR in the present tense.
  * Good: `Change the background color to hot pink`
  * Bad: `Changing the background color to hot pink`
  * Bad: `Changed the background color to hot pink`
* If your PR is not ready for review, mark it as "draft."
* [Rebase your changes](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase) onto the latest `master` commit so that there are no merge conflicts.
* Your PR must pass build checks in CI before it will be considered for merge.
  * You'll see a green checkmark or red X next to your PR depending on whether your build passed or failed.
  * You are responsible for fixing formatting and tests to ensure that your code passes build checks in CI.

I try to review all PRs within one business day. If you've been waiting longer than this, feel free to comment on the PR to verify that it's on my radar.