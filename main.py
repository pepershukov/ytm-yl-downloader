#!/usr/bin/python
# -*- coding: utf-8 -*-


# Usage: python <path to script> [YouTube cookie] [ffmpeg/bin folder]
# Requirements:
# 1. ffmpeg: https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z
# 2. YouTube.com cookie: "Netscape HTTP Cookie File": https://github.com/ytdl-org/youtube-dl/blob/master/README.md#how-do-i-pass-cookies-to-youtube-dl


# Imports
import datetime
import os
import sys
import yt_dlp
import json
import codecs

if '--help' in sys.argv: # print help message and exit
    print("""ytm-yl-downloader.exe (--help) [--cookie ...] (--ffmpeg ...) (--output ...) (--mode ...)

[...] - required arguments
(...) - optional arguments
Further information on requirements can be found in the README.md.
https://github.com/pepershukov/ytm-yl-downloader#readme

If the following arguments are not passed, the application will request them when necessary.
And if they fail to validate within the app, the application will throw an error.
Arguments:
    --help          • shows this message and exits

    --cookie        • the absolute path to file of a YouTube.com cookie as a "Netscape HTTP Cookie File"

    --ffmpeg        • the absolute path to folder of the binaries of FFmpeg
                    • only necessary if you are to select 'd' mode
    
    --output        • the absolute path to folder where you want your music downloaded
                    • only necessary if you are to select 'd' mode
    
    --mode          • mode (t|d|s|j) to request for the application to complete""")
    sys.exit()

# Handlers
def logwrite(string):
    print ('[LOG] {}'.format(string))  # prints LOG stdout
    with open('{}/log.txt'.format(path_main), 'a') as file:
        file.write('[[LOG] [{}] {}\n'.format(datetime.datetime.now(), string))  # writes stdout to file as LOG

def errorwrite(string, exit = 0):
    with open('{}/log.txt'.format(path_main), 'a') as file:
        file.write('[ERROR] [{}] {}\n'.format(datetime.datetime.now(), string))  # writes stdout to file as ERROR
    if not exit:
        print ('[ERROR] {} Exiting...'.format(string))  # prints ERROR stdout
        sys.exit() # exits app
    else:
        print ('[ERROR] {} Continuing...'.format(string))  # prints ERROR stdout


# Paths
path_json = '{}/metadata.json'.format(os.path.abspath(os.path.dirname(__file__)))
path_main = os.path.abspath(os.path.dirname(__file__))

if '--output' in sys.argv: # if output folder passed in arguments
    # apply the output path passed in arguments to global variables
    path_song = sys.argv[sys.argv.index('--output') + 1]
    path_temp = '{}/temp'.format(path_song)
else:
    # otherwise, apply default paths
    path_song = '{}/Music/ytm-yl-downloader'.format(os.path.expanduser('~'))
    path_temp = '{}/Music/ytm-yl-downloader/temp'.format(os.path.expanduser('~'))

if '--ffmpeg' in sys.argv: # if FFmpeg folder passed in arguments
    path_ffmpeg = sys.argv[sys.argv.index('--ffmpeg') + 1]
else:
    errorwrite('FFmpeg path not passed in args.', 1)  # if not passed, handle an error

if '--cookie' in sys.argv:
    path_cookie = sys.argv[sys.argv.index('--cookie') + 1]  # gets YouTube.com cookie path from arguments
else:
    path_cookie = input('[INPUT] Enter the absolute path to YouTube.com "Netscape HTTP Cookie File": '
                        ) # if not passed, ask the user for one
if os.path.isfile(path_cookie):  # checks if cookie file is existing
    with open(path_cookie, 'r') as file:
        data = file.readlines()[0]
        if not '# Netscape HTTP Cookie File' in data \
            or '# HTTP Cookie File' in data:  # checks for vaild formatting of a cookie file as depicted by yt-dlp
            errorwrite('Invalid formatting of a YouTube.com cookie file. Look into \'README.md\' under \'Requirements\' for instructions.'
                       )
else:
    errorwrite('Invalid or non-existant YouTube.com cookie file path.'
               )


# Main programm
if __name__ == '__main__':
    try:
        logwrite('Removing a log file...')
        os.remove('{}/log.txt'.format(path_main))
    except FileNotFoundError:
        errorwrite('Couldn\'t remove the log file.', 1)

    if '--mode' in sys.argv:
        mode = sys.argv[sys.argv.index('--mode') + 1]
    else:
        mode = input('[INPUT] playlist-to-text/donwload/sync? ([t|d|s]): ')

    logwrite("Changing current working directory to '{}'...".format(path_main))
    os.chdir(path_main)
    logwrite('Downloading a JSON metadata playlist file...')

    # os.system('cd "{}" & yt-dlp --cookies="{}" -i -J -- https://music.youtube.com/playlist?list=LM > metadata.json'.format(path_main, path_cookie))
    with yt_dlp.YoutubeDL({
        'cookiefile': path_cookie,
        'no_warnings': True,
        'dump_single_json': True,
        'ignoreerrors': True,
        }) as ydl:
        with open(path_json, 'w') as file:
            json.dump(ydl.sanitize_info(ydl.extract_info('https://music.youtube.com/playlist?list=LM'
                      , download=False)), file)  # writing playlist data to JSON file

logwrite('Opening a JSON metadata playlist file...')
try:
    with open(path_json, 'r') as file:
        logwrite('Loading dictionary from JSON file...')
        json_data = json.load(file)
except:
    with codecs.open(path_json, 'r', 'utf-16') as file:
        logwrite('Loading dictionary from JSON file...')
        json_data = json.load(file)

if __name__ == '__main__':
    if 't' in mode:
        import playlist_to_text
    if json_data['entries']: # check if there are liked songs
        if 's' in mode:
            import playlist_sync
        if 'd' in mode:
            import playlist_downloader
    else:
        errorwrite("No songs to sync/download.", 1)

    if 'j' not in mode:
        logwrite('Removing "{}"...'.format(path_json))
        os.remove(path_json)

    logwrite('================================================================================')
    logwrite('Execution finished.')
    logwrite("The log file is at '{}/log.txt'.".format(path_main))

    if 'j' in mode:
        logwrite("Your playlist metadata as a JSON formatted file is available in '{}'.".format(path_json))
    if 't' in mode:
        logwrite("Your parsed playlist information is available in '{}/songs_info.txt'.".format(path_main))
    if json_data['entries']: # check if there are liked songs
        if 's' in mode:
            logwrite("Your songs have been synchronised in '{}'.".format(path_song))
        if 'd' in mode:
            logwrite("Your downloaded songs are available in '{}'.".format(path_song))