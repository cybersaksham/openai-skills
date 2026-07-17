## Specification-first product workflow

- Use `.agents/skills/maintain-specifications/SKILL.md` automatically for every `.specs/` task and whenever planning or implementation discovers or changes a product, data, interface, event/job, permission, provider, runtime, migration, client, security, acceptance, or documentation contract.
- Use `.agents/skills/create-feature-plan/SKILL.md` for feature/change planning and before non-trivial behavior-affecting implementation.
- Use `.agents/skills/implement-feature/SKILL.md` for end-to-end implementation; it must use both other skills.
- Treat generated `.specs/*.html#anchor` clauses as intended product and system-design authority. Code/tests are implementation evidence and do not silently override the specifications.
- Edit specification sources and regenerate HTML; never hand-edit generated pages.
- Preserve the bundled Stride shell and repository-backed `.specs/_inventory.py`: one focused owner per journey, system flow, discovered runtime source unit, client surface, and declared developer entry flow; keep the only theme switcher at the top right.
- If a required decision is missing, conflicting, or changed, stop dependent work, ask the focused owner question, update/validate/rate specs first, then plan or implement.
- Keep implementation plans in ignored `.plans/` and cite exact `.specs/*.html#anchor` clauses plus conformance evidence.

Merge this block into the existing root `AGENTS.md` without deleting or weakening repository instructions. Reconcile semantic conflicts with the user instead of keeping two competing rules. Remove this proposal after the merge.
