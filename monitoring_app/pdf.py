from io import BytesIO
import base64
from django.http import HttpResponse
from django.shortcuts import render, redirect, HttpResponse
from django.template.loader import get_template
from django.db.models import Q, Count
from django.db.models.functions import ExtractYear
from monitoring_app.models import *
from xhtml2pdf import pisa

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if pdf.err:
        response = HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
        content ="attachment; filename='%s'" %("over all companies report")
        response['Content-Disposition']=content
        return response
    return HttpResponse(result.getvalue(), content_type='application/pdf')

def performances_pdf(request):
    reg_year_plan = Procurement_doc.objects.filter(company__name='REG').last()
    edcl_year_plan = Procurement_doc.objects.filter(company__name='EDCL').last()
    eucl_year_plan = Procurement_doc.objects.filter(company__name='EUCL').last()

    # Initialize the result list with the header row
    companies = [['Years', 'REG', 'EDCL', 'EUCL']]
    campanies = []
    reg_stages = [['Title','Tenders']]
    edcl_stages = [['Title','Tenders']]
    eucl_stages = [['Title','Tenders']]
    value = None
    reg_all_plan = Procurement_doc.objects.filter(company__name='REG')
    edcl_all_plan = Procurement_doc.objects.filter(company__name='EDCL')
    eucl_all_plan = Procurement_doc.objects.filter(company__name='EUCL')

    reg_not_started        = Tender.objects.filter(procurement_doc=reg_year_plan, workon__isnull=True).exclude(Q(activity_status="Canceled")|Q(activity_status="CLOSED")).distinct().count()
    reg_canceled_tenders   = Tender.objects.filter(procurement_doc=reg_year_plan, activity_status="Canceled").distinct().count()
    reg_working_on         = Tender.objects.filter(procurement_doc=reg_year_plan, workon__isnull=False).exclude(Q(activity_status="Canceled")|Q(activity_status="CLOSED")).distinct().count()
    reg_contracted_tenders   = Tender.objects.filter(procurement_doc=reg_year_plan, activity_status="CLOSED").distinct().count()

    edcl_not_started        = Tender.objects.filter(procurement_doc=edcl_year_plan, workon__isnull=True).exclude(Q(activity_status="Canceled")|Q(activity_status="CLOSED")).distinct().count()
    edcl_canceled_tenders   = Tender.objects.filter(procurement_doc=edcl_year_plan, activity_status="Canceled").distinct().count()
    edcl_working_on         = Tender.objects.filter(procurement_doc=edcl_year_plan, workon__isnull=False).exclude(Q(activity_status="Canceled")|Q(activity_status="CLOSED")).distinct().count()
    edcl_contracted_tenders   = Tender.objects.filter(procurement_doc=edcl_year_plan, activity_status="CLOSED").distinct().count()
    
    eucl_not_started        = Tender.objects.filter(procurement_doc=eucl_year_plan, workon__isnull=True).exclude(Q(activity_status="Canceled")|Q(activity_status="CLOSED")).distinct().count()
    eucl_canceled_tenders   = Tender.objects.filter(procurement_doc=eucl_year_plan, activity_status="Canceled").distinct().count()
    eucl_working_on         = Tender.objects.filter(procurement_doc=eucl_year_plan, workon__isnull=False).exclude(Q(activity_status="Canceled")|Q(activity_status="CLOSED")).distinct().count()
    eucl_contracted_tenders   = Tender.objects.filter(procurement_doc=eucl_year_plan, activity_status="CLOSED").distinct().count()

    reg_info = [['REG progress','Tenders'],
               ['In Progress',reg_working_on],
               ['Not Started',reg_not_started],
               ['Canceled',reg_canceled_tenders],
               ['Contracted',reg_contracted_tenders]
               ]
    edcl_info = [['EDCL progress','Tenders'],
               ['In Progress',edcl_working_on],
               ['Not Started',edcl_not_started],
               ['Canceled',edcl_canceled_tenders],
               ['Contracted',edcl_contracted_tenders]
               ]
    eucl_info = [['EUCL progress','Tenders'],
               ['In Progress',eucl_working_on],
               ['Not Started',eucl_not_started],
               ['Canceled',eucl_canceled_tenders],
               ['Contracted',eucl_contracted_tenders]
               ]
    

    reg_late_tenders = Tender.objects.filter(procurement_doc=reg_year_plan, planned_tender_doc_preparation__lt=datetime.today().date(), activity_status__isnull=True)
    reg_today_tenders = Tender.objects.filter(procurement_doc=reg_year_plan, planned_tender_doc_preparation=datetime.today().date(), activity_status__isnull=True)
    reg_to_comes = Tender.objects.filter(procurement_doc=reg_year_plan, planned_tender_doc_preparation__gt=datetime.today().date(), activity_status__isnull=True)
    edcl_late_tenders = Tender.objects.filter(procurement_doc=edcl_year_plan, planned_tender_doc_preparation__lt=datetime.today().date(), activity_status__isnull=True)
    edcl_today_tenders = Tender.objects.filter(procurement_doc=edcl_year_plan, planned_tender_doc_preparation=datetime.today().date(), activity_status__isnull=True)
    edcl_to_comes = Tender.objects.filter(procurement_doc=edcl_year_plan, planned_tender_doc_preparation__gt=datetime.today().date(), activity_status__isnull=True)
    eucl_late_tenders = Tender.objects.filter(procurement_doc=eucl_year_plan, planned_tender_doc_preparation__lt=datetime.today().date(), activity_status__isnull=True)
    eucl_today_tenders = Tender.objects.filter(procurement_doc=eucl_year_plan, planned_tender_doc_preparation=datetime.today().date(), activity_status__isnull=True)
    eucl_to_comes = Tender.objects.filter(procurement_doc=eucl_year_plan, planned_tender_doc_preparation__gt=datetime.today().date(), activity_status__isnull=True)

    years= (
    Procurement_doc.objects
    .annotate(year=ExtractYear('timestamp'))
    .values('year')
    .order_by('-year')
                    ).distinct()
    for year in years:
        year_plan_reg = Procurement_doc.objects.filter(company__name='REG', timestamp__year=year['year']).last()
        year_plan_edcl = Procurement_doc.objects.filter(company__name='EDCL', timestamp__year=year['year']).last()
        year_plan_eucl = Procurement_doc.objects.filter(company__name='EUCL', timestamp__year=year['year']).last()

        if year_plan_reg and year_plan_edcl and year_plan_eucl:
            value = [str(year['year']), year_plan_reg.total_budget, year_plan_edcl.total_budget, year_plan_eucl.total_budget]
        elif year_plan_reg and year_plan_edcl and not year_plan_eucl:
            value = [str(year['year']), year_plan_reg.total_budget, year_plan_edcl.total_budget, 0]
        elif year_plan_reg and year_plan_eucl and not year_plan_edcl:
            value = [str(year['year']), year_plan_reg.total_budget, 0, year_plan_eucl.total_budget]
        elif year_plan_eucl and year_plan_edcl and not year_plan_reg:
            value = [str(year['year']), 0, year_plan_edcl.total_budget, year_plan_eucl.total_budget]
        elif year_plan_reg and not year_plan_eucl and not year_plan_edcl:
            value = [str(year['year']), year_plan_reg.total_budget, 0, 0]
        elif year_plan_eucl and not year_plan_edcl and not year_plan_reg:
            value = [str(year['year']), 0, 0, year_plan_eucl.total_budget]
        elif year_plan_edcl and not year_plan_reg and not year_plan_eucl:
            value = [str(year['year']), 0, year_plan_edcl.total_budget, 0]

        companies.append(value)
        campanies.append(value)

    # ============================= STAGES ==================================
    if reg_year_plan:
        for stage in reg_year_plan.over_stages_procurement.all():
            stagy =[stage.stage.title, stage.plans_on_stage.count()]
            reg_stages.append(stagy)
    
    if edcl_year_plan:
        for stage in edcl_year_plan.over_stages_procurement.all():
            stagy =[stage.stage.title, stage.plans_on_stage.count()]
            edcl_stages.append(stagy)

    if eucl_year_plan:
        for stage in eucl_year_plan.over_stages_procurement.all():
            stagy =[stage.stage.title, stage.plans_on_stage.count()]
            eucl_stages.append(stagy)

    content = {
        'reg_year_plan':reg_year_plan,
        'edcl_year_plan':edcl_year_plan,
        'eucl_year_plan':eucl_year_plan,
        'reg_late_tenders':reg_late_tenders, 
        'reg_today_tenders':reg_today_tenders,
        'reg_to_comes':reg_to_comes,
        'edcl_late_tenders':edcl_late_tenders,
        'edcl_today_tenders':edcl_today_tenders,
        'edcl_to_comes':edcl_to_comes,
        'eucl_late_tenders':eucl_late_tenders,
        'eucl_today_tenders':eucl_today_tenders,
        'eucl_to_comes':eucl_to_comes,
        'reg_info':reg_info,
        'edcl_info':edcl_info,
        'eucl_info':eucl_info,
        'reg_stages':reg_stages,
        'edcl_stages':edcl_stages,
        'eucl_stages':eucl_stages,
        'companies':companies,
    }

    return render(request, 'pdf.html', content)


