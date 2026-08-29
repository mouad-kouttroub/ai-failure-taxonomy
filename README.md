# Trace Review — LLM Error-Analysis Tool

A minimal [Streamlit](https://streamlit.io/) tool for qualitative error analysis of
LLM / agent outputs. It supports the standard error-analysis workflow: **open-code**
each trace, **axial-code** failures into an editable taxonomy, view **per-category
counts**, and **export** the coded review.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run annotation_tool/trace_review.py
```

The app launches against synthetic seed traces in `annotation_tool/seeds/`.

## Workflow

1. **Open-code** — read each trace and note the first failure you observe.
2. **Axial-code** — tag failures into taxonomy categories; grow the taxonomy as new
   failure modes appear.
3. **Counts** — per-category failure counts, the output of axial coding.
4. **Export** — download the coded review (taxonomy + counts + notes) as JSON.

Annotations and any grown taxonomy persist atomically to a gitignored `state/`
directory, so an interrupted write can never corrupt saved work. Seed traces are
synthetic and data-agnostic — any JSON object with an `id` field is a valid trace.

## Layout

```
annotation_tool/
  trace_review.py   # Streamlit UI
  storage.py        # load/save + per-category counts (atomic writes)
  schema.py         # Trace / Annotation / Taxonomy dataclasses
  seeds/            # synthetic seed traces + starter taxonomy
```
