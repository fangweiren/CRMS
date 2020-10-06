from django import views
from django.shortcuts import render, redirect
from django.urls import reverse
from crm.models import ClassList
from crm.forms import ClassListForm


class ClassListView(views.View):
    def get(self, request):
        query_set = ClassList.objects.all()
        return render(request, 'class_list.html', {'class_list': query_set})

    def post(self, request):
        pass


def add_edit_class(request, edit_id=None):
    class_obj = ClassList.objects.filter(id=edit_id).first()
    form_obj = ClassListForm(instance=class_obj)
    if request.method == 'POST':
        form_obj = ClassListForm(request.POST, instance=class_obj)
        form_obj.save()
        return redirect(reverse('class_list'))
    return render(request, 'add_edit_class.html', {'form_obj': form_obj, 'edit_id': edit_id})
