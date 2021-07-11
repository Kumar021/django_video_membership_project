from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, View
from memberships.models import UserMembership
from .models import Course, Lesson

def logout_view(request):
    logout(request) 
    return redirect('courses:list')




class CourseListView(ListView):
    model = Course


class CourseDetailView(DetailView):
    model = Course


class LessonDetailView(LoginRequiredMixin, View):

    def get(self, request, course_slug, lesson_slug, *args, **kwargs):
        course = get_object_or_404(Course, slug=course_slug)
        lesson = get_object_or_404(Lesson, slug=lesson_slug)
        user_membership = get_object_or_404(UserMembership, user=request.user)
        user_membership_type = user_membership.membership.membership_type
        course_allowed_mem_types = course.allowed_memberships.all()
        context = { 'object': None }
        if course_allowed_mem_types.filter(membership_type=user_membership_type).exists():
            context = {'object': lesson}
        return render(request, "courses/lesson_detail.html", context)
