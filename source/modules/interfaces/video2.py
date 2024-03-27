from moviepy.editor import *
import numpy as np

class VideoGenerator:
    def __init__(self, position, uploaded_images, clip_duration=3, effect_duration=0.5, output_path="output.mp4"):
        self.clip_duration = clip_duration
        self.effect_duration = effect_duration
        self.clips = []
        self.output_path = output_path
        self.video = []
        self.index = 0   #xong n clips thi index = n

        max_height = 0
        max_width = 0
        for pos in position:
            if uploaded_images[pos].size[1] > max_height: max_height = uploaded_images[pos].size[1]
            if uploaded_images[pos].size[0] > max_width: max_width = uploaded_images[pos].size[0]
        
        self.clip_size = (max_width, max_height)
        self.black_image = ImageClip(np.zeros((max_height, max_width, 3), np.uint8)).set_duration(self.clip_duration)

        for pos in position:
            resize_width = False
            temp = uploaded_images[pos]
            if (temp.size[0] / max_width) > (temp.size[1] / max_height): resize_width = True

            if resize_width:
                temp = ImageClip(np.array(temp)).resize(width=max_width).set_duration(self.clip_duration)
            else:
                temp = ImageClip(np.array(temp)).resize(height=max_height).set_duration(self.clip_duration)

            self.clips.append(CompositeVideoClip([self.black_image, temp.set_position("center")]))

        # for pos in position:
        #     self.clips.append(ImageClip(np.array(uploaded_images[pos])).resize(self.clip_size).set_duration(self.clip_duration))

    #release the final video output
    def release(self):
        video_release = CompositeVideoClip(self.video)
        video_release.write_videofile(
            self.output_path,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            fps=24,
            threads=24,
            # ffmpeg_params=["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p"],
        )

    def cross_fade(self, position):
        #cross fade out at the final clip
        if position == "all":
            self.video = ([
                (
                    CompositeVideoClip(
                        [clip.fx(transfx.crossfadein, duration=self.effect_duration)]
                    )
                    .set_start((self.clip_duration - self.effect_duration) * idx)
                    .fx(transfx.crossfadeout, duration=self.effect_duration)
                )
                for idx, clip in enumerate(self.clips, start=0)
            ])
            self.index = len(self.video)
        else:
            #position chỉ check "all" hay không, còn lại đang setting cho làm từng clip theo self.index
            self.video.append(CompositeVideoClip([self.clips[self.index].fx(transfx.crossfadein, duration=self.effect_duration)]).set_start((self.clip_duration - self.effect_duration) * self.index).fx(transfx.crossfadeout, duration=self.effect_duration))
            self.index += 1

    #Assume side = left
    def slide(self, position, direction):
        if direction == "left": opposite_direction = "right"
        elif direction == "right": opposite_direction = "left"
        elif direction == "top": opposite_direction = "bottom"
        elif direction == "bottom": opposite_direction = "top"

        if position == "all":
            first_clip = CompositeVideoClip(
                [self.clips[0].fx(transfx.slide_out, duration=self.effect_duration, side=direction)]
            ).set_start((self.clip_duration - self.effect_duration) * 0)

            # For the last video we only need it to start entring the screen from the left going right
            # but not slide out at the end so the end clip exits on a full image not a partial image or black screen
            last_clip = CompositeVideoClip(
                [self.clips[-1].fx(transfx.slide_in, duration=self.effect_duration, side=opposite_direction)]
                # -1 because we start with index 0 so we go all the way up to array length - 1
            ).set_start((self.clip_duration - self.effect_duration) * (len(self.clips) - 1))

            self.video = (
                [first_clip]
                # For all other clips in the middle, we need them to slide in to the previous clip and out for the next one
                + [
                    (
                        CompositeVideoClip(
                            [clip.fx(transfx.slide_in, duration=self.effect_duration, side=opposite_direction)]
                        )
                        .set_start((self.clip_duration - self.effect_duration) * idx)
                        .fx(transfx.slide_out, duration=self.effect_duration, side=direction) 
                    )
                        # set start to 1 since we start from second clip in the original array
                    for idx, clip in enumerate(self.clips[1:-1], start=1)
                ]
                + [last_clip]
            )
            self.index = len(self.video)

        else:
            if self.index == 0:
                self.video.append(CompositeVideoClip([self.clips[0].fx(transfx.slide_in, duration=self.effect_duration, side=opposite_direction)]).set_start((self.clip_duration - self.effect_duration) * 0))
            else:
                #transition out effect of the previous clip
                self.video[-1] = self.video[-1].fx(transfx.slide_out, duration=self.effect_duration, side=direction)
                #transition in effect of the current clip
                self.video.append(
                    (
                        CompositeVideoClip(
                            [self.clips[self.index].fx(transfx.slide_in, duration=self.effect_duration, side=opposite_direction)]
                        )
                        .set_start((self.clip_duration - self.effect_duration) * self.index)
                    )
                )
            self.index += 1

    #old_version
    # def slide_in_left(self):
    #     # For the first clip we will need it to start from the beginning and only add
    #     # slide out effect to the end of it
    #     first_clip = CompositeVideoClip(
    #         [self.clips[0].fx(transfx.slide_out, duration=self.effect_duration, side="left")]
    #     ).set_start((self.clip_duration - self.effect_duration) * 0)

    #     # For the last video we only need it to start entring the screen from the left going right
    #     # but not slide out at the end so the end clip exits on a full image not a partial image or black screen
    #     last_clip = CompositeVideoClip(
    #         [self.clips[-1].fx(transfx.slide_in, duration=self.effect_duration, side="right")]
    #         # -1 because we start with index 0 so we go all the way up to array length - 1
    #     ).set_start((self.clip_duration - self.effect_duration) * (len(self.clips) - 1))

    #     self.video = (
    #         [first_clip]
    #         # For all other clips in the middle, we need them to slide in to the previous clip and out for the next one
    #         + [
    #             (
    #                 CompositeVideoClip(
    #                     [clip.fx(transfx.slide_in, duration=self.effect_duration, side="right")]
    #                 )
    #                 .set_start((self.clip_duration - self.effect_duration) * idx)
    #                 .fx(transfx.slide_out, duration=self.effect_duration, side="left")
    #             )
    #                 # set start to 1 since we start from second clip in the original array
    #             for idx, clip in enumerate(self.clips[1:-1], start=1)
    #         ]
    #         + [last_clip]
    #     )

    #old_version
    # def slide_in_right(self):
    #     # For the first clip we will need it to start from the beginning and only add
    #     # slide out effect to the end of it
    #     first_clip = CompositeVideoClip(
    #         [self.clips[0].fx(transfx.slide_out, duration=self.effect_duration, side="right")]
    #     ).set_start((self.clip_duration - self.effect_duration) * 0)

    #     # For the last video we only need it to start entring the screen from the right going left
    #     # but not slide out at the end so the end clip exits on a full image not a partial image or black screen
    #     last_clip = CompositeVideoClip(
    #         [self.clips[-1].fx(transfx.slide_in, duration=self.effect_duration, side="left")]
    #         # -1 because we start with index 0 so we go all the way up to array length - 1
    #     ).set_start((self.clip_duration - self.effect_duration) * (len(self.clips) - 1))

    #     self.video = (
    #         [first_clip]
    #         # For all other clips in the middle, we need them to slide in to the previous clip and out for the next one
    #         + [
    #             (
    #                 CompositeVideoClip(
    #                     [clip.fx(transfx.slide_in, duration=self.effect_duration, side="left")]
    #                 )
    #                 .set_start((self.clip_duration - self.effect_duration) * idx)
    #                 .fx(transfx.slide_out, duration=self.effect_duration, side="right")
    #             )
    #                 # set start to 1 since we start from second clip in the original array
    #             for idx, clip in enumerate(self.clips[1:-1], start=1)
    #         ]
    #         + [last_clip]
    #     )

    #old_version
    # def slide_in_top(self):
    #     # For the first clip we will need it to start from the beginning and only add
    #     # slide out effect to the end of it
    #     first_clip = CompositeVideoClip(
    #         [self.clips[0].fx(transfx.slide_out, duration=self.effect_duration, side="top")]
    #     ).set_start((self.clip_duration - self.effect_duration) * 0)

        
    #     last_clip = CompositeVideoClip(
    #         [self.clips[-1].fx(transfx.slide_in, duration=self.effect_duration, side="bottom")]
    #         # -1 because we start with index 0 so we go all the way up to array length - 1
    #     ).set_start((self.clip_duration - self.effect_duration) * (len(self.clips) - 1))

    #     self.video = (
    #         [first_clip]
    #         # For all other clips in the middle, we need them to slide in to the previous clip and out for the next one
    #         + [
    #             (
    #                 CompositeVideoClip(
    #                     [clip.fx(transfx.slide_in, duration=self.effect_duration, side="bottom")]
    #                 )
    #                 .set_start((self.clip_duration - self.effect_duration) * idx)
    #                 .fx(transfx.slide_out, duration=self.effect_duration, side="top")
    #             )
    #                 # set start to 1 since we start from second clip in the original array
    #             for idx, clip in enumerate(self.clips[1:-1], start=1)
    #         ]
    #         + [last_clip]
    #     )   

    #old_version
    # def slide_in_bottom(self):
    #     # For the first clip we will need it to start from the beginning and only add
    #     # slide out effect to the end of it
    #     first_clip = CompositeVideoClip(
    #         [self.clips[0].fx(transfx.slide_out, duration=self.effect_duration, side="bottom")]
    #     ).set_start((self.clip_duration - self.effect_duration) * 0)

        
    #     last_clip = CompositeVideoClip(
    #         [self.clips[-1].fx(transfx.slide_in, duration=self.effect_duration, side="top")]
    #         # -1 because we start with index 0 so we go all the way up to array length - 1
    #     ).set_start((self.clip_duration - self.effect_duration) * (len(self.clips) - 1))

    #     self.video = (
    #         [first_clip]
    #         # For all other clips in the middle, we need them to slide in to the previous clip and out for the next one
    #         + [
    #             (
    #                 CompositeVideoClip(
    #                     [clip.fx(transfx.slide_in, duration=self.effect_duration, side="top")]
    #                 )
    #                 .set_start((self.clip_duration - self.effect_duration) * idx)
    #                 .fx(transfx.slide_out, duration=self.effect_duration, side="bottom")
    #             )
    #                 # set start to 1 since we start from second clip in the original array
    #             for idx, clip in enumerate(self.clips[1:-1], start=1)
    #         ]
    #         + [last_clip]
    #     )    
    
    def reset(self):
        self.images = []
        self.clips = []
        self.video = []
        self.index = 0