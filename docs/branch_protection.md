# Enabling Branch Protection on `main`

To ensure the regression gate actually blocks degraded prompt changes from being merged into production, you must configure a branch protection rule on your repository.

1. Go to your repository on GitHub.
2. Click **Settings** > **Branches** (under the "Code and automation" section).
3. Click **Add branch protection rule**.
4. In the **Branch name pattern** box, type `main`.
5. Check the box for **Require status checks to pass before merging**.
6. In the search box that appears under "Status checks that are required", type the name of your regression job (e.g., `test_and_deploy` or `run_regression_suite` depending on the exact name of the job in `.github/workflows/on_prompt_change.yml`).
   - *Note: You may need to trigger the workflow once on a PR for the status check name to appear in the search box.*
7. Check the box for **Require a pull request before merging**.
8. Click **Create** at the bottom of the page to save the rule.

With this enabled, if a prompt change degrades output quality on the Golden Set and the Wilcoxon test fails, the GitHub Actions check will fail, and the "Merge pull request" button will be blocked.
