from Katna.video import Video


def get_keyframes_from_video(video_path, num_frames):
    video = Video()
    images = video.extract_frames_as_images(num_frames, video_path)
    return images
