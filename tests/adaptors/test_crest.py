import pytest
import qccodec
from qccodec.models import NativeInput
from qcdata import SinglePointData

from qccompute.adapters.crest import CRESTAdapter
from qccompute.exceptions import ExternalProgramError


def test_crest_parser_error_preserves_partial_data(
    monkeypatch, prog_input_factory, tmp_path
):
    monkeypatch.chdir(tmp_path)
    partial_data = SinglePointData(extras={"program_version": "3.0.2"})

    def raise_parser_error(*args, **kwargs):
        raise qccodec.exceptions.ParserError(
            "Missing required output artifact(s): crest.engrad",
            data=partial_data,
        )

    monkeypatch.setattr(
        qccodec,
        "encode",
        lambda *args, **kwargs: NativeInput(
            input_file="",
            geometry_file="",
            geometry_filename="structure.xyz",
        ),
    )
    monkeypatch.setattr(
        "qccompute.adapters.crest.execute_subprocess",
        lambda *args, **kwargs: "Version 3.0.2, test stdout",
    )
    monkeypatch.setattr(qccodec, "decode", raise_parser_error)

    with pytest.raises(ExternalProgramError) as exc_info:
        CRESTAdapter().compute_data(prog_input_factory("gradient"))

    assert exc_info.value.data is partial_data
