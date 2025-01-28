import os

from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Grid, Vertical, Horizontal
from textual.widgets import Input, Footer, Header, Static, Markdown, Label
from textual.screen import ModalScreen

from .tools import search_jobs, save_to_csv, load_csv

class SearchScreen(ModalScreen):

    BINDINGS = [
        ("q", "leave_screen", "Leave screen"),
        ("escape", "unfocus_field", "Unfocus"),
        ("ctrl+enter", "submit_form", "Submit the form"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()
        with Vertical():

            with Vertical():
              yield Static("[bold yellow]Start searching for a job[/bold yellow]", id="search-title")
              yield Input(placeholder="Indeed search", type="text", id="main-query")

            with Horizontal():
                with Vertical():
                    yield Input(placeholder="Country", type="text", id="country-query")
                    yield Input(placeholder="Where in this country ? (Empty for whole country)", type="text", id="location-query")
                with Vertical():
                    yield Input(value = "168", placeholder="Max hours old ?", type="integer", id="time-query")
                    yield Input(value = "20", placeholder="How many results ? (max)", type="integer", id="max-results-query")

    @on(Input.Submitted)
    def next_focus(self) -> None:
        self.focus_next()

    def action_submit_form(self) -> None:
        val_list = []
        id_list = [
            "#main-query",
            "#country-query",
            "#location-query",
            "#time-query",
            "#max-results-query"
        ]

        for id in id_list:
            val = self.app.query_one(id).value
            val_list.append(val)

        self.dismiss(val_list)

    def action_unfocus_field(self) -> None:
        self.set_focus(None)

    def action_leave_screen(self) -> None:
        self.app.pop_screen()

class JobScreen(ModalScreen):
    BINDINGS = [("q", "leave_screen", "Pop screen")]

    def __init__(self, markdown_to_render: str) -> None:
        super().__init__()
        self.markdown_to_render = markdown_to_render

    def compose(self) -> ComposeResult:
        yield Grid(
            Markdown(self.markdown_to_render),
            id="dialog",
        )

    def action_leave_screen(self) -> None:
        self.app.pop_screen()

class Tuindeed(App):

    CSS_PATH = "base_screen.tcss"

    BINDINGS = [
        ("q", "exit", "Exit"),
        ("j", "go_down", "Down"),
        ("k", "go_up", "Up"),
        ("down", "go_down", "Down"),
        ("up", "go_up", "Up"),
        ("a", "read_description", "Open job description"),
        ("s", "new_search", "Make a new search"),
    ]

    # Global variables
    data_dir = os.path.join(os.environ["HOME"], ".local/share/tuindeed/jobs_descriptions")
    current_index = 0
    job_list = load_csv()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(
            Static(self.get_list("title"), id="title-list"),
        )

    def get_list(self, key: str) -> str:
        """Return the list of words with the current index highlighted."""
        return "\n".join(
            f"[bold yellow]{word}[/bold yellow]" if i == self.current_index else word
            for i, word in enumerate(self.job_list[key])
        )

    def get_markdown_to_render(self) -> str:
        job_id, job_title = self.job_list.loc[self.current_index, ["id", "title"]]
        filepath = os.path.join(self.data_dir, job_id+".md")

        with open(filepath, 'r') as f:
            text_core = f.read()
        text_title = f"# {job_title}\n\n"
        markdown_to_render = text_title + text_core

        return markdown_to_render

    def reset_index(self) -> None:
        self.current_index = 0
        self.query_one("#title-list", Static).update(self.get_list("title"))

    def action_go_down(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.job_list)
        self.query_one("#title-list", Static).update(self.get_list("title")) # update rendering

    def action_go_up(self) -> None:
        self.current_index = (self.current_index - 1) % len(self.job_list)
        self.query_one("#title-list", Static).update(self.get_list("title")) # update rendering

    def action_read_description(self) -> None:
        md = self.get_markdown_to_render()
        self.push_screen(JobScreen(md))

    def action_new_search(self) -> None:
        self.push_screen(SearchScreen(), self.process_new_search)

    def process_new_search(self, fields: list) -> None:
        new_job_list = search_jobs(fields)
        save_to_csv(new_job_list)
        self.job_list = load_csv()
        self.reset_index()

    def action_exit(self) -> None:
        self.exit()

    def action_test(self) -> None:
        self.mount(Label(self.job_list.loc["title"]))

if __name__ == "__main__" :
    app = Tuindeed()
    app.run()
