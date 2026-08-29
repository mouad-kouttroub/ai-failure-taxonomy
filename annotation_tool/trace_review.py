"""Annotation / trace-review tool - minimal Streamlit skeleton.

The scaffold runs on first launch against synthetic seed traces; the core
error-analysis logic (tagging, per-category counts, export) is left as
clearly-marked TODOs to implement.

Run:  streamlit run annotation_tool/trace_review.py

Workflow: open-code each trace, axial-code into a failure taxonomy,
per-category counts, iterate to saturation, export.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `streamlit run annotation_tool/trace_review.py` to import the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from annotation_tool import storage  # noqa: E402
from annotation_tool.schema import Annotation  # noqa: E402

st.set_page_config(page_title="Trace Review \u2014 error analysis", layout="wide")


# --------------------------------------------------------------------------- #
# Session state bootstrap \u2014 DONE (so the app runs on first launch)
# --------------------------------------------------------------------------- #
def _bootstrap():
    if "traces" not in st.session_state:
        st.session_state.traces = storage.load_traces()
    if "taxonomy" not in st.session_state:
        st.session_state.taxonomy = storage.load_taxonomy()
    if "annotations" not in st.session_state:
        st.session_state.annotations = storage.load_annotations()
    if "idx" not in st.session_state:
        st.session_state.idx = 0


def _current_annotation(trace_id: str) -> Annotation:
    ann = st.session_state.annotations.get(trace_id)
    if ann is None:
        ann = Annotation(trace_id=trace_id)
        st.session_state.annotations[trace_id] = ann
    return ann


# --------------------------------------------------------------------------- #
# Trace rendering \u2014 DONE (data-agnostic: renders known fields, dumps the rest)
# --------------------------------------------------------------------------- #
def render_trace(trace):
    st.subheader(f"Trace: {trace.id}")
    if trace.get("prompt") is not None:
        st.markdown("**Prompt**")
        st.info(trace.get("prompt"))
    if trace.get("response") is not None:
        st.markdown("**Response**")
        st.warning(trace.get("response"))
    if trace.get("tool_calls"):
        st.markdown("**Tool calls**")
        st.json(trace.get("tool_calls"))
    if trace.get("retrieval"):
        st.markdown("**Retrieval**")
        st.json(trace.get("retrieval"))
    other = trace.other_fields()
    if other:
        with st.expander("Other fields (raw)"):
            st.json(other)


def main():
    _bootstrap()
    traces = st.session_state.traces
    n = len(traces)

    st.title("Trace Review \u2014 error analysis workbench")
    st.caption(
        "Open-code each trace \u2192 axial-code into a failure taxonomy \u2192 counts \u2192 saturation. "
        "SKELETON: the tagging/counts/export logic is TODO \u2014 see the TODO notes."
    )

    if n == 0:
        st.error("No traces loaded. Drop a traces.json into annotation_tool/seeds/.")
        return

    # ---- Navigation (DONE) ----
    col_prev, col_prog, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("\u2190 Prev", disabled=st.session_state.idx <= 0):
            st.session_state.idx -= 1
    with col_next:
        if st.button("Next \u2192", disabled=st.session_state.idx >= n - 1):
            st.session_state.idx += 1
    # Clamp index into valid range: st.progress needs [0,1] and traces[idx] needs a
    # valid index; button `disabled` is computed pre-rerun, so idx can overrun n-1.
    st.session_state.idx = max(0, min(st.session_state.idx, n - 1))
    with col_prog:
        coded = sum(1 for a in st.session_state.annotations.values() if a.note or a.tags)
        st.progress((st.session_state.idx + 1) / n, text=f"Trace {st.session_state.idx + 1} of {n} \u00b7 {coded} coded")

    trace = traces[st.session_state.idx]
    left, right = st.columns([2, 1])

    with left:
        render_trace(trace)

    with right:
        ann = _current_annotation(trace.id)

        # ---- Open-coding note field (DONE for the note itself) ----
        st.markdown("### Open-coding note")
        ann.note = st.text_area(
            "First failure you observe (journal it):",
            value=ann.note,
            height=120,
            key=f"note_{trace.id}",
        )

        # ---- Failure-taxonomy tagging (TODO) ----
        st.markdown("### Failure-taxonomy tags")
        ann.tags = st.multiselect(
              "Assign categories (grow the taxonomy in the sidebar):",
              options=st.session_state.taxonomy.names(),
              default=ann.tags,
              key=f"tags_{trace.id}",
              )

        if st.button("Save annotation"):
            storage.save_annotations(st.session_state.annotations)
            st.success("Saved.")

    # ---- Sidebar: taxonomy editor + counts (partly TODO) ----
    with st.sidebar:
        st.header("Failure taxonomy")
        new_cat = st.text_input("Add a category (axial coding):")
        if st.button("Add category") and new_cat:
              st.session_state.taxonomy.add(new_cat)
              storage.save_taxonomy(st.session_state.taxonomy)
              st.success(f"Added category: {new_cat}")

        st.subheader("Per-category counts")
        counts = storage.category_counts(st.session_state.annotations, st.session_state.taxonomy)
        st.bar_chart(counts)

        st.subheader("Export")
        review_str = storage.export_review(st.session_state.annotations, st.session_state.taxonomy)
        st.download_button(
            "Export review",
            data=review_str,
            file_name="trace_review_export.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
else:
    # Streamlit executes the module top-to-bottom; call main() on import too.
    main()
