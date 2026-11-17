# `test_check_doc_links.py` -- Tests for the IDs the link script derives
# =====================================================================
#
# `scripts/check_doc_links.py` is run by hand against a clone of the Git
# source, as "Maintenance script" in the specification describes. These tests
# check only how it finds the IDs in the lines of a page, which needs neither
# a clone nor the network. The lines come from Git's `MyFirstContribution`,
# whose IDs the live page confirms.
import importlib.util
from pathlib import Path

# The script is not part of a package, so it is loaded from its path.
SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "check_doc_links.py"
)
_spec = importlib.util.spec_from_file_location("check_doc_links", SCRIPT)
assert _spec is not None and _spec.loader is not None
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


# A link macro in a title is rendered as its text, whose `#` the derivation
# deletes.
def test_link_macro_in_title() -> None:
    lines = [
        "==== https://web.libera.chat/#git-devel[#git-devel] on Libera Chat",
        "==== https://discord.gg/GRFVkzgxRd[#discord] on Discord",
    ]
    assert script.collect_ids(lines) == [
        "_git_devel_on_libera_chat",
        "_discord_on_discord",
    ]


# Text in a passthrough is output as written, so `[[dco]]` in one is no anchor.
def test_anchor_in_passthrough() -> None:
    line = "`Documentation/SubmittingPatches` +++[[dco]]+++ header)."
    assert script.collect_ids([line]) == []
