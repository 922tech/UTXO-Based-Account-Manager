from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from apps.common.serializers import BaseModelSerializer


class PostListSerializer(ListSerializer):
    class Meta:
        # model = Post
        fields = [
            'title',
        ]


#     todo: exclude the content

class PostSerializer(BaseModelSerializer):
    # author = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        fields = '__all__'  # TODO: change this to fields
        # model = Post
        list_serializer_class = PostListSerializer