# def performances_pdf(request):
#     reg_year_plan = Procurement_doc.objects.filter(company__name='REG').last()
#     edcl_year_plan = Procurement_doc.objects.filter(company__name='EDCL').last()
#     eucl_year_plan = Procurement_doc.objects.filter(company__name='EUCL').last()
#     chart_url = 'https://chart.googleapis.com/chart?cht=p&chs=250x100&chl=A|B|C&chd=t:60,40,20'
#     companies = ['REG','EDCL','EUCL']
#     amount =[]
#     years= (Procurement_doc.objects.annotate(year=ExtractYear('timestamp')).values('year').order_by('-year')).distinct()
#     for year in years:
#         year_plan_reg = Procurement_doc.objects.filter(company__name='REG', timestamp__year=year['year']).last()
#         year_plan_edcl = Procurement_doc.objects.filter(company__name='EDCL', timestamp__year=year['year']).last()
#         year_plan_eucl = Procurement_doc.objects.filter(company__name='EUCL', timestamp__year=year['year']).last()

#         if year_plan_reg and year_plan_edcl and year_plan_eucl:
#             value = [year_plan_reg.total_budget, year_plan_edcl.total_budget, year_plan_eucl.total_budget]
#         elif year_plan_reg and year_plan_edcl and not year_plan_eucl:
#             value = [year_plan_reg.total_budget, year_plan_edcl.total_budget, 0]
#         elif year_plan_reg and year_plan_eucl and not year_plan_edcl:
#             value = [year_plan_reg.total_budget, 0, year_plan_eucl.total_budget]
#         elif year_plan_eucl and year_plan_edcl and not year_plan_reg:
#             value = [0, year_plan_edcl.total_budget, year_plan_eucl.total_budget]
#         elif year_plan_reg and not year_plan_eucl and not year_plan_edcl:
#             value = [year_plan_reg.total_budget, 0, 0]
#         elif year_plan_eucl and not year_plan_edcl and not year_plan_reg:
#             value = [0, 0, year_plan_eucl.total_budget]
#         elif year_plan_edcl and not year_plan_reg and not year_plan_eucl:
#             value = [0, year_plan_edcl.total_budget, 0]

#         amount = value
#     positions = range(len(amount))
#     plt.figure(figsize=(10,5))
#     plt.bar(companies, positions)
#     # plt.yticks(positions, companies)
#     # plt.xticks(positions, companies)
#     plt.title("Budgets Over all Companies")
#     plt.xlabel("Companies")
#     plt.ylabel("Budgets")

#     # ================================= saving image =================================
#     plt.tight_layout()
#     chart = get_graph()
#     # buffer = BytesIO()
#     # plt.savefig(buffer, format='png')
#     # buffer.seek(0)
#     # image_png = buffer.getvalue()
#     # buffer.close()

#     # graphic = base64.b64encode(image_png)
#     # graphic = graphic.decode('utf-8')

#     content={
#         'chart':chart,
#     }
#     return render_to_pdf('extraction.html', content)


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph