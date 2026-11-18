# Demo Video Creation - Installation Guide

This guide explains how to install and use VHS for creating demo videos.

## Quick Start

### 1. Install Demo Dependencies

Run the installation script to install VHS and its dependencies:

```bash
# macOS
bash scripts/install-demo-dependencies-macos.sh
```

This script will:

- ✅ Install VHS (terminal recorder)
- ✅ Install ttyd (required by VHS)
- ✅ Check/install ffmpeg
- ✅ Fix common libvpx/ffmpeg dependency issues
- ✅ Verify all tools are working

### 2. Create a Demo Video

```bash
# Activate virtual environment
source .venv/bin/activate

# Run VHS with a tape file
vhs docs/demos/tapes/get_full_metadata.tape
```

This will generate:

- `get_full_metadata_demo.gif` - Animated GIF

### Generated files and Git

- **`docs/demos/output/`** — GIFs/MP4s from tapes under `docs/demos/tapes/` are **not committed** (gitignored). Tracked sources are tapes and `sample.mp3`.

## Troubleshooting

### libvpx/ffmpeg Error

If you see an error like:

```
dyld: Library not loaded: /usr/local/opt/libvpx/lib/libvpx.11.dylib
```

**Fix:**

```bash
# Reinstall libvpx and ffmpeg
brew reinstall libvpx
brew reinstall ffmpeg

# Or run the installation script which handles this automatically
bash scripts/install-demo-dependencies-macos.sh
```

### ttyd Connection Refused

If you see:

```
could not open ttyd: navigation failed: net::ERR_CONNECTION_REFUSED
```

**Fix:**

```bash
# Install ttyd
brew install ttyd

# Or run the installation script
bash scripts/install-demo-dependencies-macos.sh
```

### VHS Not Found

If you see:

```
vhs: command not found
```

**Fix:**

```bash
# Install VHS
brew tap charmbracelet/tap
brew install charmbracelet/tap/vhs

# Or run the installation script
bash scripts/install-demo-dependencies-macos.sh
```

## Available Tape Files

The repository includes pre-made tape files in the root directory:

1. **audiometa_demo.tape** - Interactive Python REPL demo
2. **audiometa_demo_script.tape** - Script execution demo

### Creating New Tape Files

See `VHS_DEMO_README.md` for detailed instructions on creating custom tape files.

## Verifying Installation

After running the installation script, verify everything works:

```bash
# Check VHS version
vhs --version

# Check ttyd is installed
ttyd --version

# Check ffmpeg works
ffmpeg -version

# Test VHS (quick test)
echo "Output test.gif
Type 'echo Hello, World!'" | vhs /dev/stdin
```

## Next Steps

1. ✅ Install dependencies (done with installation script)
2. ✅ Verify installation (run tests above)
3. Create demo videos with existing tape files
4. Customize tape files for your needs

## Links

- [VHS Documentation](https://github.com/charmbracelet/vhs)
- [VHS Examples](https://github.com/charmbracelet/vhs/tree/main/examples)
- [Creating Tape Files](VHS_DEMO_README.md)
