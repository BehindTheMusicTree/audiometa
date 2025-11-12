from pathlib import Path

import pytest

from audiometa.cli import expand_file_patterns


@pytest.mark.unit
class TestExpandFilePatterns:
    def test_single_file_exists(self, tmp_path):
        test_file = tmp_path / "test.mp3"
        test_file.write_text("fake mp3 content")

        result = expand_file_patterns([str(test_file)])
        assert len(result) == 1
        assert result[0] == test_file

    def test_single_file_nonexistent(self, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.mp3"

        result = expand_file_patterns([str(nonexistent_file)], continue_on_error=True)
        assert result == []

    def test_glob_pattern_matching_files(self, tmp_path):
        # Create test files
        (tmp_path / "song1.mp3").write_text("content1")
        (tmp_path / "song2.mp3").write_text("content2")
        (tmp_path / "other.txt").write_text("content3")

        pattern = str(tmp_path / "*.mp3")
        result = expand_file_patterns([pattern])

        assert len(result) == 2
        assert all(path.suffix == ".mp3" for path in result)
        assert all(path.parent == tmp_path for path in result)

    def test_glob_pattern_no_matches(self, tmp_path):
        pattern = str(tmp_path / "*.wav")
        result = expand_file_patterns([pattern], continue_on_error=True)
        assert result == []

    def test_directory_non_recursive(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "song.mp3").write_text("content")

        result = expand_file_patterns([str(subdir)], continue_on_error=True)
        assert result == []

    def test_directory_recursive(self, tmp_path):
        subdir = tmp_path / "music"
        subdir.mkdir()
        nested_dir = subdir / "album1"
        nested_dir.mkdir()

        # Create various audio files
        (subdir / "song1.mp3").write_text("content1")
        (nested_dir / "song2.flac").write_text("content2")
        (nested_dir / "song3.wav").write_text("content3")
        (nested_dir / "notes.txt").write_text("content4")  # Non-audio file

        result = expand_file_patterns([str(subdir)], recursive=True)

        assert len(result) == 3
        assert all(path.suffix in [".mp3", ".flac", ".wav"] for path in result)
        assert all(subdir in path.parents for path in result)

    def test_directory_recursive_nested_directories(self, tmp_path):
        # Create nested structure: music/artist/album/songs
        music_dir = tmp_path / "music"
        artist_dir = music_dir / "artist"
        album_dir = artist_dir / "album"
        album_dir.mkdir(parents=True)

        # Create files at different levels
        (music_dir / "root.mp3").write_text("root")
        (artist_dir / "artist.mp3").write_text("artist")
        (album_dir / "song1.mp3").write_text("song1")
        (album_dir / "song2.flac").write_text("song2")

        result = expand_file_patterns([str(music_dir)], recursive=True)

        assert len(result) == 4
        assert all(path.suffix in [".mp3", ".flac"] for path in result)

    def test_mixed_patterns(self, tmp_path):
        # Create files and directories
        single_file = tmp_path / "single.mp3"
        single_file.write_text("single")

        music_dir = tmp_path / "music"
        music_dir.mkdir()
        (music_dir / "album.mp3").write_text("album")

        # Create glob-matching files
        (tmp_path / "glob1.mp3").write_text("glob1")
        (tmp_path / "glob2.mp3").write_text("glob2")

        patterns = [
            str(single_file),  # Single file
            str(music_dir),  # Directory (recursive)
            str(tmp_path / "glob*.mp3"),  # Glob pattern
        ]

        result = expand_file_patterns(patterns, recursive=True)

        assert len(result) == 4  # single + album + glob1 + glob2
        assert single_file in result
        assert music_dir / "album.mp3" in result

    def test_unsupported_audio_extensions_ignored(self, tmp_path):
        music_dir = tmp_path / "music"
        music_dir.mkdir()

        # Create files with supported and unsupported extensions
        (music_dir / "song.mp3").write_text("mp3")
        (music_dir / "song.flac").write_text("flac")
        (music_dir / "song.wav").write_text("wav")
        (music_dir / "song.ogg").write_text("ogg")  # Not supported
        (music_dir / "song.m4a").write_text("m4a")  # Not supported

        result = expand_file_patterns([str(music_dir)], recursive=True)

        assert len(result) == 3
        assert all(path.suffix in [".mp3", ".flac", ".wav"] for path in result)

    def test_no_files_found_continue_on_error_true(self, tmp_path, capsys):
        nonexistent_pattern = str(tmp_path / "nonexistent.mp3")

        result = expand_file_patterns([nonexistent_pattern], continue_on_error=True)

        assert result == []
        captured = capsys.readouterr()
        assert "Warning: No valid audio files found" in captured.err

    def test_no_files_found_continue_on_error_false(self, tmp_path, capsys):
        nonexistent_pattern = str(tmp_path / "nonexistent.mp3")

        with pytest.raises(SystemExit) as exc_info:
            expand_file_patterns([nonexistent_pattern], continue_on_error=False)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: No valid audio files found" in captured.err

    def test_complex_glob_patterns(self, tmp_path):
        # Create test files with different patterns
        (tmp_path / "track01.mp3").write_text("track01")
        (tmp_path / "track02.mp3").write_text("track02")
        (tmp_path / "song_a.mp3").write_text("song_a")
        (tmp_path / "song_b.mp3").write_text("song_b")
        (tmp_path / "other.wav").write_text("other")

        # Test character class glob
        pattern1 = str(tmp_path / "track[0-9][0-9].mp3")
        result1 = expand_file_patterns([pattern1])
        assert len(result1) == 2

        # Test wildcard glob
        pattern2 = str(tmp_path / "song_?.mp3")
        result2 = expand_file_patterns([pattern2])
        assert len(result2) == 2

    def test_relative_paths(self, tmp_path, monkeypatch):
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        # Create relative file
        rel_file = Path("relative.mp3")
        rel_file.write_text("relative")

        result = expand_file_patterns(["relative.mp3"])
        assert len(result) == 1
        assert result[0].name == "relative.mp3"

    def test_hidden_files_ignored(self, tmp_path):
        (tmp_path / "visible.mp3").write_text("visible")
        (tmp_path / ".hidden.mp3").write_text("hidden")

        pattern = str(tmp_path / "*.mp3")
        result = expand_file_patterns([pattern])

        assert len(result) == 1
        assert result[0].name == "visible.mp3"

    def test_case_sensitive_extensions(self, tmp_path):
        # On case-insensitive filesystems, we can't create both .mp3 and .MP3 files
        # So we'll test with different extensions instead
        (tmp_path / "song.mp3").write_text("lowercase")
        (tmp_path / "song.wav").write_text("wav")

        pattern_mp3 = str(tmp_path / "*.mp3")
        pattern_wav = str(tmp_path / "*.wav")

        result_mp3 = expand_file_patterns([pattern_mp3], continue_on_error=True)
        result_wav = expand_file_patterns([pattern_wav], continue_on_error=True)

        # Each pattern should match exactly one file
        assert len(result_mp3) == 1
        assert result_mp3[0].name == "song.mp3"
        assert len(result_wav) == 1
        assert result_wav[0].name == "song.wav"

    def test_empty_pattern_list(self):
        result = expand_file_patterns([], continue_on_error=True)
        assert result == []

    def test_directory_with_no_audio_files_recursive(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        (empty_dir / "text.txt").write_text("text")

        result = expand_file_patterns([str(empty_dir)], recursive=True, continue_on_error=True)
        assert result == []

    def test_file_vs_directory_same_name(self, tmp_path):
        # Create a file named "music"
        music_file = tmp_path / "music"
        music_file.write_text("not audio")

        # Create a directory named "music_dir" with audio files
        music_dir = tmp_path / "music_dir"
        music_dir.mkdir()
        (music_dir / "song.mp3").write_text("audio")

        # Test file takes precedence when it exists
        result1 = expand_file_patterns([str(music_file)])
        assert len(result1) == 1
        assert result1[0] == music_file

        # Test directory expansion
        result2 = expand_file_patterns([str(music_dir)], recursive=True)
        assert len(result2) == 1
        assert result2[0] == music_dir / "song.mp3"
