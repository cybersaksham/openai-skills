#!/usr/bin/env python3
"""Regression tests for the generic specification source and renderer contracts."""

from __future__ import annotations

import tempfile
import unittest
from collections import Counter
from pathlib import Path

from _inventory import RUNTIME_MODULE_INVENTORY
from _spec_core import href_for, inline, load_pages, render_block, render_contract_registry, render_page
from _validate import validate_block, validate_inventory, validate_runtime_discovery


class SpecificationCoreTests(unittest.TestCase):
    def test_inline_escapes_text_and_renders_local_links(self) -> None:
        rendered = inline('Use <unsafe> and [[Details|architecture/system-map.html#scope]]', 'features/example.html')
        self.assertIn('&lt;unsafe&gt;', rendered)
        self.assertIn('../architecture/system-map.html#scope', rendered)

    def test_nested_routes_compute_asset_and_page_links(self) -> None:
        self.assertEqual(href_for('architecture/backend/accounts.html', 'index.html'), '../../index.html')
        self.assertEqual(href_for('architecture/backend/accounts.html', '#flow'), '#flow')

    def test_unknown_block_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, 'Unsupported specification block type'):
            render_block({'type': 'raw-html'}, 'index.html')

    def test_code_blocks_escape_content(self) -> None:
        rendered = render_block({'type': 'code', 'language': 'html', 'code': '<script>alert(1)</script>'}, 'index.html')
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_loader_rejects_sources_without_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'broken.py').write_text('VALUE = 1\n')
            with self.assertRaisesRegex(ValueError, 'has no PAGE'):
                load_pages(Path(directory))

    def test_loader_reads_independent_page_modules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'one.py').write_text("PAGE = {'route': 'one.html'}\n")
            pages = load_pages(Path(directory))
            self.assertEqual(pages[0]['route'], 'one.html')
            self.assertTrue(pages[0]['_source'].endswith('one.py'))

    def test_rendered_page_uses_canonical_stride_shell_and_topbar_theme(self) -> None:
        page = {
            'route': 'index.html',
            'nav_group': 'Start here',
            'nav_order': 0,
            'title': 'Documentation home',
            'summary': 'Canonical documentation shell.',
            'kind': 'overview',
            'sections': [{'id': 'scope', 'title': 'Scope', 'blocks': [{'type': 'paragraph', 'text': 'Exact scope.'}]}],
            'related': [],
            'contracts': [],
        }
        rendered = render_page(page, [page])
        for landmark in (
            'class="sidebar-header"',
            'class="documentation-nav"',
            'class="documentation-layout"',
            'class="content"',
            'class="page-rail"',
            'class="page-navigation"',
        ):
            self.assertIn(landmark, rendered)
        topbar = rendered.split('<header class="topbar">', 1)[1].split('</header>', 1)[0]
        self.assertIn('data-theme-toggle', topbar)
        sidebar_footer = rendered.split('<div class="sidebar-footer">', 1)[1].split('</div>', 1)[0]
        self.assertNotIn('data-theme-toggle', sidebar_footer)

    def test_nested_navigation_uses_stride_documentation_hierarchy(self) -> None:
        overview = {
            'route': 'features/example.html',
            'nav_group': 'Product guides',
            'nav_subgroup': 'Manage',
            'nav_parent': 'Example feature',
            'nav_order': 0,
            'title': 'Example feature overview',
            'summary': 'Example.',
            'kind': 'overview',
            'sections': [{'id': 'scope', 'title': 'Scope', 'blocks': [{'type': 'paragraph', 'text': 'Scope.'}]}],
            'related': [],
            'contracts': [],
        }
        flow = {
            **overview,
            'route': 'features/example/create.html',
            'nav_category': 'User flows',
            'nav_order': 10,
            'title': 'Create one example record',
        }
        rendered = render_page(flow, [overview, flow])
        self.assertIn('class="nav-subgroups"', rendered)
        self.assertIn('class="nav-subgroup nav-feature"', rendered)
        self.assertIn('<div class="nav-caption">User flows</div>', rendered)

    def test_developer_flow_renders_exact_symbols_reads_and_writes(self) -> None:
        flow = {
            'id': 'code-flow-example',
            'title': 'Commit one example command',
            'trigger': 'POST /examples',
            'initiator': 'Authorized workspace member',
            'authority': 'examples.policy.can_create',
            'entry_point': 'examples.http.create -> examples.commands.create',
            'steps': [
                {'title': 'Parse', 'symbols': ['examples.http.create'], 'reads': ['request.body'], 'writes': ['none: validation only'], 'behavior': 'Validate the sealed input.'},
                {'title': 'Authorize', 'symbols': ['examples.policy.can_create'], 'reads': ['WorkspaceGrant'], 'writes': ['none: policy read'], 'behavior': 'Apply current scope.'},
                {'title': 'Commit', 'symbols': ['examples.commands.create'], 'reads': ['Example'], 'writes': ['Example', 'OutboxEvent'], 'behavior': 'Write state and outbox atomically.'},
                {'title': 'Dispatch', 'symbols': ['examples.jobs.publish'], 'reads': ['OutboxEvent'], 'writes': ['PublishedEvent'], 'behavior': 'Run after commit.'},
            ],
            'data_effects': 'Creates Example and OutboxEvent.',
            'transaction': 'One transaction commits before dispatch.',
            'handoff': 'examples.created.v1 -> examples.jobs.publish',
            'duplicates_concurrency': 'Idempotency key returns the committed response.',
            'terminal': '201 and committed ExampleDTO.',
            'failures': 'Validation and authorization fail without writes.',
            'observability': 'Safe ids and duration only.',
            'recovery': 'Replay the outbox event after repair.',
        }
        rendered = render_block({'type': 'developer-flow', 'flow': flow}, 'architecture/backend/modules/examples.html')
        self.assertIn('examples.commands.create', rendered)
        self.assertIn('<strong>Reads:</strong>', rendered)
        self.assertIn('<strong>Writes:</strong>', rendered)
        self.assertIn('Terminal failures', rendered)

    def test_contract_registry_renders_exact_contract_fields(self) -> None:
        page = {
            'route': 'reference/scenarios.html',
            'contracts': [{
                'kind': 'scenario',
                'id': 'SCN-EXAMPLE-001',
                'anchor': 'scenario-example',
                'actor': 'member',
                'authority': 'workspace grant',
                'fixture': 'deterministic fixture',
                'invocation': 'POST /examples',
                'response': '201',
                'effects': 'one row',
                'forbidden_effects': 'no duplicate row',
                'controls': 'frozen clock',
                'cleanup': 'rollback fixture',
                'evidence': 'service and API tests',
            }],
        }
        rendered = render_contract_registry(page)
        self.assertIn('SCN-EXAMPLE-001', rendered)
        self.assertIn('forbidden effects', rendered)
        self.assertIn('service and API tests', rendered)

    def test_aggregate_style_developer_flow_without_step_evidence_is_rejected(self) -> None:
        errors = []
        metrics = Counter()
        validate_block({
            'type': 'developer-flow',
            'flow': {
                'id': 'code-flow-too-vague',
                'title': 'Persist and invoke',
                'trigger': 'request',
                'authority': 'member',
                'entry_point': 'handler',
                'steps': [('Persist', 'Write state'), ('Invoke', 'Call provider')],
                'data_effects': 'records change',
                'transaction': 'transactional',
                'handoff': 'worker',
                'terminal': 'done',
                'recovery': 'retry',
            },
        }, 'test flow', errors, metrics)
        self.assertTrue(any('missing' in error for error in errors))
        self.assertTrue(any('at least four' in error for error in errors))
        self.assertTrue(any('exact route/event/schedule and symbol' in error for error in errors))

    def test_repository_discovery_rejects_collapsing_two_source_units_into_one_handbook(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Path(root, 'backend/internal/alpha').mkdir(parents=True)
            Path(root, 'backend/internal/beta').mkdir(parents=True)
            Path(root, 'backend/internal/alpha/main.go').write_text('package alpha\n')
            Path(root, 'backend/internal/beta/main.go').write_text('package beta\n')
            metrics = Counter()
            errors = validate_runtime_discovery(
                True,
                metrics,
                repo_root=root,
                discovery_roots=[{'path': 'backend/internal', 'mode': 'child-directories', 'include_extensions': ['.go']}],
                exclusions=[],
                runtime_modules=[{
                    'id': 'runtime-alpha-and-beta',
                    'role': 'implementation',
                    'source_unit': 'backend/internal/alpha',
                    'owned_paths': ['backend/internal/alpha', 'backend/internal/beta'],
                }],
            )
            self.assertIn('Discovered runtime source unit has no focused handbook owner: backend/internal/beta', errors)
            self.assertEqual(metrics['runtime_units_discovered'], 2)
            self.assertEqual(metrics['runtime_units_owned'], 1)

    def test_repository_discovery_accepts_one_focused_owner_per_source_unit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Path(root, 'services/accounts').mkdir(parents=True)
            Path(root, 'services/notifications').mkdir(parents=True)
            Path(root, 'services/accounts/service.py').write_text('def run(): pass\n')
            Path(root, 'services/notifications/service.py').write_text('def run(): pass\n')
            errors = validate_runtime_discovery(
                True,
                Counter(),
                repo_root=root,
                discovery_roots=[{'path': 'services', 'mode': 'child-directories', 'include_extensions': ['.py']}],
                exclusions=[],
                runtime_modules=[
                    {'id': 'runtime-accounts', 'role': 'implementation', 'source_unit': 'services/accounts', 'owned_paths': ['services/accounts']},
                    {'id': 'runtime-notifications', 'role': 'implementation', 'source_unit': 'services/notifications', 'owned_paths': ['services/notifications']},
                ],
            )
            self.assertEqual(errors, [])

    def test_final_runtime_inventory_requires_settings_then_common(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Path(root, 'backend/config').mkdir(parents=True)
            Path(root, 'backend/common').mkdir(parents=True)
            Path(root, 'backend/config/settings.py').write_text('SETTING = True\n')
            Path(root, 'backend/common/ids.py').write_text('def new_id(): pass\n')
            errors = validate_runtime_discovery(
                False,
                Counter(),
                repo_root=root,
                discovery_roots=[
                    {'path': 'backend/config', 'mode': 'root', 'include_extensions': ['.py']},
                    {'path': 'backend/common', 'mode': 'root', 'include_extensions': ['.py']},
                ],
                exclusions=[],
                runtime_modules=[
                    {'id': 'runtime-common', 'role': 'common', 'source_unit': 'backend/common', 'owned_paths': ['backend/common']},
                    {'id': 'runtime-settings', 'role': 'settings', 'source_unit': 'backend/config', 'owned_paths': ['backend/config']},
                ],
            )
            self.assertTrue(any('must list settings then common' in error for error in errors))

    def test_root_discovery_cannot_hide_source_bearing_child_packages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Path(root, 'backend/internal/alpha').mkdir(parents=True)
            Path(root, 'backend/internal/beta').mkdir(parents=True)
            Path(root, 'backend/internal/root.go').write_text('package internal\n')
            Path(root, 'backend/internal/alpha/main.go').write_text('package alpha\n')
            Path(root, 'backend/internal/beta/main.go').write_text('package beta\n')
            errors = validate_runtime_discovery(
                True,
                Counter(),
                repo_root=root,
                discovery_roots=[{'path': 'backend/internal', 'mode': 'root', 'include_extensions': ['.go']}],
                exclusions=[],
                runtime_modules=[{
                    'id': 'runtime-everything',
                    'role': 'implementation',
                    'source_unit': 'backend/internal',
                    'owned_paths': ['backend/internal'],
                }],
            )
            self.assertTrue(any('root mode would hide source-bearing child units' in error for error in errors))

    def test_short_settings_and_common_not_applicable_reasons_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Path(root, 'worker').mkdir()
            Path(root, 'worker/main.py').write_text('def run(): pass\n')
            errors = validate_runtime_discovery(
                False,
                Counter(),
                repo_root=root,
                discovery_roots=[{'path': 'worker', 'mode': 'root', 'include_extensions': ['.py']}],
                exclusions=[],
                runtime_modules=[{'id': 'worker', 'role': 'implementation', 'source_unit': 'worker', 'owned_paths': ['worker']}],
                settings_not_applicable_reason='none',
                common_not_applicable_reason='none',
            )
            self.assertTrue(any('settings owner or a concrete' in error for error in errors))
            self.assertTrue(any('common owner or a concrete' in error for error in errors))

    def test_two_runtime_units_cannot_share_one_handbook_route(self) -> None:
        original = list(RUNTIME_MODULE_INVENTORY)
        try:
            RUNTIME_MODULE_INVENTORY[:] = [
                {
                    'id': 'runtime-alpha',
                    'title': 'Alpha',
                    'route': 'architecture/backend/modules/combined.html',
                    'role': 'implementation',
                    'source_unit': 'backend/alpha',
                    'owned_paths': ['backend/alpha'],
                    'public_boundary': 'alpha.public',
                    'entry_flows': ['code-flow-combined'],
                    'scenario_ids': ['SCN-COMBINED-001'],
                },
                {
                    'id': 'runtime-beta',
                    'title': 'Beta',
                    'route': 'architecture/backend/modules/combined.html',
                    'role': 'implementation',
                    'source_unit': 'backend/beta',
                    'owned_paths': ['backend/beta'],
                    'public_boundary': 'beta.public',
                    'entry_flows': ['code-flow-combined'],
                    'scenario_ids': ['SCN-COMBINED-001'],
                },
            ]
            pages = [{
                'route': 'architecture/backend/modules/combined.html',
                'kind': 'runtime-module',
                'contracts': [{'id': 'SCN-COMBINED-001', 'kind': 'scenario'}],
                'sections': [{'blocks': [{'type': 'developer-flow', 'flow': {'id': 'code-flow-combined'}}]}],
            }]
            errors = validate_inventory(pages, True, Counter())
            self.assertTrue(any('reuses focused page' in error for error in errors))
        finally:
            RUNTIME_MODULE_INVENTORY[:] = original


if __name__ == '__main__':
    unittest.main(verbosity=2)
