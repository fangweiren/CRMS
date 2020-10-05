from django.http import JsonResponse
from crm import models


def ajax_class(request):
    res = {'code': 200, 'data': []}
    sid = request.GET.get('sid')
    query_set = models.ClassList.objects.filter(campuses_id=sid)
    for c in query_set:
        res['data'].append({'id': c.id, 'name': '{}-{}'.format(c.get_course_display(), c.semester)})

    return JsonResponse(res)
