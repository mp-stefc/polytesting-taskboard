import json
from django.http import HttpResponse # TODO: this disables streaming :(

class JsonResponse(HttpResponse):

    def __init__(self, obj_to_dump, **kw):
        kwarg_content_type = kw.get('content_type', None) 
        assert kwarg_content_type is None, kwarg_content_type
        kw['content_type'] = 'application/json'
        kw['content'] = json.dumps(obj_to_dump)
        super(JsonResponse, self).__init__(**kw)

