import boto, json, os, urllib2, StringIO 
import settings_local as settings
from boto.s3.key import Key
from os import walk

ROOT = os.path.dirname(os.path.realpath(__file__))

# Instantiate aws client
aws = boto.connect_s3(settings.AWS_KEY, settings.AWS_SECRET)
bucket = aws.get_bucket(settings.AWS_BUCKET)

bucket_keys = [k.key for k in bucket.list()] 

def set_key_from_string(key, data):
    print 'Trying to set key string for %s' % key
    if not key in bucket_keys:
        print '-- Setting %s' % key
        k = Key(bucket)
        k.key = key
        k.set_contents_from_string(data)
    else:
        print '-- Already set'

def set_key_from_url(key, url):
    print 'Trying to set key string for %s' % key
    if not key in bucket_keys:
        print '-- Setting %s' % key
        k = Key(bucket)
        k.key = key
        file_object = urllib2.urlopen(url)
        fp = StringIO.StringIO(file_object.read())
        k.set_contents_from_file(fp)
    else:
        print '-- Already set'        


data_dir = 'data'
for (dirpath, dirnames, filenames) in walk(os.path.join(ROOT, data_dir)):
    for f in filenames:
        json_file = open(os.path.join(ROOT, data_dir, f))
        data = json.load(json_file)


        set_key_from_string(
            '%s/info.json' % data['id'],
            json.dumps(
                {
                    'title': data['title']
                },
                indent=4
            )
        )

        # Tour photos 
        for photo in data['photos']:
            set_key_from_string(
                '%s/%s.%s' % (data['id'], photo['id'], 'json'),
                json.dumps(
                    {
                        'title': photo['title']
                    },
                    indent=4
                )
            )
            for k in photo['sizes'].keys():
                set_key_from_url(
                    '%s/%s_%s.jpg' % (data['id'], photo['id'], k),
                    photo['sizes'][k]['source']
                )
