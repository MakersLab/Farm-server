import requests
import json
from os.path import join
import progressbar
import zipfile
import shutil
import os

RELEASES_URL = 'https://api.github.com/repos/MakersLab/farm-client/releases/latest'
DOWNLOAD_FOLDER = './client-build'
DESTINATION_FOLDER = './server/static/'

def deleteContentsOfFolder(path):
    if (os.path.isdir(path)):
        shutil.rmtree(path)
    os.makedirs(path)

def main():
    print('Looking for latest release')
    response = requests.get(RELEASES_URL)
    if(response.ok):
        release = json.loads(response.text)
        print('Found latest release with version {0}'.format(release['tag_name']))
        if(len(release['assets']) > 0):
            downloadableAssetIndex = -1
            for index,asset in enumerate(release['assets']):
                if(asset['name'][0:5] == 'build' and downloadableAssetIndex == -1):
                    downloadableAssetIndex = index
            if(downloadableAssetIndex == -1):
                print('Could not find downloadable release build, aborting')
            else:
                print('Found downloadable build with name {0}'.format(release['assets'][downloadableAssetIndex]['name']))
                print('Downloading latest client release with version {0}'.format(release['tag_name']))
                buildDownloadUrl = release['assets'][downloadableAssetIndex]['browser_download_url']
                buildFileName = release['assets'][downloadableAssetIndex]['name']
                r = requests.get(buildDownloadUrl, stream=True)
                # bar = progressbar.ProgressBar(max_value=len(r.content))
                with progressbar.ProgressBar(max_value=len(r.content)) as bar:
                    deleteContentsOfFolder(DOWNLOAD_FOLDER)
                    with open(join(DOWNLOAD_FOLDER,buildFileName), 'wb') as file:
                        for chunk in r.iter_content(chunk_size=1024):
                            bar.update(len(chunk))
                            file.write(chunk)
                print('Download finished')
                deleteContentsOfFolder(DESTINATION_FOLDER)

                with zipfile.ZipFile(join(DOWNLOAD_FOLDER,buildFileName), 'r') as zip:
                    print('Extracting downloaded file into {0}'.format(DESTINATION_FOLDER))
                    zip.extractall(DESTINATION_FOLDER)
                print('Finished')
                return True
    else:
        print('Could not get info about latest release')
        return False

if __name__ == '__main__':
    main()