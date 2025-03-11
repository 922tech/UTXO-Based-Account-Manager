from rest_framework import serializers


class WriteOnceMixin:
    """
    Adds support for write once fields to serializers.

    To use it, specify a list of fields as `write_once_fields` on the
    serializer's Meta:
    ```
    class Meta:
        model = SomeModel
        fields = '__all__'
        write_once_fields = ('collection', )
    ```

    Now the fields in `write_once_fields` can be set during POST (create),
    but cannot be changed afterwards via PUT or PATCH (update).
    Inspired by http://stackoverflow.com/a/37487134/627411.
    """

    def get_fields(self):
        fields = super().get_fields()

        # We're only interested in PATCH and PUT.
        if 'update' in getattr(self.context.get('view'), 'action', ''):
            fields = self._update_write_once_fields(fields)

        return fields

    def _update_write_once_fields(self, fields):
        """
        Set all fields in `Meta.write_once_fields` to read_only.
        """

        write_once_fields = getattr(self.Meta, 'write_once_fields', None)
        if not write_once_fields:
            return fields

        if not isinstance(write_once_fields, (list, tuple)):
            raise TypeError(
                'The `write_once_fields` option must be a list or tuple. '
                'Got {}.'.format(type(write_once_fields).__name__)
            )

        for field_name in write_once_fields:
            fields[field_name].read_only = True

        return fields


class BaseModelSerializer(WriteOnceMixin, serializers.ModelSerializer):
    pass


class BaseSerializer(WriteOnceMixin, serializers.Serializer):
    pass

