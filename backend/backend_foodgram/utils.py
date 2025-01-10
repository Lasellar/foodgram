import random
import string


def generate_short_link(request):
    random.seed(request.path)
    short_link = ''.join(
        [
            random.choice(string.ascii_letters + string.digits)
            for _ in range(3)
        ]
    )
    return short_link


def generate_full_short_url(link):
    return {
        'short-link': f'https://foodgram_lasellar.ddns.com/s/{link}'
    }
