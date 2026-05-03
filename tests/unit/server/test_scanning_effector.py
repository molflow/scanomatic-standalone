import os

from scanomatic.io.jsonizer import dumps
from scanomatic.models.factories.rpc_job_factory import RPC_Job_Model_Factory
from scanomatic.models.factories.scanning_factory import ScanningModelFactory
from scanomatic.models.scanning_model import SCAN_STEP
from scanomatic.server.scanning_effector import ScannerEffector


class _FakeSaneBase:
    def __init__(self, scan_mode, model):
        self.scan_mode = scan_mode
        self.model = model

    @staticmethod
    def get_scan_program():
        return "fake-scan"

    @staticmethod
    def get_program_version():
        return "0.0"

    def get_scan_instructions_as_tuple(self):
        return ("--dpi", "600")


class _FakeRPCClient:
    def __init__(self, compile_job_id="compile-job"):
        self.compile_job_id = compile_job_id
        self.payloads = []

    def create_compile_project_job(self, payload):
        self.payloads.append(payload)
        return self.compile_job_id


def _make_scan_job(tmp_path, pinning_formats):
    scan_model = ScanningModelFactory.create(
        project_name="pinning-regression",
        directory_containing_project=str(tmp_path),
        fixture="fixture-1",
        scanner=1,
        scanner_hardware="EPSON V800",
        pinning_formats=pinning_formats,
        number_of_scans=2,
    )
    return RPC_Job_Model_Factory.create(id="scan-job", content_model=scan_model)


def test_setup_copies_scan_pinning_formats_to_compile_model(tmp_path, monkeypatch):
    fake_rpc_client = _FakeRPCClient()
    monkeypatch.setattr(
        "scanomatic.server.scanning_effector.rpc_client.get_client",
        lambda: fake_rpc_client,
    )
    monkeypatch.setattr(
        "scanomatic.server.scanning_effector.sane.SaneBase",
        _FakeSaneBase,
    )

    pinning_formats = ((8, 12), (16, 24), None)
    job = _make_scan_job(tmp_path, pinning_formats)
    effector = ScannerEffector(job)

    effector.setup(dumps(job))

    assert (
        effector._scanning_effector_data.compile_project_model
        .overwrite_pinning_matrices
        == pinning_formats
    )


def test_compile_request_payload_contains_scan_pinning_formats(
    tmp_path,
    monkeypatch,
):
    fake_rpc_client = _FakeRPCClient(compile_job_id="compile-123")
    monkeypatch.setattr(
        "scanomatic.server.scanning_effector.rpc_client.get_client",
        lambda: fake_rpc_client,
    )
    monkeypatch.setattr(
        "scanomatic.server.scanning_effector.sane.SaneBase",
        _FakeSaneBase,
    )

    pinning_formats = ((8, 12), None, (32, 48))
    job = _make_scan_job(tmp_path, pinning_formats)
    effector = ScannerEffector(job)

    effector.setup(dumps(job))
    effector._scanning_effector_data.current_image = 0

    step = effector._do_request_project_compilation()

    assert step == SCAN_STEP.NextMajor
    assert len(fake_rpc_client.payloads) == 1
    assert (
        fake_rpc_client.payloads[0]["overwrite_pinning_matrices"]
        == pinning_formats
    )
    assert (
        effector._scanning_effector_data.compile_project_model.start_condition
        == "compile-123"
    )
    assert os.path.isdir(tmp_path / "pinning-regression")
