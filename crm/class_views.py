from django import views
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.forms import modelformset_factory
from django.http import QueryDict
from crm.models import ClassList, CourseRecord, StudyRecord
from crm.forms import ClassListForm, CourseRecordForm, StudyRecordForm


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

    def post(self, request, class_id):
        # 1.从 POST 提交过来的数据里找 action 和 勾选的课程记录 id
        cid = request.POST.getlist('cid')
        action = request.POST.get('action')
        # 2.利用反射执行指定的动作
        if hasattr(self, '_{}'.format(action)):
            ret = getattr(self, '_{}'.format(action))(cid)
        else:
            return HttpResponse('滚')
        if ret:
            return ret
        else:
            return redirect(reverse('course_record_list', kwargs={'class_id': class_id}))

    def _multi_init(self, cid):
        # 3.根据 cid 找到要初始化学习记录的那些课程
        course_objs = CourseRecord.objects.filter(id__in=cid)
        # 4.针对每个课程挨个初始化学习记录
        # 4.1 创建学习记录：课程记录对象上面已经找到了，找学生？ --> 根据课程记录找 re_class --> 反向查找这个班级的所有学生
        for course_record in course_objs:
            students = course_record.re_class.customer_set.all()
            student_record_objs = (StudyRecord(course_record=course_record, student=student) for student in students)
            try:
                StudyRecord.objects.bulk_create(student_record_objs)
            except:
                print('初始化学习记录发生错误，应该是重复导入数据')
        return HttpResponse('初始化好了')


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


def study_record_list(request, course_record_id):
    FormSet = modelformset_factory(StudyRecord, StudyRecordForm, extra=0)
    query_set = StudyRecord.objects.filter(course_record_id=course_record_id)
    formset_obj = FormSet(queryset=query_set)
    if request.method == 'POST':
        formset_obj = FormSet(request.POST, queryset=query_set)
        if formset_obj.is_valid():
            formset_obj.save()
    return render(request, 'study_record_list.html', {'formset_obj': formset_obj})
