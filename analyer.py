from parser import parse_log
import polars as pl
import shlex
import cmd
from rich import print


class Analyzer(cmd.Cmd):
    intro = "Analize v0.1\nCreated by Chimdiebube Okonkwo"
    prompt = "analize>> "

    VALID_LOG_FORMATS = ["common", "combined"]

    def __init__(self):
        super().__init__()

        self.df: pl.DataFrame = None
        self.free_mode = False

        # Restricted execution environment for free mode
        self.env = {
            "__builtins__": {
                "print": print,
                "len": len,
            },
            "get_df": lambda: self.df,
        }

    # -------------------------
    # Helper methods
    # -------------------------

    def _require_df(self):
        """Ensure a dataframe is loaded before running commands."""
        if self.df is None:
            print("No dataframe loaded")
            return False

        return True

    def _parse_args(self, arg, expected=None):
        """
        Parse arguments using shlex.

        expected:
            None -> Any number of arguments allowed
            int  -> Exact number of arguments required
        """
        args = shlex.split(arg)

        if not args:
            print("No argument provided")
            return None

        if expected is not None and len(args) != expected:
            print(f"Expected {expected} argument(s)")
            return None

        return args

    def _validate_column(self, col):
        """Validate dataframe column."""
        if col not in self.df.columns:
            print("Invalid column id")
            return False

        return True

    # -------------------------
    # Core behavior
    # -------------------------

    def default(self, line):
        """Fallback when command is not recognized."""

        if not self.free_mode:
            print("---Unknown syntax:", line)
            return

        try:
            # Evaluate expressions first
            result = eval(line, self.env, self.env)

            if result is not None:
                print(result)

        except SyntaxError:
            # If not an expression, treat as statement
            try:
                exec(line, self.env, self.env)

            except Exception as e:
                print(f"Execution error: {e}")

        except Exception as e:
            print(f"Evaluation error: {e}")

    # -------------------------
    # Commands
    # -------------------------

    def do_load(self, arg):
        """Load a log file into a Polars DataFrame."""

        args = self._parse_args(arg, expected=2)

        if args is None:
            return

        path, log_format = args

        if log_format not in self.VALID_LOG_FORMATS:
            print("Invalid apache log format")
            return

        try:
            data = parse_log(path, log_format)
            self.df = pl.DataFrame(data)

            print("Log loaded into dataframe")

        except Exception as e:
            print(f"Load error: {e}")

    def do_free_mode(self, arg):
        """Toggle Free Mode."""

        self.free_mode = not self.free_mode

        self.prompt = "F>> " if self.free_mode else "analize>> "

        state = "activated" if self.free_mode else "deactivated"

        print(f"Free mode {state}")

    def do_query(self, arg):
        """Execute a Polars select query."""

        if not self._require_df():
            return

        if not arg:
            print("No argument provided")
            return

        try:
            result = self.df.select(
                eval(arg, {"pl": pl})
            )

            print(result)

        except Exception as e:
            print(f"Query error: {e}")

    def do_summarize(self, arg):
        """Summarize dataframe traffic patterns."""

        if not self._require_df():
            return

        try:
            hours = int(arg) if arg else 4

            count_time_df = (
                self.df
                .group_by(
                    pl.col("time").dt.truncate(f"{hours}h")
                )
                .agg(
                    pl.len().alias("count")
                )
                .sort("time")
            )

            print(
                "[underline bold dark_orange]"
                "Traffic Count"
                "[/underline bold dark_orange]"
            )

            print(count_time_df)

            highest_df = (
                self.df
                .sort("bytes", descending=True)
                .unique(
                    subset="ip",
                    keep="first",
                    maintain_order=True
                )
                .head(5)
            )

            print(
                "\n[underline bold dark_orange]"
                "Highest Request IPs"
                "[/underline bold dark_orange]"
            )

            for row in highest_df.iter_rows(named=True):

                num_requests = (
                    self.df
                    .filter(pl.col("ip") == row["ip"])
                    .height
                )

                print(
                    f"[bold red]IP:[/bold red] {row['ip']} | "
                    f"[bold red]Largest Request Size:[/bold red] {row['bytes']} | "
                    f"[bold red]Time:[/bold red] {row['time']} | "
                    f"[bold red]No. Requests:[/bold red] {num_requests}"
                )

        except ValueError:
            print("Hour value must be a number")

    def do_head(self, arg):
        """Display the first N rows of the dataframe."""

        if not self._require_df():
            return

        try:
            rows = int(arg) if arg else 4

            print(self.df.head(rows))

        except ValueError:
            print("Row count must be an integer")

    def do_tail(self, arg):
        """Display the last N rows of the dataframe."""

        if not self._require_df():
            return

        try:
            rows = int(arg) if arg else 4

            print(self.df.tail(rows))

        except ValueError:
            print("Row count must be an integer")

    def do_sort(self, arg):
        """Sort dataframe by column."""

        if not self._require_df():
            return

        args = self._parse_args(arg, expected=1)

        if args is None:
            return

        col = args[0]

        if not self._validate_column(col):
            return

        print(
            self.df.sort(
                pl.col(col),
                descending=True
            )
        )

    def do_count(self, arg):
        """Count occurrences of a value in a column."""

        if not self._require_df():
            return

        args = self._parse_args(arg, expected=2)

        if args is None:
            return

        col, value = args

        if not self._validate_column(col):
            return

        try:
            amount = (
                self.df
                .select(
                    (pl.col(col) == value).sum()
                )
                .item()
            )

            if amount > 0:
                print(f"Value: {value}, Count: {amount}")
            else:
                print("Not found")

        except Exception as e:
            print(f"Count error: {e}")

    def do_highest(self, arg):
        """Show the most frequent value in a column."""

        if not self._require_df():
            return

        args = self._parse_args(arg, expected=1)

        if args is None:
            return

        col = args[0]

        if not self._validate_column(col):
            return

        print(
            self.df.select(
                pl.col(col).mode()
            )
        )

    def do_highest_list(self, arg):
        """Show sorted value counts for a column."""

        if not self._require_df():
            return

        args = self._parse_args(arg, expected=1)

        if args is None:
            return

        col = args[0]

        if not self._validate_column(col):
            return

        print(
            self.df.select(
                pl.col(col).value_counts(sort=True)
            )
        )

    def do_exit(self, arg):
        """Exit the shell."""
        return True


if __name__ == "__main__":
    Analyzer().cmdloop()