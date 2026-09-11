from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from apps.profiles.models import Department, Skill, ResearchInterest
from apps.profiles.taxonomy import DEPARTMENT_NAMES
from .models import Project

class DiscoveryForm(forms.Form):
    q = forms.CharField(required=False, max_length=160, label='Search opportunities',
        widget=forms.TextInput(attrs={'placeholder':'Title, summary or available role'}))
    department = forms.ModelChoiceField(required=False, queryset=Department.objects.filter(name__in=DEPARTMENT_NAMES),
        empty_label='All departments')
    domain = forms.ModelChoiceField(required=False, queryset=ResearchInterest.objects.all(),
        empty_label='All research domains', label='Research domain')
    skill = forms.ModelChoiceField(required=False, queryset=Skill.objects.all(), empty_label='All skills',
        label='Required skill')
    sort = forms.ChoiceField(required=False, choices=[('newest','Newest first'),('oldest','Oldest first'),
        ('positions','Most open positions'),('title','Title A–Z')], label='Sort by')

def discovery_context(request):
    form = DiscoveryForm(request.GET)
    records = Project.objects.filter(status=Project.Status.RECRUITING,creator__is_demo=request.user.is_demo)
    valid = form.is_valid()
    if valid:
        values = form.cleaned_data
        if values['q']:
            records = records.filter(Q(title__icontains=values['q']) |
                Q(short_description__icontains=values['q']) | Q(available_roles__icontains=values['q']))
        if values['department']:
            records = records.filter(departments=values['department'])
        if values['domain']:
            records = records.filter(domain=values['domain'])
        if values['skill']:
            records = records.filter(skills=values['skill'])
        ordering = {'newest':['-created_at','-pk'], 'oldest':['created_at','pk'],
            'positions':['-open_positions','-created_at','-pk'],
            'title':[Lower('title'),'pk']}
        records = records.order_by(*ordering[values['sort'] or 'newest']).distinct()
    else:
        records = records.none()  # Invalid filters must not silently broaden a search.
    records = records.select_related('domain','creator__profile','mentor__profile').prefetch_related('departments','skills')
    page = Paginator(records,12).get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page',None)
    return {'discovery_form':form, 'page':page, 'recruiting_projects':page, 'filters_valid':valid,
        'has_filters':any(request.GET.get(key) for key in ('q','department','domain','skill')),
        'extra_query':query.urlencode()+'&' if query else ''}
