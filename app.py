from shiny import App, render, ui, Inputs, Outputs, Session
from shiny import reactive
import math
import random

app_ui = ui.page_fluid(
    ui.row(
        ui.column(6, ui.h2("Hunger Games Simulator")),
        ui.column(6, ui.tags.div(
            ui.output_ui("theme_button"),
            style="text-align: right;"
        )),
        style="align-items: center;"
    ),
    ui.navset_card_pill(
        ui.nav_panel(
            "Settings",
            ui.input_numeric(
                "num_players",
                "Number of Tributes",
                12,
                min=12, max=24
            ),
            ui.output_ui("tribute_inputs"),
            ui.output_ui("tribute_list"),
            ui.output_ui("ranks"),
            ui.output_ui("alliances"),
            ui.output_ui("traits"),
        ),
        ui.nav_panel(
            "Game",
        ),
        ui.nav_panel(
            "Statistics",
        ),
        id="tab",
    )
)

def server(input: Inputs, output: Outputs, session: Session):
    # store saved tribute names (as list of district dicts)
    tributes = reactive.Value([])
    alliances_store = reactive.Value(None)   # will hold alliances (None = random/not set)
    traits_store = reactive.Value(None)      # will hold traits assignments
    ranks_store = reactive.Value(None)       # will hold rank assignments
    theme_mode = reactive.Value('light')    # track current theme mode

    @reactive.effect
    @reactive.event(input.num_players)
    def show_warning():
        n = input.num_players()
        if n is None:
            return
        if n < 12 or n > 24:
            ui.notification_show(
                "Please choose between 12 and 24 tributes.",
                type="error",
                duration=3
            )
        else:
            ui.notification_show(
                "Number of tributes OK.",
                type="default",
                duration=1
            )

    # dynamic UI: either show input boxes+Save (when not saved) or saved summary + Edit button (when saved)
    @output
    @render.ui
    def tribute_inputs():
        n = input.num_players()
        saved = tributes.get()
        # if tributes saved -> show summary + Edit button
        if saved:
            items = []
            for d in saved:
                trib_names = " & ".join([t for t in d["tributes"] if t])
                items.append(ui.tags.li(ui.tags.strong(f"District {d['district']}: "), trib_names))
            return ui.TagList(
                ui.hr(),           # horizontal divider between num_players and tribute list
                ui.tags.h4("The Tributes:"),
                ui.tags.ul(*items),
                ui.tags.br(),
                ui.input_action_button("edit_tributes", "Edit tributes")
            )

        # otherwise show inputs (as before)
        if n is None or n < 12 or n > 24:
            return ui.HTML("<p>Enter a valid number of tributes (12–24) to show input fields.</p>")

        inputs = [ui.input_text(f"tribute_{i}", f"Tribute {i+1}", value="") for i in range(n)]

        # split into two columns
        half = (n + 1) // 2
        left_inputs = inputs[:half]
        right_inputs = inputs[half:]

        # two-column row (each column uses half the width)
        cols = ui.row(
            ui.column(6, *left_inputs),
            ui.column(6, *right_inputs)
        )

        # include Save button with a divider above the tribute inputs
        return ui.TagList(
            ui.tags.hr(),           # horizontal divider between num_players and tribute inputs
            cols,
            ui.tags.br(),
            ui.input_action_button("save_tributes", "Save tributes")
        )

    # when Save button is clicked, collect values and store them (assign to districts)
    @reactive.effect
    @reactive.event(input.save_tributes)
    def save_tributes():
        n = input.num_players()
        if n is None:
            ui.notification_show("No number of tributes set.", type="error", duration=2)
            return

        # collect raw names in order
        names = []
        for i in range(n):
            try:
                val = getattr(input, f"tribute_{i}")()
            except Exception:
                val = ""
            names.append((val or "").strip())

        if any(name == "" for name in names):
            ui.notification_show(
                "Please fill in all tribute names before saving.",
                type="warning",
                duration=3
            )
            return

        # assign to districts, two tributes per district
        districts = []
        for i in range(0, len(names), 2):
            district_num = i // 2 + 1
            pair = names[i:i+2]
            if len(pair) < 2:
                pair.append("")
            districts.append({"district": district_num, "tributes": pair})

        tributes.set(districts)
        alliances_store.set(None)
        traits_store.set(None)
        ranks_store.set(None)
        ui.notification_show("Tribute names saved and assigned to districts.", type="success", duration=2)

    # Edit button: unsave tributes and return to input mode
    @reactive.effect
    @reactive.event(input.edit_tributes)
    def edit_tributes():
        # clear saved tributes so tribute_inputs will render input boxes again
        tributes.set([])
        alliances_store.set(None)
        traits_store.set(None)
        ranks_store.set(None)
        ui.notification_show("You can now edit tribute names.", type="default", duration=2)

    def _saved_tribute_names_and_districts(saved):
        names = []
        districts = []
        for d in saved:
            for t in d["tributes"]:
                if t:
                    names.append(t)
                    districts.append(d["district"])
        return names, districts

    # Render alliances configuration area (mode selector + manual inputs)
    @output
    @render.ui
    def alliances():
        saved = tributes.get()
        if not saved:
            ui.hr()
            return ui.HTML("<p>Save tributes first to configure alliances.</p>")

        # preserve the current selection if present, otherwise default to Random
        try:
            mode = input.alliances_mode()
        except Exception:
            mode = "Random"
        radios = ui.input_radio_buttons("alliances_mode", "", ["Random", "Manual"], selected=mode)

        # hide the explanatory paragraph if random alliances were already generated
        stored = alliances_store.get()

        show_paragraph = True
        if stored is not None and mode == "Random":
            show_paragraph = False

        parts = [
            ui.h4("Alliances mode"),
            ui.tags.div(radios, style="margin-top:10px;"),
            ui.tags.br(),
            ui.row(
                ui.column(6, ui.output_ui("alliances_manual_container")),
                ui.column(6, ui.output_ui("alliances_preview")),
            ),
            ui.tags.br(),
        ]

        if show_paragraph:
            parts.append(ui.tags.p("Choose 'Manual' to pick allies for each tribute, then click Save."))

        return ui.TagList(*parts)

    @output
    @render.ui
    def ranks():
        saved = tributes.get()
        if not saved:
            ui.hr()
            return ui.HTML("<p>Save tributes first to assign ranks.</p>")

        try:
            mode = input.ranks_mode()
        except Exception:
            mode = "Random"
        radios = ui.input_radio_buttons("ranks_mode", "", ["Random", "Manual"], selected=mode)
        stored = ranks_store.get()

        show_paragraph = True
        if stored is not None and mode == "Random":
            show_paragraph = False

        parts = [
            ui.h4("Rank assignment"),
            ui.tags.div(radios, style="margin-top:10px;"),
            ui.tags.br(),
            ui.row(
                ui.column(6, ui.output_ui("ranks_manual_container")),
                ui.column(6, ui.output_ui("ranks_preview")),
            ),
            ui.tags.br(),
        ]
        if show_paragraph:
            parts.append(ui.tags.p("Choose 'Manual' to assign each tribute a rank from 1 to 12, or generate random ranks."))

        return ui.TagList(*parts)

    @output
    @render.ui
    def ranks_manual_container():
        saved = tributes.get()
        mode = None
        try:
            mode = input.ranks_mode()
        except Exception:
            mode = "Random"

        if mode != "Manual":
            return ui.TagList(ui.input_action_button("generate_ranks", "Generate random ranks"))

        names, _ = _saved_tribute_names_and_districts(saved)
        if not names:
            return ui.HTML("<p>No tributes available.</p>")

        stored = ranks_store.get() or {}
        rank_choices = [str(i) for i in range(1, 13)]

        max_rows = 3
        n = len(names)
        ncols = (n + max_rows - 1) // max_rows
        col_width = max(1, 12 // ncols)
        cols = []
        for col_idx in range(ncols):
            start = col_idx * max_rows
            end = min(start + max_rows, n)
            items = []
            for i in range(start, end):
                nm = names[i]
                selected = str(stored.get(nm, "")) if stored.get(nm) is not None else None
                items.append(
                    ui.tags.div(
                        ui.tags.label(nm, style="font-weight:600; display:block; margin-bottom:8px;"),
                        ui.input_select(f"rank_for_{i}", "", choices=rank_choices, selected=selected),
                        style="margin-bottom:14px;"
                    )
                )
            cols.append(ui.column(col_width, *items))

        return ui.TagList(
            ui.tags.hr(),
            ui.row(*cols),
            ui.tags.br(),
            ui.input_action_button("save_ranks", "Save ranks")
        )

    @output
    @render.ui
    def ranks_preview():
        saved = tributes.get()
        if not saved:
            return ui.HTML("<p>No tributes saved.</p>")

        names, _ = _saved_tribute_names_and_districts(saved)
        preview_items = []
        stored = ranks_store.get()

        if stored:
            for n in names:
                rank = stored.get(n)
                preview_items.append(ui.tags.li(ui.tags.strong(f"{n}: "), str(rank) if rank is not None else "—"))
        else:
            for i, n in enumerate(names):
                try:
                    val = getattr(input, f"rank_for_{i}")()
                except Exception:
                    val = None
                preview_items.append(ui.tags.li(ui.tags.strong(f"{n}: "), str(val) if val is not None else "—"))

        return ui.TagList(
            ui.h4("Rank preview"),
            ui.tags.ul(*preview_items)
        )

    @reactive.effect
    @reactive.event(input.save_ranks)
    def save_ranks():
        saved = tributes.get()
        if not saved:
            ui.notification_show("No tributes to assign ranks.", type="error", duration=2)
            return

        names, _ = _saved_tribute_names_and_districts(saved)
        mapping = {}
        for i, n in enumerate(names):
            try:
                raw = getattr(input, f"rank_for_{i}")()
            except Exception:
                raw = None
            if raw is None or raw == "":
                ui.notification_show("Please assign all ranks before saving.", type="warning", duration=3)
                return
            try:
                mapping[n] = int(raw)
            except ValueError:
                mapping[n] = None

        ranks_store.set(mapping)
        ui.notification_show("Ranks saved.", type="success", duration=2)

    @reactive.effect
    @reactive.event(input.generate_ranks)
    def generate_ranks():
        saved = tributes.get()
        if not saved:
            ui.notification_show("No saved tributes to generate ranks.", type="error", duration=2)
            return

        names, _ = _saved_tribute_names_and_districts(saved)
        mapping = {n: random.randint(1, 12) for n in names}
        ranks_store.set(mapping)
        ui.notification_show("Random ranks generated.", type="success", duration=2)

    # manual container shows inputs only when manual mode selected
    @output
    @render.ui
    def alliances_manual_container():
        saved = tributes.get()
        mode = None
        try:
            mode = input.alliances_mode()
        except Exception:
            mode = "Random"

        if mode != "Manual":
            # show Generate random button for convenience
            return ui.TagList(ui.input_action_button("generate_alliances", "Generate random alliances"))

        # create checkbox groups arranged into columns with at most 3 rows per column
        names = [t for d in saved for t in d["tributes"] if t]
        if not names:
            return ui.HTML("<p>No tributes available.</p>")

        max_rows = 3
        n = len(names)
        ncols = (n + max_rows - 1) // max_rows
        # compute bootstrap column width (12-grid)
        col_width = max(1, 12 // ncols)

        cols = []
        for col_idx in range(ncols):
            start = col_idx * max_rows
            end = min(start + max_rows, n)
            items = []
            for i in range(start, end):
                nm = names[i]
                choices = [c for c in names if c != nm]
                items.append(
                    ui.tags.div(
                        ui.tags.label(nm, style="font-weight:600; display:block; margin-bottom:8px;"),
                        ui.input_checkbox_group(f"ally_for_{i}", "", choices=choices),
                        style="margin-bottom:14px;"
                    )
                )
            cols.append(ui.column(col_width, *items))

        return ui.TagList(
            ui.tags.hr(),
            ui.row(*cols),
            ui.tags.br(),
            ui.input_action_button("save_alliances", "Save alliances")
        )

    # preview output: reads current checkbox values (does NOT re-render the inputs)
    @output
    @render.ui
    def alliances_preview():
        saved = tributes.get()
        if not saved:
            return ui.HTML("<p>No tributes saved.</p>")

        names = [t for d in saved for t in d["tributes"] if t]
        preview_items = []

        stored = alliances_store.get()
        if stored:
            # show saved alliances (pairs or mapping)
            if isinstance(stored, dict) and "pairs" in stored:
                for pair in stored["pairs"]:
                    preview_items.append(ui.tags.li(", ".join([p for p in pair if p])))
            elif isinstance(stored, dict):
                for n in names:
                    allies = stored.get(n, [])
                    preview_items.append(ui.tags.li(ui.tags.strong(f"{n}: "), ", ".join(allies) if allies else "—"))
            else:
                preview_items.append(ui.tags.li(str(stored)))
        else:
            # live preview from current checkbox-group inputs
            for i, n in enumerate(names):
                try:
                    val = getattr(input, f"ally_for_{i}")()
                except Exception:
                    val = None
                if isinstance(val, (list, tuple)):
                    allies = [a for a in val if a]
                elif isinstance(val, str):
                    allies = [a.strip() for a in val.split(",") if a.strip()]
                else:
                    allies = []
                preview_items.append(ui.tags.li(ui.tags.strong(f"{n}: "), ", ".join(allies) if allies else "—"))

        return ui.TagList(
            ui.h4("Alliances"),
            ui.tags.ul(*preview_items)
        )

    # Save manual alliances: parse comma-separated ally names and validate against saved tributes
    @reactive.effect
    @reactive.event(input.save_alliances)
    def save_alliances():
        saved = tributes.get()
        if not saved:
            ui.notification_show("No saved tributes to assign alliances.", type="error", duration=2)
            return

        names = [t for d in saved for t in d["tributes"] if t]
        name_set = set(names)
        alliances = {}
        for i, n in enumerate(names):
            try:
                raw = getattr(input, f"ally_for_{i}")()
            except Exception:
                raw = None

            # raw may be a list (from select multiple) or a comma-separated string (fallback)
            if isinstance(raw, (list, tuple)):
                allies = [a for a in raw if a and a in name_set and a != n]
            elif isinstance(raw, str):
                allies = [a.strip() for a in raw.split(",") if a.strip() and a.strip() in name_set and a.strip() != n]
            else:
                allies = []

            alliances[n] = allies

        alliances_store.set(alliances)
        ui.notification_show("Manual alliances saved.", type="success", duration=2)

    # Generate random alliances (variable number of allies per tribute; some may have none)
    @reactive.effect
    @reactive.event(input.generate_alliances)
    def generate_alliances():
        saved = tributes.get()
        if not saved:
            ui.notification_show("No saved tributes to generate alliances.", type="error", duration=2)
            return

        names = [t for d in saved for t in d["tributes"] if t]
        if not names:
            ui.notification_show("No tributes to assign.", type="error", duration=2)
            return

        # Probability that any given other tribute becomes an ally (adjustable)
        p_ally = 0.25

        alliances = {}
        for name in names:
            allies = []
            for other in names:
                if other == name:
                    continue
                if random.random() < p_ally:
                    allies.append(other)
            alliances[name] = allies

        alliances_store.set(alliances)
        ui.notification_show("Random alliances generated.", type="success", duration=2)

    # Traits UI and handlers
    @output
    @render.ui
    def traits():
        saved = tributes.get()
        if not saved:
            ui.hr()
            return ui.HTML("<p>Save tributes first to assign traits.</p>")

        # preserve current selection if available so switching to Manual isn't undone by rerender
        try:
            mode = input.traits_mode()
        except Exception:
            mode = "Random"
        radios = ui.input_radio_buttons("traits_mode", "", ["Random", "Manual"], selected=mode)
        stored = traits_store.get()

        show_paragraph = True
        if stored is not None and mode == "Random":
            show_paragraph = False

        parts = [
            ui.h4("Traits"),
            ui.tags.div(radios, style="margin-top:10px;"),
            ui.tags.br(),
            ui.row(
                ui.column(6, ui.output_ui("traits_manual_container")),
                ui.column(6, ui.output_ui("traits_preview")),
            ),
            ui.tags.br(),
        ]
        if show_paragraph:
            parts.append(ui.tags.p("Choose 'Manual' to pick traits per tribute, or generate random traits."))

        return ui.TagList(*parts)

    @output
    @render.ui
    def traits_manual_container():
        saved = tributes.get()
        mode = None
        try:
            mode = input.traits_mode()
        except Exception:
            mode = "Random"

        if mode != "Manual":
            return ui.TagList(ui.input_action_button("generate_traits", "Generate random traits"))

        TRAIT_CHOICES = ["Brave", "Cunning", "Strong", "Stealthy", "Charismatic", "Resourceful", "Agile"]
        names, districts = _saved_tribute_names_and_districts(saved)
        if not names:
            return ui.HTML("<p>No tributes available.</p>")

        # arrange inputs into columns of at most 3 rows like alliances UI
        max_rows = 3
        n = len(names)
        ncols = (n + max_rows - 1) // max_rows
        col_width = max(1, 12 // ncols)
        cols = []
        for col_idx in range(ncols):
            start = col_idx * max_rows
            end = min(start + max_rows, n)
            items = []
            for i in range(start, end):
                nm = names[i]
                # Career is only available for districts 1,2,4
                choices = TRAIT_CHOICES[:]
                selected = None
                if districts[i] in (1, 2, 4):
                    choices = choices + ["Career"]
                    selected = ["Career"]  # pre-select Career (it will also be enforced on save)
                items.append(
                    ui.tags.div(
                        ui.tags.label(nm, style="font-weight:600; display:block; margin-bottom:8px;"),
                        ui.input_checkbox_group(f"traits_for_{i}", "", choices=choices, selected=selected),
                        style="margin-bottom:14px;"
                    )
                )
            cols.append(ui.column(col_width, *items))

        return ui.TagList(
            ui.tags.hr(),
            ui.row(*cols),
            ui.tags.br(),
            ui.input_action_button("save_traits", "Save traits")
        )

    @output
    @render.ui
    def traits_preview():
        saved = tributes.get()
        if not saved:
            return ui.HTML("<p>No tributes saved.</p>")

        names, districts = _saved_tribute_names_and_districts(saved)
        preview_items = []
        stored = traits_store.get()

        if stored:
            for i, n in enumerate(names):
                tr = stored.get(n, [])
                if districts[i] in (1, 2, 4) and "Career" not in tr:
                    tr = ["Career"] + tr
                preview_items.append(ui.tags.li(ui.tags.strong(f"{n}: "), ", ".join(tr) if tr else "—"))
        else:
            for i, n in enumerate(names):
                try:
                    val = getattr(input, f"traits_for_{i}")()
                except Exception:
                    val = None
                if isinstance(val, (list, tuple)):
                    traits = [a for a in val if a]
                elif isinstance(val, str):
                    traits = [a.strip() for a in val.split(",") if a.strip()]
                else:
                    traits = []
                # enforce showing Career for district 1,2,4 even if not explicitly selected
                if districts[i] in (1, 2, 4) and "Career" not in traits:
                    traits = ["Career"] + traits
                preview_items.append(ui.tags.li(ui.tags.strong(f"{n}: "), ", ".join(traits) if traits else "—"))

        return ui.TagList(
            ui.h4("Traits preview"),
            ui.tags.ul(*preview_items)
        )

    @reactive.effect
    @reactive.event(input.save_traits)
    def save_traits():
        saved = tributes.get()
        if not saved:
            ui.notification_show("No tributes to assign traits.", type="error", duration=2)
            return

        names, districts = _saved_tribute_names_and_districts(saved)
        mapping = {}
        for i, n in enumerate(names):
            try:
                raw = getattr(input, f"traits_for_{i}")()
            except Exception:
                raw = None
            if isinstance(raw, (list, tuple)):
                chosen = [a for a in raw if a]
            elif isinstance(raw, str):
                chosen = [a.strip() for a in raw.split(",") if a.strip()]
            else:
                chosen = []
            # ensure Career is present for districts 1,2,4
            if districts[i] in (1, 2, 4) and "Career" not in chosen:
                chosen = ["Career"] + chosen
            mapping[n] = chosen

        traits_store.set(mapping)
        ui.notification_show("Traits saved.", type="success", duration=2)

    @reactive.effect
    @reactive.event(input.generate_traits)
    def generate_traits():
        saved = tributes.get()
        if not saved:
            ui.notification_show("No saved tributes to generate traits.", type="error", duration=2)
            return

        TRAIT_CHOICES = ["Brave", "Cunning", "Strong", "Stealthy", "Charismatic", "Resourceful", "Agile"]
        p_trait = 0.25
        names, districts = _saved_tribute_names_and_districts(saved)

        mapping = {}
        for i, n in enumerate(names):
            chosen = [trait for trait in TRAIT_CHOICES if random.random() < p_trait]
            # add Career for districts 1,2,4
            if districts[i] in (1, 2, 4) and "Career" not in chosen:
                chosen = ["Career"] + chosen
            mapping[n] = chosen

        traits_store.set(mapping)
        ui.notification_show("Random traits generated.", type="success", duration=2)

    @output
    @render.ui
    def theme_button():
        mode = theme_mode.get() or 'light'
        label = '☾' if mode == 'light' else '☼'
        return ui.input_action_button("toggle_theme", label, style="padding:4px 8px; font-size:1.1rem;")

    @reactive.effect
    @reactive.event(input.toggle_theme)
    def toggle_theme():
        current = theme_mode.get() or 'light'
        next_mode = 'dark' if current == 'light' else 'light'
        theme_mode.set(next_mode)
        ui.update_dark_mode(next_mode)
        ui.notification_show(f"Switched to {next_mode} mode.", type="default", duration=2)

app = App(app_ui, server)

if __name__ == "__main__":
    # Run with: python app.py
    try:
        from shiny import run_app
        # change host/port if needed (port may be in use)
        run_app(app, host="127.0.0.1", port=8000, debug=True)
    except Exception as e:
        import traceback, sys
        print("Failed to start Shiny server:", e, file=sys.stderr)
        traceback.print_exc()