import argparse

from ImageToSound import ImageToSound
from SoundToImage import SoundToImage


def main():
    parser = argparse.ArgumentParser(prog="image_to_sound")
    parser.add_argument('mode', help="mode 0: convert image to sound\nmode 1: convert sound to image", type=int)
    parser.add_argument('infile', help="The name of the input image.")
    parser.add_argument('outfile', help="The name of the output file.")
    parser.add_argument('-a', '--all_pixels', help="If specified frequencies are generated from all pixels.",
                        action="store_true")
    parser.add_argument('-d', '--disk_db', help="If specified the wave storage database will be saved to disk. You'll "
                                                "likely want to specify this if you are specifying -a.",
                        action="store_true")
    parser.add_argument('-f', '--framerate', help="Output framerate.", default=48000, type=int)
    parser.add_argument('-l', '--duration', help="Length of output.", default=180, type=int)
    parser.add_argument('-c', '--chunk_size', help="Size of chunk.", default=1, type=int)
    args = parser.parse_args()

    if args.mode == 0:
        converter = ImageToSound(args)
    elif args.mode == 1:
        converter = SoundToImage(args)
    else:
        raise ValueError("Invalid mode")
    converter.run()

if __name__ == "__main__":
    main()
