import re
from rest_framework import serializers


def validate_youtube_link(value):
    """
    Валидатор для проверки, что ссылка ведёт на youtube.com
    Можно использовать как функцию-валидатор
    """
    if not value:
        return value

    # Регулярное выражение для проверки youtube ссылок
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'

    if not re.match(youtube_pattern, value):
        raise serializers.ValidationError(
            'Разрешены только ссылки на YouTube (youtube.com или youtu.be)'
        )

    return value


class YouTubeLinkValidator:
    """
    Класс-валидатор для проверки, что ссылка ведёт на youtube.com
    """

    def __call__(self, value):
        if not value:
            return value

        youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'

        if not re.match(youtube_pattern, value):
            raise serializers.ValidationError(
                'Разрешены только ссылки на YouTube (youtube.com или youtu.be)'
            )

        return value
