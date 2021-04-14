def validate_video_fps(value):
    try:
        assert 1 <= int(str(value)) <= 30
    except (ValueError, AssertionError):
        return False
    else:
        return True
