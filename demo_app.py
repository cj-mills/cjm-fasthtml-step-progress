"""Demo application for cjm-fasthtml-step-progress library.

Showcases the step progress bar component with interactive step switching,
multiple configurations, and theme switching.

Run with: python demo_app.py
"""


def main():
    """Initialize step progress demos and start the server."""
    from fasthtml.common import (
        fast_app, Div, H1, H2, H3, P, Button, Li, Ul, APIRouter
    )

    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes
    from cjm_fasthtml_daisyui.components.navigation.steps import steps, step, step_colors
    from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui
    from cjm_fasthtml_daisyui.utilities.border_radius import border_radius

    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import max_w, w
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight
    from cjm_fasthtml_tailwind.utilities.effects import opacity
    from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
        flex_display, flex_direction, flex_wrap, gap, items
    )
    from cjm_fasthtml_tailwind.core.base import combine_classes

    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout

    from cjm_fasthtml_step_progress.core.models import StepInfo
    from cjm_fasthtml_step_progress.core.config import StepProgressConfig
    from cjm_fasthtml_step_progress.components.progress_bar import render_step_progress

    print("\n" + "=" * 70)
    print("Initializing cjm-fasthtml-step-progress Demo")
    print("=" * 70)

    APP_ID = "stepprog"

    app, rt = fast_app(
        pico=False,
        hdrs=[*get_daisyui_headers(), create_theme_persistence_script()],
        title="Step Progress Demo",
        htmlkw={'data-theme': 'light'},
        session_cookie=f'session_{APP_ID}_',
        secret_key=f'{APP_ID}-demo-secret',
    )

    router = APIRouter(prefix="")

    # ── Step definitions ──────────────────────────────────────────────────

    DECOMP_STEPS = [
        StepInfo("Selection"),
        StepInfo("Segment & Align"),
        StepInfo("Review"),
        StepInfo("Verify"),
    ]

    PIPELINE_STEPS = [
        StepInfo("Ingest"),
        StepInfo("Chunk"),
        StepInfo("Transcribe"),
        StepInfo("Validate"),
        StepInfo("Correct"),
        StepInfo("Filter"),
        StepInfo("Group"),
        StepInfo("Export"),
    ]

    MINIMAL_STEPS = [
        StepInfo("Upload"),
        StepInfo("Process"),
    ]

    # ── Demo configurations ───────────────────────────────────────────────

    demos = {
        'default': {
            'title': 'Default (4 steps)',
            'description': 'Decomposition workflow with default config.',
            'steps': DECOMP_STEPS,
            'config': StepProgressConfig(),
            'current': 0,
        },
        'pipeline': {
            'title': 'Pipeline (8 steps)',
            'description': 'Longer pipeline to test scaling.',
            'steps': PIPELINE_STEPS,
            'config': StepProgressConfig(id='pipeline-progress'),
            'current': 0,
        },
        'minimal': {
            'title': 'Minimal (2 steps)',
            'description': 'Two-step workflow.',
            'steps': MINIMAL_STEPS,
            'config': StepProgressConfig(id='minimal-progress'),
            'current': 0,
        },
        'custom': {
            'title': 'Custom Styling',
            'description': 'Secondary fill, box radius, bottom tooltips, taller.',
            'steps': DECOMP_STEPS,
            'config': StepProgressConfig(
                fill_bg='secondary',
                border_radius='box',
                tooltip_position='bottom',
                height=4,
                id='custom-progress',
            ),
            'current': 0,
        },
        'no_tooltips': {
            'title': 'No Tooltips',
            'description': 'Tooltips disabled — minimal visual only.',
            'steps': DECOMP_STEPS,
            'config': StepProgressConfig(show_tooltips=False, id='notip-progress'),
            'current': 0,
        },
    }

    # ── Helper: render a demo section ─────────────────────────────────────

    def render_demo_section(demo_id):
        """Render one demo section with progress bar and step buttons."""
        demo = demos[demo_id]
        step_list = demo['steps']
        config = demo['config']
        current = demo['current']

        # Step switching buttons
        btn_cls = combine_classes(btn, btn_sizes.xs)
        btn_active_cls = combine_classes(btn, btn_sizes.xs, btn_colors.primary)
        buttons = []
        for i, s in enumerate(step_list):
            cls = btn_active_cls if i == current else btn_cls
            buttons.append(Button(
                s.title,
                cls=cls,
                hx_post=f'/set_step/{demo_id}/{i}',
                hx_target=f'#{demo_id}-section',
                hx_swap='outerHTML',
            ))

        btn_row_cls = combine_classes(
            flex_display, flex_direction.row, flex_wrap.wrap, gap(2), items.center, m.t(4)
        )

        section_cls = combine_classes(p(6), bg_dui.base_200, border_radius.box)

        return Div(
            H3(demo['title'], cls=combine_classes(font_size.lg, font_weight.semibold, m.b(2))),
            P(demo['description'], cls=combine_classes(font_size.sm, opacity(50), m.b(4))),
            render_step_progress(step_list, current, config),
            Div(*buttons, cls=btn_row_cls),
            cls=section_cls,
            id=f'{demo_id}-section',
        )

    # ── DaisyUI steps comparison ──────────────────────────────────────────

    def render_daisyui_comparison(current=1):
        """Render the DaisyUI steps component for size comparison."""
        step_items = []
        for idx, s in enumerate(DECOMP_STEPS):
            if idx <= current:
                cls = combine_classes(step, step_colors.primary)
            else:
                cls = step
            step_items.append(Li(s.title, cls=cls))

        section_cls = combine_classes(p(6), bg_dui.base_200, border_radius.box)

        return Div(
            H3("DaisyUI Steps (for comparison)",
               cls=combine_classes(font_size.lg, font_weight.semibold, m.b(2))),
            P("The built-in component this library replaces. Note the vertical space difference.",
              cls=combine_classes(font_size.sm, opacity(50), m.b(4))),
            Ul(*step_items, cls=combine_classes(steps, w.full)),
            cls=section_cls,
        )

    # ── Page content ──────────────────────────────────────────────────────

    def page_content():
        """Build the full demo page."""
        container_cls = combine_classes(max_w._4xl, m.x.auto, p(8))

        return Div(
            H1("Step Progress Bar",
               cls=combine_classes(font_size._2xl, font_weight.bold, m.b(2))),
            P("Compact, theme-aware step progress indicator for multi-step workflows.",
              cls=combine_classes(font_size.sm, opacity(50), m.b(8))),
            Div(
                *[render_demo_section(d) for d in demos],
                render_daisyui_comparison(),
                cls=combine_classes(flex_display, flex_direction.col, gap(6)),
            ),
            cls=container_cls,
        )

    # ── Routes ────────────────────────────────────────────────────────────

    @router
    def index(request):
        return handle_htmx_request(
            request, page_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    @router("/set_step/{demo_id}/{step_idx}", methods=["POST"])
    def set_step(demo_id: str, step_idx: int):
        if demo_id in demos:
            demos[demo_id]['current'] = step_idx
        return render_demo_section(demo_id)

    # ── Navbar & route registration ───────────────────────────────────────

    navbar = create_navbar(
        title="Step Progress Demo",
        nav_items=[
            ("Home", index),
        ],
        home_route=index,
        theme_selector=True,
    )

    register_routes(app, router)

    # Debug output
    print("\n" + "=" * 70)
    print("Registered Routes:")
    print("=" * 70)
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
    print("=" * 70)
    print("Demo App Ready!")
    print("=" * 70 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    app = main()

    port = 5036
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print(f"\n  http://{display_host}:{port}/  — Homepage")
    print()

    timer = threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    uvicorn.run(app, host=host, port=port)
