import flickrapi, json, os
import settings_local as settings

ROOT = os.path.dirname(os.path.realpath(__file__))

# Instantiate flickr client
flickr = flickrapi.FlickrAPI(settings.FLICKR_KEY, settings.FLICKR_SECRET)
(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

# Create data dir if don't exists
d = os.path.join(ROOT, 'data')
if not os.path.exists(d):
    os.makedirs(d)

# Populate a list of dicts with photosets id and titles
photosets = [
    {
        'id': ps.attrib['id'],
        'title': ps[0].text
    } for ps in flickr.photosets_getList()[0]
]


for i in range(len(photosets)):
    photoset = photosets[i]
    f = os.path.join(d, '%s.json' % (photoset['id']))
    if not os.path.isfile(f):
        photos = flickr.photosets_getPhotos(photoset_id=photoset['id'])[0]
        photos = [
            {
                'id': photo.attrib['id'],
                'title': photo.attrib['title'], 
            } for photo in photos
        ]
        
        for j in range(len(photos)):
            sizes = flickr.photos_getSizes(photo_id=photos[j]['id'])[0]
            photos[j]['sizes'] = {
                size.attrib['label'].lower(): {
                    'width': size.attrib['width'],
                    'height': size.attrib['height'],
                    'source': size.attrib['source'],
                } for size in sizes
            } 
        photoset['photos'] = photos

        with open(f, 'w') as jsonfile:
            json.dump(photoset, jsonfile, indent=4)
