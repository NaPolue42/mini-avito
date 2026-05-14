from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from .models import Ad, Category


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 6

    def get_queryset(self):
        queryset = Ad.objects.filter(is_active=True).select_related('category', 'author')
        
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            )
        
        category_slug = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    template_name = 'ads/ad_form.html'
    fields = ['title', 'text', 'price', 'image', 'category']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Объявление успешно создано!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.pk})


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    template_name = 'ads/ad_form.html'
    fields = ['title', 'text', 'price', 'image', 'category']
    
    def test_func(self):
        return self.get_object().author == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Объявление обновлено!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.pk})


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')
    
    def test_func(self):
        return self.get_object().author == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Объявление удалено!')
        return super().form_valid(form)


class MyAdsView(LoginRequiredMixin, ListView):
    model = Ad
    template_name = 'ads/my_ads.html'
    context_object_name = 'ads'
    
    def get_queryset(self):
        return Ad.objects.filter(author=self.request.user).select_related('category')


class RegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Регистрация успешна! Теперь войдите.')
        return super().form_valid(form)