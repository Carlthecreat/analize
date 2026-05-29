# Analize v0.1

A lightweight command-line Apache log analyzer built with Python and Polars.

Analize loads Apache access logs into a Polars DataFrame and provides an interactive shell for querying, summarizing, and exploring traffic data directly from the terminal.

---

# Overview

Analize is designed for fast, interactive Apache log analysis.

It supports both Apache Common and Combined log formats and provides built-in commands for traffic analysis alongside direct Polars querying.

The project focuses on:

* Fast parsing
* Efficient dataframe operations
* Interactive terminal workflows
* Simplicity and extensibility

---

# Features

* Support for Apache Common and Combined logs
* Interactive command shell
* Traffic summaries and request statistics
* Sorting and filtering tools
* Frequency analysis for columns
* Native Polars query support
* Restricted Free Mode for quick Python evaluation

Example commands:

```bash id="rnlfbx"
load access.log combined
head
sort bytes
count status_code 404
highest ip
summarize
```

---

# Polars vs NumPy

This project uses Polars because log analysis is dataframe-oriented rather than purely numerical.

Polars provides:

* Fast dataframe operations
* Efficient memory usage
* Strong datetime handling
* Powerful grouping and aggregation
* Parallel execution

NumPy is excellent for numerical computing, but Polars is better suited for structured log data containing timestamps, strings, and categorical values.

---

# Installation

Clone the repository:

```bash id="s1uk0n"
git clone <repository-url>
cd analize
```

Install dependencies:

```bash id="b8xg9n"
pip install polars apachelogs rich
```

---

# Usage

Start the shell:

```bash id="twvty7"
python analyzer.py
```

Load a log file:

```bash id="2f9t0q"
load access.log combined
```

Run commands:

```bash id="3f2v5w"
head
tail
summarize
query pl.col("bytes").mean()
```

---

# Next Stages

Planned improvements include:

* Real-time log streaming
* Advanced filtering
* Visualization support
* Exporting results
* Security-focused detection features
* Plugin support

---

# License

MIT License.
