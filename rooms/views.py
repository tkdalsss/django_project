from django.views.generic import ListView, DetailView
#from django.utils import timezone
from django.shortcuts import render, redirect
#from django.urls import reverse
from django_countries import countries
from . import models

class HomeView(ListView): # class-based View

    # Home View Definition

    model = models.Room
    paginate_by = 10
    ordering = "created"
    context_object_name = "rooms"
    
class RoomDetail(DetailView):
    
    # Room_Detail Definition
    
    model = models.Room
    
def search(request):
    city = request.GET.get("city", "Anywhere")
    city = str.capitalize(city)
    room_types = models.RoomType.objects.all()
    return render(request, "rooms/search.html", {
        "city": city,
        "countries": countries,
        "room_types": room_types
    })

"""
### function-based view ###
def room_detail(request, pk):
    try:
        room = models.Room.objects.get(pk=pk)
        return render(request, "rooms/detail.html", {"room": room})
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))

    

    
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    now = timezone.now()
    context["now"] = now
    return context
    




from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from . import models

# Create your views here.
def all_rooms(request):
    # previous code
    page = request.GET.get("page", 1)
    page = int(page or 1)
    page_size = 10
    limit = page_size * page
    offset = limit - page_size
    all_rooms = models.Room.objects.all()[offset:limit]
    page_count = ceil(models.Room.objects.count() / page_size)
    return render(request, "rooms/all_rooms.html", context={
        "rooms": all_rooms,
        "page": page,
        "page_count": page_count,
        "page_range": range(1, page_count+1)
    })
    # recent code
    page = request.GET.get("page", 1)
    room_list = models.Room.objects.all() # create querySet
    paginator = Paginator(room_list, 10)

    try:
        rooms = paginator.page(int(page))
        return render(request, "rooms/all_rooms.html", context={
            "rooms": rooms
        })
    except EmptyPage:
        rooms = paginator.page(1)
        return redirect("/")
"""
    