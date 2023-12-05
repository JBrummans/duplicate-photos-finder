import os
import numpy as np
import time
import itertools
from PIL import Image
from tqdm import tqdm
import argparse
import skimage.measure

# Constants
COMPARE_SIZE = 300


def process_image(file_path):
    try:
        # Check if the file is an image
        if not os.path.isfile(file_path):
            return None

        img = Image.open(file_path).convert("L")
        img = img.resize((COMPARE_SIZE, COMPARE_SIZE))
        img = np.array(img)

        for _ in range(3):
            img = skimage.measure.block_reduce(img, (2, 2), func=np.mean)

        return img
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return None


def find_duplicates(images, images_name):
    im_duplicates = []

    for i in tqdm(range(len(images))):
        duplicates = np.all(images == images[i], axis=(1, 2))
        duplicates[i] = False
        idx = np.where(duplicates)[0]
        if idx.size > 0:
            im_duplicate = [i] + idx.tolist()
            im_duplicate.sort()
            im_duplicates.append(im_duplicate)

    return im_duplicates


def delete_files(files_to_delete):
    for file in files_to_delete:
        os.remove(file)
    print("Deleted files.")


def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate images in a directory."
    )
    parser.add_argument(
        "--directory",
        "-d",
        nargs="?",
        type=str,
        default=os.getcwd(),
        help="Directory of images.",
    )
    args = parser.parse_args()

    try:
        if args.directory:
            directory = args.directory
            print(f"Inspection Directory: {directory}")
        else:
            print("ERROR: Inspection Directory not specified")
            return
    except Exception as e:
        print(e)
        return

    folders = [x[0] for x in os.walk(directory)]
    to_delete = []

    try:
        for folder in folders:
            print(f"Checking Folder -> {folder}")
            files = os.listdir(folder)
            files.sort()
            images = []
            images_name = []

            for i in tqdm(range(len(files))):
                img = process_image(os.path.join(folder, files[i]))
                try:
                    if img is not None:
                        images.append(img)
                        images_name.append(files[i])
                except Exception as e:
                    input(e)
                    
            images = np.array(images)
            print(f"Images Read. Total images = {len(images)}")

            if len(images) < 2:
                continue

            print("Finding duplicates now...")
            im_duplicates = find_duplicates(images, images_name)

            im_duplicates.sort()
            im_duplicates = list(
                im_duplicates for im_duplicates, _ in itertools.groupby(im_duplicates)
            )

            if len(im_duplicates) > 0:
                print("Duplicates:")
                for i in range(len(im_duplicates)):
                    for j in range(len(im_duplicates[i])):
                        print(images_name[im_duplicates[i][j]], end="\t")
                        if j > 0:
                            to_delete.append(
                                os.path.join(folder, images_name[im_duplicates[i][j]])
                            )
                    print()
            else:
                print("No duplicates found.")

        print(
            "-----------------------------Overall Report----------------------------------"
        )

        if len(to_delete) == 0:
            print("No duplicates found.")
            return

        print("Files marked for delete:")
        for file in to_delete:
            print(file)
        if  input("Type Y to delete: ").lower() == "y":
            delete_files(to_delete)
        else:
            print("Files not deleted.")
    except Exception as e:
        print(e)
    finally:
        input("Complete. Press enter to finish")


if __name__ == "__main__":
    main()
