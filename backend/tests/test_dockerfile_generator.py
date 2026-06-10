from pathlib import Path

from deployment_engine.dockerfile_generator import image_tag_for_deployment, prepare_build_context


def test_prepare_build_context_writes_files(tmp_path: Path) -> None:
    model_file = tmp_path / "model.pkl"
    model_file.write_bytes(b"test")

    build_dir = tmp_path / "build"
    prepare_build_context(build_dir, str(model_file), "sklearn")

    assert (build_dir / "Dockerfile").exists()
    assert (build_dir / "server.py").exists()
    assert (build_dir / "model.file").exists()


def test_image_tag_for_deployment() -> None:
    assert image_tag_for_deployment("abc-123") == "ai-platform/deployment-abc-123:latest"
