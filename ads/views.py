from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Ad, Category


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 6

    def get_queryset(self):
        queryset = Ad.objects.filter(is_active=True).select_related('category', 'author')
        
        # Поиск по заголовку и тексту
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            )
        
        # Фильтр по категории
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