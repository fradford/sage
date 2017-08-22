import argparse

import src


def main():
    parser = argparse.ArgumentParser(prog="sage")
    parser.add_argument('mode', help="mode 0: convert image to sound\nmode 1: convert sound to image", type=int)
    parser.add_argument('infile', help="The name of the input image.")
    parser.add_argument('outfile', help="The name of the output file.")
    parser.add_argument('-f', '--framerate', help="Output framerate.", default=48000, type=int)
    parser.add_argument('-l', '--duration', help="Length of output, in seconds.", default=180, type=int)
    parser.add_argument('-c', '--chunksize', help="Number of frames to hold in memory.", default=1000000, type=int)
    parser.add_argument('-t', '--threading', help="Specifies multiprocessing or no multiprocessing. Vital on large "
                                                  "images, slows down small images considerably due to I/O overhead.",
                        action="store_true")
    args = parser.parse_args()

    if args.mode == 0:
        converter = src.Converters.ImageToSound(args)
    elif args.mode == 1:
        converter = src.Converters.SoundToImage(args)
    else:
        raise ValueError("Invalid mode")
    converter.run()

if __name__ == "__main__":
    main()
