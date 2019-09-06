CODE_TYPES = ['x-c', 'html']

FILE_TYPES = {
    'image': '<figure><img class="image" src="{}"><figcaption>{}</figcaption></figure>',
    'pdf': (
        '<object data="{}" class="pdf" type="application/pdf">'
        '<embed src="{}" type="application/pdf" /></object>'
    ),
    'text': '<a href="{}" class="text">{}</a>',
    'video': ('<video class="video" controls>' '<source src="{}"></source></video>'),
    'audio': ('<audio controls class="audio">' '<source src="{}"></source></audio>'),
}

