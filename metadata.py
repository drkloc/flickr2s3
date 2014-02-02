import flickrapi, json, os, boto
import settings_local as settings
from boto.s3.key import Key
from os import walk


ROOT = os.path.dirname(os.path.realpath(__file__))

# Instantiate aws client
aws = boto.connect_s3(settings.AWS_KEY, settings.AWS_SECRET)
bucket = aws.get_bucket(settings.AWS_BUCKET)

# Instantiate flickr client
flickr = flickrapi.FlickrAPI(settings.FLICKR_KEY, settings.FLICKR_SECRET)
(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

def update_exifs_from_string(photo_id, key):
    print 'Updating  %s' % key
    k = Key(bucket)
    k.key = key
    j = json.loads(k.get_contents_as_string())
    if not j.has_key('exif'):
        print '-- %s not set' % key
        exifs = flickr.photos_getExif(photo_id=photo_id)[0]
        exifs = {
            exif.attrib['label'].lower(): {
                'space': exif.attrib['tagspace'],
                'id': exif.attrib['tagspaceid'],
                'tag': exif.attrib['tag'],
                'raw': exif[0].text,
            } for exif in exifs
        }
        j['exif'] = exifs
        k.set_contents_from_string(json.dumps(j, indent=2))
        print '-- Updated  %s' % key
    else:
        print '-- %s already set' % key


data_dir = 'data'
for (dirpath, dirnames, filenames) in walk(os.path.join(ROOT, data_dir)):
    for f in filenames:
        json_file = open(os.path.join(ROOT, data_dir, f))
        data = json.load(json_file)
        for photo in data['photos']:
            update_exifs_from_string(
                photo['id'],
                '%s/%s.%s' % (data['id'], photo['id'], 'json')
            )
