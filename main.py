# %%
import cairo
import matplotlib.pylab as plt
import numpy as np
import moviepy.editor as mpy
import argparse


parser = argparse.ArgumentParser(description="From a given subtitle file (and optionally an audio file), creates video suitable for karaoke")
parser.add_argument("-f", "--fps",   type=int, help="fps", default = 24)
parser.add_argument("-a", "--audio",  help="file containing music audio (supported: *.mp3, *.mp4)", default = None)
parser.add_argument("-o", "--output", help="where to write output video (format: *.mp4, default: output.mp4)", default = "output.mp4")
parser.add_argument("subtitle_file",  help="*.srt file containing text aligned to audio")

args = parser.parse_args()
# answer = args.x**args.y

# sub_file = "paroles_parodies.srt"
# audio_file = "audio.mp4"
# output = "test.mp4"
# fps = 24
sub_file   = args.subtitle_file
audio_file = args.audio
output     = args.output
fps        = args.fps
width, height = 1280, 720

with open(sub_file, "r") as f:
	sub_raw = f.read().split("\n")

def parse_time_interval(time_string):
	start_string, end_string = time_string.split(" --> ")

	return tuple(
		int(string[3:5]) * 60 + int(string[6:8]) + float(string[9:12]) / 1000
		for string in [start_string, end_string]
	)



relevant_lines = [
	(parse_time_interval(sub_raw[i+1]), sub_raw[i+2])
	for i in range(0, len(sub_raw), 4)
]




# %%


def write_centered(context, text, x, y):
	x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = \
	    context.text_extents(text)

	if text_width < width * 0.9:
		x  -= (text_width / 2  + x_bearing)
		y  -= (text_height / 2 + y_bearing)

		context.move_to(x, y)
		context.show_text(text)
	else:

		# Cut roughly in the middle
		i_middle = len(text) // 2
		cut_at = i_middle + text[i_middle:].find(" ")
		string1, string2 = text[:cut_at], text[cut_at:]

		write_centered(context, string1, x, y - text_height * 1.2)
		write_centered(context, string2, x, y)



# adapted from [Gizeh](https://github.com/Zulko/gizeh)
def get_npimage(surface, width, height, transparent=False, y_origin="top"):
    """ Returns a WxHx[3-4] numpy array representing the RGB picture.

    If `transparent` is True the image is WxHx4 and represents a RGBA
    picture, i.e. array[i,j] is the [r,g,b,a] value of the pixel at
    position [i,j]. If `transparent` is false, a RGB array is returned.

    Parameter y_origin ("top" or "bottom") decides whether point (0,0)
    lies in the top-left or bottom-left corner of the screen.
    """

    im = 0 + np.frombuffer(surface.get_data(), np.uint8)
    im.shape = (height, width, 4)
    im = im[:, :, [2, 1, 0, 3]]  # put RGB back in order
    if y_origin == "bottom":
        im = im[::-1]
    return im if transparent else im[:, :, :3]

def draw_frame(i, time):
	((_, end_line), main_text) = relevant_lines[i]

	if i + 1 == len(relevant_lines):
		after_text = ""
		start_next_line = 100000
	else:
		(start_next_line, _), after_text = relevant_lines[i+1]

	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

	context = cairo.Context(surface)

	context.set_source_rgb(0, 0, 0)
	context.rectangle(0, 0, width, height)
	context.fill()



	context.select_font_face("Sans",
	                    cairo.FONT_SLANT_NORMAL,
	                    cairo.FONT_WEIGHT_NORMAL)

	context.set_source_rgb(1, 1, 1)

	context.set_font_size(50)
	write_centered(context, main_text, width / 2, height / 2)

	if start_next_line < end_line + 5:
		context.set_font_size(25)
		write_centered(context, after_text, width / 2, height / 2 + 100)
	context.close_path()

	timebar_width = (end_line - time) / 5 * width / 2
	context.set_source_rgb(0, 0.3, 0.7)
	context.rectangle(width / 2 - timebar_width, 10, 2 * timebar_width, 10)
	context.close_path()
	context.fill()

	# surface.write_to_png(tmp_file_name)
	return get_npimage(surface, width, height)


# plt.imshow(
# 	draw_frame(13, 45)
# )

# %%

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

context = cairo.Context(surface)

context.set_source_rgb(0, 0, 0)
context.rectangle(0, 0, width, height)
context.fill()

# surface.write_to_png("output/blank.png")

blank_image = get_npimage(surface, width, height)

# %%

def get_frame_index(time):
	for i, ((start, end), _) in enumerate(relevant_lines):
		if start <= time < end:
			return i
	return None

def build_frame(time):
	i_frame = get_frame_index(time)
	if i_frame is not None:
		return draw_frame(i_frame, time)
	else:
		return blank_image


total_duration = max(end for (_, end), _ in relevant_lines)

if audio_file is not None:
	audio_clip = mpy.AudioFileClip(audio_file)
	total_duration = max(total_duration, audio_clip.duration)

video_clip = mpy.VideoClip(build_frame, duration = total_duration)

if audio_file is not None:
	video_clip.audio = audio_clip

video_clip.write_videofile(output, fps = fps)

# %%



