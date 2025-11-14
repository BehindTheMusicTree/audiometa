"""Test configuration for audiometa-python tests."""

import platform
import subprocess
import tomllib
from pathlib import Path

import pytest


def _load_dependencies_pinned_versions():
    """Load pinned versions from system-dependencies.toml."""
    config_path = Path(__file__).parent.parent.parent.parent / "system-dependencies.toml"

    if not config_path.exists():
        return None

    try:
        with config_path.open("rb") as f:
            config = tomllib.load(f)

        pinned_versions = {}

        # Extract versions for each OS
        for os_type in ["ubuntu", "macos", "windows"]:
            if os_type not in config:
                continue

            os_config = config[os_type]
            for tool in ["ffmpeg", "flac", "mediainfo", "id3v2", "bwfmetaedit"]:
                if tool not in os_config:
                    continue

                version_value = os_config[tool]
                # Handle both string values and dict values (for bwfmetaedit)
                if isinstance(version_value, str):
                    version = version_value
                elif isinstance(version_value, dict) and "pinned_version" in version_value:
                    version = version_value["pinned_version"]
                else:
                    continue

                if tool not in pinned_versions:
                    pinned_versions[tool] = {}
                pinned_versions[tool][os_type] = version
    except Exception:
        return None
    else:
        return pinned_versions


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Verify system dependency versions match pinned versions before running tests."""
    # Load pinned versions from system-dependencies.toml (single source of truth)
    pinned_versions = _load_dependencies_pinned_versions()

    if not pinned_versions:
        # Skip verification if config file not found or can't be parsed
        return

    def get_os_type():
        """Detect OS type for version checking."""
        system = platform.system().lower()
        if system == "linux":
            return "ubuntu"
        if system == "darwin":
            return "macos"
        if system == "windows":
            return "windows"
        return None

    def get_installed_version_ubuntu(package):
        """Get installed package version on Ubuntu."""
        try:
            result = subprocess.run(["dpkg", "-l"], capture_output=True, text=True, check=True)
            for line in result.stdout.split("\n"):
                if line.startswith("ii") and package in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def get_installed_version_macos(package):
        """Get installed package version on macOS."""
        try:
            result = subprocess.run(
                ["brew", "list", "--versions", package],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                version = result.stdout.strip().split()[-1]
                # Normalize version: extract major.minor from "7.1_4" -> "7.1"
                # Homebrew version pinning uses major versions (e.g., @7) but installed versions include revisions
                if "_" in version:
                    version = version.split("_")[0]
                return version
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def get_installed_version_windows(package):
        """Get installed package version on Windows."""
        try:
            result = subprocess.run(
                ["choco", "list", "--local-only", package, "--exact"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.split("\n"):
                if package in line and not line.startswith("Chocolatey"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def check_tool_available(tool_name):
        """Check if tool is available in PATH."""
        try:
            # Some tools (like ffprobe) output version to stderr and return non-zero
            # So we check both stdout and stderr, and don't require check=True
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            # Tool is available if we get output in either stdout or stderr
            return bool(result.stdout or result.stderr)
        except FileNotFoundError:
            return False

    # Only verify versions if we can detect the OS and tools are available
    os_type = get_os_type()
    if not os_type:
        return  # Skip verification if OS not detected

    has_errors = False
    errors = []

    for tool, versions in pinned_versions.items():
        expected_version = versions.get(os_type)
        if not expected_version:
            continue

        # Check if tool is available
        tool_command = "ffprobe" if tool == "ffmpeg" else tool
        if not check_tool_available(tool_command):
            errors.append(f"{tool}: NOT INSTALLED")
            has_errors = True
            continue

        # Get installed version
        if os_type == "ubuntu":
            installed = get_installed_version_ubuntu(tool)
        elif os_type == "macos":
            # mediainfo is called media-info in Homebrew
            brew_package = "media-info" if tool == "mediainfo" else tool
            installed = get_installed_version_macos(brew_package)
        else:  # windows
            installed = get_installed_version_windows(tool)

        if not installed:
            errors.append(f"{tool}: VERSION CHECK FAILED")
            has_errors = True
        elif os_type == "macos":
            # For macOS, only ffmpeg supports version pinning via @version syntax
            # Other packages (flac, mediainfo, id3v2, bwfmetaedit) don't support version pinning
            # and install the latest available version, so we skip strict version checking for them
            if tool == "ffmpeg":
                # For ffmpeg, compare major versions since Homebrew pins by major version
                # e.g., expected "7" should match installed "7.1" or "7.1_4"
                installed_major = installed.split(".")[0] if "." in installed else installed
                expected_major = expected_version.split(".")[0] if "." in expected_version else expected_version
                if installed_major != expected_major:
                    errors.append(
                        f"{tool}: version mismatch (expected major version {expected_major}, got {installed})"
                    )
                    has_errors = True
            # For other packages, skip version checking since Homebrew doesn't support version pinning
        elif os_type == "ubuntu" and tool == "bwfmetaedit":
            # For bwfmetaedit on Ubuntu, normalize deb package version by stripping revision suffix
            # Expected: "25.04.1" (from pinned_version), Installed: "25.04.1-1" (deb package format)
            # Strip deb revision suffix (e.g., "-1", "-2") before comparison
            installed_normalized = installed.split("-")[0] if "-" in installed else installed
            if installed_normalized != expected_version:
                errors.append(f"{tool}: version mismatch (expected {expected_version}, got {installed})")
                has_errors = True
        elif installed != expected_version:
            errors.append(f"{tool}: version mismatch (expected {expected_version}, got {installed})")
            has_errors = True

    if has_errors:
        error_msg = "System dependency version verification failed:\n" + "\n".join(f"  - {e}" for e in errors)
        error_msg += (
            "\n\nUpdate system-dependencies.toml and scripts/install-system-dependencies-*.sh with correct versions."
        )
        error_msg += "\nThis ensures tests use the same tool versions as CI."
        pytest.exit(error_msg, returncode=1)


def pytest_collection_modifyitems(items):
    """Reorder test items to ensure proper execution order: unit → integration → e2e."""
    # Define the desired test execution order based on directory structure
    test_order = {"unit": 1, "integration": 2, "e2e": 3}

    def get_test_priority(item):
        """Get the priority order for a test item based on its path."""
        test_path = str(item.fspath)

        # Check for unit tests
        if "/unit/" in test_path:
            return test_order["unit"]
        # Check for integration tests
        if "/integration/" in test_path:
            return test_order["integration"]
        # Check for e2e tests
        if "/e2e/" in test_path:
            return test_order["e2e"]
        # Default priority for other tests (comprehensive, etc.)
        return 0  # Run first (before unit tests)

    # Sort items by priority
    items.sort(key=get_test_priority)


@pytest.fixture
def assets_dir() -> Path:
    return Path(__file__).parent.parent.parent / "test" / "assets"


@pytest.fixture
def sample_mp3_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.mp3"


@pytest.fixture
def sample_flac_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.flac"


@pytest.fixture
def sample_wav_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.wav"


@pytest.fixture
def sample_m4a_file(assets_dir: Path) -> Path:
    return assets_dir / "sample.m4a"


@pytest.fixture
def metadata_id3v1_big_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_big.mp3"


@pytest.fixture
def metadata_id3v1_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_small.flac"


@pytest.fixture
def metadata_id3v1_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_big.flac"


@pytest.fixture
def metadata_id3v1_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_small.wav"


@pytest.fixture
def metadata_id3v1_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v1_big.wav"


@pytest.fixture
def metadata_id3v2_small_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_small.mp3"


@pytest.fixture
def metadata_id3v2_big_mp3(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_big.mp3"


@pytest.fixture
def metadata_id3v2_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_small.flac"


@pytest.fixture
def metadata_id3v2_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_big.flac"


@pytest.fixture
def metadata_id3v2_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_small.wav"


@pytest.fixture
def metadata_id3v2_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_big.wav"


@pytest.fixture
def metadata_id3v2_and_riff_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_id3v2_and_riff_small.wav"


@pytest.fixture
def metadata_riff_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_riff_small.wav"


@pytest.fixture
def metadata_riff_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_riff_big.wav"


@pytest.fixture
def metadata_vorbis_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_vorbis_small.flac"


@pytest.fixture
def metadata_vorbis_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "metadata=long a_vorbis_big.flac"


@pytest.fixture
def artists_one_two_three_comma_id3v2(assets_dir: Path) -> Path:
    return assets_dir / "artists=One Two Three_comma_id3v2.mp3"


@pytest.fixture
def artists_one_two_three_semicolon_id3v2(assets_dir: Path) -> Path:
    return assets_dir / "artists=One Two Three_semicolon_id3v2.mp3"


@pytest.fixture
def artists_one_two_three_multi_tags_vorbis(assets_dir: Path) -> Path:
    return assets_dir / "artists=One Two Three_muti tags_vorbis.flac"


@pytest.fixture
def album_koko_id3v2_mp3(assets_dir: Path) -> Path:
    return assets_dir / "album=koko_id3v2.mp3"


@pytest.fixture
def album_koko_id3v2_wav(assets_dir: Path) -> Path:
    return assets_dir / "album=koko_id3v2.wav"


@pytest.fixture
def album_koko_vorbis_flac(assets_dir: Path) -> Path:
    return assets_dir / "album=koko_vorbis.flac"


@pytest.fixture
def genre_code_id3v1_abstract_mp3(assets_dir: Path) -> Path:
    return assets_dir / "genre_code_id3v1=Abstract.mp3"


@pytest.fixture
def genre_code_id3v1_unknown_mp3(assets_dir: Path) -> Path:
    return assets_dir / "genre_code_id3v1=Unknown.mp3"


@pytest.fixture
def duration_1s_mp3(assets_dir: Path) -> Path:
    return assets_dir / "duration=1s.wav"


@pytest.fixture
def duration_182s_mp3(assets_dir: Path) -> Path:
    return assets_dir / "duration=182.mp3"


@pytest.fixture
def duration_335s_flac(assets_dir: Path) -> Path:
    return assets_dir / "duration=335s.flac"


@pytest.fixture
def duration_472s_wav(assets_dir: Path) -> Path:
    return assets_dir / "duration=472s.wav"


@pytest.fixture
def bitrate_320_mp3(assets_dir: Path) -> Path:
    return assets_dir / "bitrate in kbps_big=320.mp3"


@pytest.fixture
def bitrate_946_flac(assets_dir: Path) -> Path:
    return assets_dir / "bitrate in kbps_big=946.flac"


@pytest.fixture
def bitrate_1411_wav(assets_dir: Path) -> Path:
    return assets_dir / "bitrate in kbps_big=1411.wav"


@pytest.fixture
def size_small_mp3(assets_dir: Path) -> Path:
    return assets_dir / "size_small=0.01mo.mp3"


@pytest.fixture
def size_big_mp3(assets_dir: Path) -> Path:
    return assets_dir / "size_big=9.98mo.mp3"


@pytest.fixture
def size_small_flac(assets_dir: Path) -> Path:
    return assets_dir / "size_small=0.05mo.flac"


@pytest.fixture
def size_big_flac(assets_dir: Path) -> Path:
    return assets_dir / "size_big=26.6mo.flac"


@pytest.fixture
def size_small_wav(assets_dir: Path) -> Path:
    return assets_dir / "size_small=0.08mo.wav"


@pytest.fixture
def size_big_wav(assets_dir: Path) -> Path:
    return assets_dir / "size_big=79.55mo.wav"
