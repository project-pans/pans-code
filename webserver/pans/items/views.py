from django.db.models import Q
from django.views.generic import TemplateView, ListView
from .models import Item


class HomePageView(TemplateView):
    template_name = 'home.html'

class SearchResultsView(ListView):
    model = Item
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Item.objects.filter(
            Q(name__icontains=query) | Q(upc__icontains=query)
        )
        return object_list
