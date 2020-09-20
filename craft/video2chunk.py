import numpy as np
from jina.executors.crafters import BaseSegmenter

from craft.keyframe_extractor import get_keyframes_from_video


class VideoPreprocessor(BaseSegmenter):
    def __init__(self, num_keyframes=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_keyframes = num_keyframes

    def craft(self, buffer, id):
        result = []
        try:
            idx = 0
            for frame in get_keyframes_from_video(buffer, self.num_keyframes):
                try:
                    img = (np.array(frame) / 255).astype(np.float32)
                    result.append(dict(id=id, offset=idx,
                            weight=1., blob=img))
                except Exception as ex:
                    self.logger.error(ex)
                finally:
                    idx = idx + 1
            return result

        except Exception as ex:
            self.logger.error(ex)
