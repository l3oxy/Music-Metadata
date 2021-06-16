'''
Progam to update song metadata for all flac files.
By l3oxy

Expects the following:
1. Python3.7+
2. A shell that supports the "ls" command. (e.g. BASH, SH)
3. "python-mutagen" or "python3-mutagen" package to be installed, which brings command "mid3v2". (e.g. on Ubuntu use "sudo apt-get update -y" and then "sudo apt install python-mutagen", but if that fails then try "sudo apt install python3-mutagen")
4. Flac files to have filename format of "Song_-_Artist_-_{videoID}.flac" , 
though the "_-_{videoID}" part is optional.

Syntax:
    python3.7 this_script.py [/home/me/music/]

    Where the last argument is optional (indicated by the square brackets),
    but, if used, specifies the directory to operate in.
'''
import concurrent.futures
import logging
import subprocess
import sys
import time # this just for benchmarking.

# Configure logging settings.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

# Verify that a specific command is available
logging.debug("STARTING MID3V2 CHECK")
mid3v2_test = subprocess.run(args=["mid3v2 --version"], shell=True, check=False, text=True)

if mid3v2_test.returncode == 0:
	logging.debug("MID3V2 CHECK COMPLETE")
else:
    logging.warning("mid3v2 not detected. Install package either 'python-mutagen' or 'python3-mutagen', which brings command 'mid3v2' (e.g. on Ubuntu use 'sudo apt-get update -y' and then 'sudo apt install python-mutagen', but if that fails then try 'sudo apt install python3-mutagen')")
    exit();

# Begin benchmark time.
benchmark_start = time.perf_counter()

# Determine if directory argument was supplied
directory = ""
if len(sys.argv) > 1 and len(sys.argv[-1]) >= 1:
    directory = sys.argv[-1]
else:
    directory = "./"
if not directory.endswith("/"):
    directory += "/"
logging.debug("DIRECTORY_INPUT: " + directory)

# If a directory argument was provided, verify that it is accessible.
directory_check_output = subprocess.run(args="ls -d " + directory, capture_output=True, shell=True, text=True, timeout=30)
if directory_check_output.returncode != 0:
    logging.error("Attempt to verify existence of directory \"" + directory + "\" failed with the following error: " + directory_check_output.stderr)
    sys.exit(1)
else:
    logging.debug("DIRECTORY_VERIFICATION: " + directory_check_output.stdout.rstrip())

# Attempt to identify all flac files. If unsuccessful, error out.
flacs_output = subprocess.run(args="ls -l -1 --time-style=full-iso --ignore-backups " + directory + "*.flac", capture_output=True, shell=True, text=True, timeout=30)
if flacs_output.returncode == 0:
    logging.debug("LISTINGS: \n" + flacs_output.stdout.rstrip())
else:
    logging.error("Attempt to locate flac files within directory \"" + directory + "\" failed. Perhaps none are present. Full error: " + flacs_output.stderr)
    sys.exit(1)
    


# Convert identified flacs into a list
flacs_output_list = flacs_output.stdout.split("\n")
#  Remove any empty items.
while '' in flacs_output_list:
    flacs_output_list.remove('')

# Output how many flacs were found
flacs_output_list_len = len(flacs_output_list)
logging.info("LISTSINGS COUNT: " + str(flacs_output_list_len))



# Function used on each flac
def process_flac(flac_listing, ID_int):
    # Increment counter.
    ID = str(ID_int)


    # Starting operation on this flac file.
    logging.info(ID + ":Begin")

    # Seperate parts of the flac listing.
    flac_listing_parts = flac_listing.split()
    
    flac_listing_parts_count = len(flac_listing_parts);
    if flac_listing_parts_count == 9:
        logging.debug(ID + ": parts count " + str(flac_listing_parts_count))
    else:
        logging.error(ID + ": parts count is unexpectedly " + str(flac_listing_parts_count) + " instead of 9 **************************************************************************************************************************************************************************************************************************************************************************************************** CHECK FOR ANY UNEXPECTED SPACES IN THE FILENAME ********************")
        return

    # Filepath and filename
    filepath = flac_listing_parts[-1]
    logging.debug(ID + ":Filepath: " + filepath)
    filename = filepath[len(directory):]
    logging.info(ID + ":Filename: " + filename)

    # Song
    filename_parts_no_extension = filename[:filename.rfind(".")].split("_-_")
    song = filename_parts_no_extension[0].replace("_", " ").strip()
    logging.info(ID + ":Song:     " + song)

    # Artist
    artist = filename_parts_no_extension[1].replace("_", " ").strip()
    logging.info(ID + ":Artist:   " + artist)

    # (Optionally) the songID in braces (which may also contain the character "-")
    if filename_parts_no_extension[-1].startswith("{") and filename_parts_no_extension[-1].endswith("}"):
        videoID = filename_parts_no_extension[-1].strip("{}")
    else:
        videoID = ""
    argument_to_add_videoID_as_comment = "--comment=" + videoID
    logging.info(ID + ":VideoID:  " + videoID)

    # Original datetime
    change_date = flac_listing_parts[-4].split("-")
    change_year = change_date[0]
    change_month = change_date[1]
    change_day = change_date[2]
    change_time = flac_listing_parts[-3].split(":")
    change_hour = change_time[0]
    change_minute = change_time[1]
    change_second = change_time[2].split(".")[0]
    original_datetime = change_year + change_month + change_day + change_hour + change_minute + "." + change_second
    logging.info(ID + ":Datetime: " + original_datetime)

    # Add song and artist metadata (changes modification_date of file)
    subprocess.run(args=["mid3v2", '--artist=' + artist, '--song=' + song, argument_to_add_videoID_as_comment, filepath], shell=False, check=True, text=True)

    # Reset file's modification_date back to what it was.
    subprocess.run(args=['touch', '-t', original_datetime, filepath], shell=False, check=True, text=True)

    # This flac file is complete.
    logging.info(ID + ":Complete")


id_generator = iter(range(1, (flacs_output_list_len + 1))) # Calling next() on this returns an int to be used as an identifier for each process.
completed_processes = 0


with concurrent.futures.ProcessPoolExecutor() as executor:
    list_of_processes = [executor.submit(process_flac, flac_listing, next(id_generator)) for flac_listing in flacs_output_list]

    for f in concurrent.futures.as_completed(list_of_processes):
        completed_processes += 1

benchmark_finish = time.perf_counter()

if flacs_output_list_len == completed_processes:
    logging.info("Attempted operations on all " + str(flacs_output_list_len) + " file(s) detected, in " +
            str(round(benchmark_finish - benchmark_start, 3)) + " second(s).")
else:
    logging.info("Of " + str(flacs_output_list_len) + " file(s) found, attempted operations on " + str(completed_processes) +
            ", over " + str(round(benchmark_finish - benchmark_start, 3)) + " second(s).")
