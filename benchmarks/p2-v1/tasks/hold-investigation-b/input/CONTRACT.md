Each build has project,build_id,sequence,status. Choose greatest integer sequence
per project first, regardless of status. Ties repeat identical rows and count once.
Only then include selected builds whose status is success. summarize(builds)
returns {"successful_projects": N,"build_ids": [ids sorted by project name]}.
A latest failure means the project contributes nothing, not its older success.
Inputs must be unchanged. Run python3 scripts/export.py builds.json totals.json.
