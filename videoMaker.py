
# Import all the things!
import os
import requests
import sys
from time import sleep
from shutil import make_archive
from datetime import date, timedelta
from twython import Twython, exceptions
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)


# Function to check internet connectivity
def checkConnection():
    try:
        requests.get("http://google.com", timeout=3)
        return True
    except requests.ConnectionError:
        pass

    return False


# Function to tweet video
def tweetVideo(fileName):
    # Set attempts for while loop below
    attempt = 0
    maxAttempts = 5

    while attempt < maxAttempts:
        # This section posts the video to twitter if the internet is connected
        if checkConnection():
            twitter = Twython(
                consumer_key, consumer_secret,
                access_token, access_token_secret)

            message = 'Garden timelapse - %s' % yesterday.strftime('%d-%m-%Y')
            video = open(fileName, 'rb')

            # Maybe add try so that if it mucks up/timesout then it'll retry
            try:
                response = twitter.upload_video(
                    media=video,
                    media_type='video/mp4',
                    media_category='tweet_video',
                    check_progress=True)

                twitter.update_status(
                    status=message, media_ids=[response['media_id']])
                return
            except exceptions.TwythonError:
                attempt += 1

        # If internet is not currently available then wait and retry
        else:
            sleep(15)
            attempt += 1


if len(sys.argv) > 1:
    fps = sys.argv[1]
else:
    fps = "15"

# Generate string for yesterdays files
yesterday = date.today() - timedelta(1)
yesterdayStr = yesterday.strftime('%Y-%m-%d')

# Set working directory as home
os.chdir(os.path.expanduser("~"))

# Dictionary of directories
dirs = {
    'archiveDir': 'archive',
    'outputDir': 'videos',
    'inputDir': 'Camera1/%s' % yesterdayStr
}

# If the directories specified above doesn't exist then make them
for key in dirs:
    if not(os.path.exists(dirs[key])):
        os.mkdir(dirs[key])

# Generate filenames and directories
# Input
inputFiles = os.path.join(dirs['inputDir'], '*.jpg')
# Output
outputFile = os.path.join(dirs['outputDir'], '%s.mov' % yesterdayStr)
# Archive
archiveFile = os.path.join(dirs['archiveDir'], yesterdayStr)

# Check if output file already exists
if not(os.path.exists(outputFile)):
    # If not generate mp4 from the still images recorded the day before
    os.system(
        'cat %s | ' % inputFiles +
        'ffmpeg -loglevel 10 -nostats -framerate %s -f image2pipe ' % fps +
        '-vcodec mjpeg -i - -vcodec libx264 -b:v 2048k -y temp.mov'
    )
    # Cut before dawn and after dusk
    os.system(
        'ffmpeg -loglevel 10 -nostats -i temp.mov ' +
        '-ss 00:00:16.0 -to 00:01:32.0 -c copy %s' % outputFile
    )
    # Delete temporary file
    os.remove('temp.mov')

# Archive the images used for the video and delete original folder
make_archive(archiveFile, 'zip', dirs['inputDir'])
# rmtree(dir['inputDir'])

# Try and tweet the videos
tweetVideo(outputFile)
