from django import views
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import QueryDict
from crm.models import ClassList, CourseRecord
from crm.forms import ClassListForm, CourseRecordForm


class ClassListView(views.View):
    def get(self, request):
        query_set = ClassList.objects.all()
        return render(request, 'class_list.html', {'class_list': query_set})


def add_edit_class(request, edit_id=None):
    class_obj = ClassList.objects.filter(id=edit_id).first()
    form_obj = ClassListForm(instance=class_obj)
    if request.method == 'POST':
        form_obj = ClassListForm(request.POST, instance=class_obj)
        form_obj.save()
        return redirect(reverse('class_list'))
    return render(request, 'add_edit_class.html', {'form_obj': form_obj, 'edit_id': edit_id})


class CourseRecordListView(views.View):
    def get(self, request, class_id):
        query_set = CourseRecord.objects.filter(re_class_id=class_id)
        current_url = request.get_full_path()
        qd = QueryDict(mutable=True)
        qd['next'] = current_url
        return render(request, 'course_record_list.html',
                      {'course_record_list': query_set, 'next_url': qd.urlencode(), 'class_id': class_id})


def course_record(request, class_id=None, course_record_id=None):
    class_obj = ClassList.objects.filter(id=class_id).first()
    course_record_obj = CourseRecord.objects.filter(id=course_record_id).first()
    # 如果查询不到上课记录说明是添加上课记录操作
    # 又因为添加上课记录必须指定班级
    if not course_record_obj:
        course_record_obj = CourseRecord(re_class=class_obj)
    form_obj = CourseRecordForm(instance=course_record_obj)
    if request.method == 'POST':
        form_obj = CourseRecordForm(request.POST, instance=course_record_obj)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next', '/crm/class_list/')
            return redirect(next_url)
    return render(request, 'course_record.html', {'form_obj': form_obj, 'edit_id': course_record_id})
