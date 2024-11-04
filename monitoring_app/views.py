import uuid
import random
import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Q, Count
from django.db.models.functions import ExtractYear

# from monitoring_app.serializer import *

from itertools import chain
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import *
from django.contrib.auth import authenticate, login, logout
from monitoring_app.models import *
from django.contrib import messages
from tablib import Dataset
from monitoring_app.forms import *


def home(request):
    companies   = Company.objects.all()
    if request.user.is_authenticated:
        year_plan   = Procurement_doc.objects.filter(company__name="REG").first()
        departments = None
        stages      = Stage.objects.all()
        user = user_contact.objects.filter(user__id=request.user.id).first()
        if user:
            user = user_contact.objects.get(user__id=request.user.id)
            company = user.company
            if company:
                year_plan   = Procurement_doc.objects.filter(company=company.first()).last()     
        elif request.user.is_staff:
            if request.method =="POST":
                company = request.POST.get('company')
                if company != " " or company is None:
                    year_plan   = Procurement_doc.objects.filter(company__name=company).first()       
        else:
            if request.method =="POST":
                company = request.POST.get('company')
                if company != " " or company is None:
                    year_plan   = Procurement_doc.objects.filter(company__name=company).first()
                
    else:
        stages      = Stage.objects.all()
        year_plan   = Procurement_doc.objects.filter(company__name="REG").first()

    # overall_stages_calculation(year_plan)

    late_tenders = Tender.objects.filter(procurement_doc=year_plan, planned_tender_doc_preparation__lt=datetime.today().date(), activity_status__isnull=True)
    today_tenders = Tender.objects.filter(procurement_doc=year_plan, planned_tender_doc_preparation=datetime.today().date(), activity_status__isnull=True)
    to_comes = Tender.objects.filter(procurement_doc=year_plan, planned_tender_doc_preparation__gt=datetime.today().date(), activity_status__isnull=True)
    content = {
        'year_plan':year_plan,
        'stages':stages,
        'late_tenders':late_tenders, 
        'today_tenders':today_tenders, 
        'to_comes':to_comes,
        'companies':companies
    }
    return render(request, 'home.html', content)

@login_required
def progress(request):
    if request.user.is_authenticated:
        year_plan   = Procurement_doc.objects.filter(company__name="REG").first()
        user = user_contact.objects.filter(user__id=request.user.id).first()
        if user:
            company = user.company.all()
            if company:
                year_plan   = Procurement_doc.objects.filter(company=company.last()).last()

        elif request.user.is_staff:
            if request.method =="POST":
                company = request.POST.get('company')
                if company != " " or company is None:
                    year_plan   = Procurement_doc.objects.filter(company__name=company).first()      
        else:
            if request.method =="POST":
                company = request.POST.get('company')
                if company != " " or company is None:
                    year_plan   = Procurement_doc.objects.filter(company__name=company).first()            
    else:
        year_plan   = Procurement_doc.objects.filter(company__name="REG").first()
    
    # ================= charts ===============
    all_stages  = Overall_stages.objects.filter(procurement_doc=year_plan)
    unworked_on = Tender.objects.filter(procurement_doc=year_plan, tenders_on_stage__isnull=True)
    stages = [['Stages','Tenders']]
    for ov_stage in all_stages:
        stage = [ov_stage.stage.title,ov_stage.plans_on_stage.count()]
        stages.append(stage)
    
    stages.append(['UNWORKED_ON',unworked_on.count()])
    content = {
        'year_plan':year_plan,
        'stages':stages
    }
    return render(request, 'overall/progress.html', content)

@login_required
def departments(request):
    content = {}
    if request.user.is_authenticated:
        year_plan   = Procurement_doc.objects.filter(company__name="REG").first()
        user = user_contact.objects.filter(user__id=request.user.id).first()
        if user:
            user = user_contact.objects.get(user__id=request.user.id)
            company = user.company.all()
            if company:
                year_plan   = Procurement_doc.objects.filter(company=company.last()).last()     
        elif request.user.is_staff:
            if request.method =="POST":
                company = request.POST.get('company')
                if company != " " or company is None:
                    year_plan   = Procurement_doc.objects.filter(company__name=company).first()      
        else:
            if request.method =="POST":
                company = request.POST.get('company')
                if company != " " or company is None:
                    year_plan   = Procurement_doc.objects.filter(company__name=company).first()            
    else:
        year_plan   = Procurement_doc.objects.filter(company__name="REG").first()
    
    
    if year_plan:
        # ================= charts ===============
        ov_departments = Overall_department.objects.filter(year_proc=year_plan)
        all_departments = [['departments','Tenders','Total Budget']]
        xvalue = []
        yvalue = []
        p_xvalue = []
        p_yvalue = []
        colors = []
        for department in ov_departments:
            department_ = [department.department.name,department.tenders.count(), department.overall_budget]
            # label = department.department.name + " : " + str(department.tenders.count())
            # =========== Bar Chart =============
            xvalue.append(department.department.name)
            yvalue.append(department.overall_budget) 
            # ============= Pie Chart =============
            p_lable = department.department.name + ":" + str(department.committed.count())
            color = "#"+str(department.in_use_budget)
            p_xvalue.append(p_lable)
            p_yvalue.append(department.in_use_budget)
            colors.append(color)

            all_departments.append(department_)
        
        all_departments.append(['All Tenders',year_plan.plan_tenders.count(),year_plan.total_budget])
        xvalue.append('Overall')
        yvalue.append(year_plan.total_budget)
        p_xvalue.append('Overall')
        p_yvalue.append(year_plan.total_budget)
        colors.append("#"+str(year_plan.total_budget))
        content = {
            'year_plan':year_plan,
            'all_departments':all_departments,
            'yvalue':yvalue,
            'xvalue':xvalue,
            'p_xvalue':p_xvalue,
            'p_yvalue':p_yvalue,
            'colors':colors
        }
    return render(request, 'overall/departments.html', content)


def reg_progress(request):
    year_plan   = Procurement_doc.objects.filter(company__name="REG").first()
    # ================= charts ===============
    all_stages  = Overall_stages.objects.filter(procurement_doc=year_plan)
    unworked_on = Tender.objects.filter(procurement_doc=year_plan, tenders_on_stage__isnull=True)
    stages = [['Stages','Tenders']]
    for ov_stage in all_stages:
        stage = [ov_stage.stage.title,ov_stage.plans_on_stage.count()]
        stages.append(stage)
    
    stages.append(['UNWORKED_ON',unworked_on.count()])
    content = {
        'year_plan':year_plan,
        'stages':stages
    }
    return render(request, 'overall/progress.html', content)

def event_charts(request):
    # Bar chart data: Events per location
    year_plan   = Procurement_doc.objects.filter(company__name="EUCL").first()
    overall_department = Overall_department.objects.filter(year_proc=year_plan)
    departments = [["department","Budget"]]
    dxvalue = []
    dyvalue = []
    for department in overall_department:
        depart = [department.department.name,department.overall_budget]
        departments.append(depart)
        dxvalue.append(department.department.name)
        dyvalue.append(department.committed.count())
    
    content = {
        'departments':departments,
        'year_plan':year_plan,
        'dyvalue':dyvalue,
        'dxvalue':dxvalue
    }
    return render(request, 'overall/charts.html', content)


def eucl_progress(request):
    year_plan   = Procurement_doc.objects.filter(company__name="EUCL").last()
    # ================= charts ===============
    all_stages  = Overall_stages.objects.filter(procurement_doc=year_plan)
    unworked_on = Tender.objects.filter(procurement_doc=year_plan, tenders_on_stage__isnull=True)
    stages = [['Stages','Tenders']]
    for ov_stage in all_stages:
        stage = [ov_stage.stage.title,ov_stage.plans_on_stage.count()]
        stages.append(stage)
    
    stages.append(['UNWORKED_ON',unworked_on.count()])
    content = {
        'year_plan':year_plan,
        'stages':stages
    }
    return render(request, 'overall/progress.html', content)

def edcl_progress(request):
    year_plan   = Procurement_doc.objects.filter(company__name="EDCL").first()
    # ================= charts ===============
    all_stages  = Overall_stages.objects.filter(procurement_doc=year_plan)
    unworked_on = Tender.objects.filter(procurement_doc=year_plan, tenders_on_stage__isnull=True)
    stages = [['Stages','Tenders']]
    for ov_stage in all_stages:
        stage = [ov_stage.stage.title,ov_stage.plans_on_stage.count()]
        stages.append(stage)
    
    stages.append(['UNWORKED_ON',unworked_on.count()])
    content = {
        'year_plan':year_plan,
        'stages':stages
    }
    return render(request, 'overall/progress.html', content)


def performances(request):

    reg_year_plan = Procurement_doc.objects.filter(company__name='REG').last()
    edcl_year_plan = Procurement_doc.objects.filter(company__name='EDCL').last()
    eucl_year_plan = Procurement_doc.objects.filter(company__name='EUCL').last()

    # Initialize the result list with the header row
    companies = [['Years', 'REG', 'EDCL', 'EUCL']]
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
        elif year_plan_reg and not year_plan_eucl and not year_plan_edcl:
            value = [str(year['year']), year_plan_reg.total_budget, 0, 0]
        elif year_plan_eucl and year_plan_edcl and not year_plan_reg:
            value = [str(year['year']), 0, year_plan_edcl.total_budget, year_plan_eucl.total_budget]
        elif year_plan_eucl and not year_plan_edcl and not year_plan_reg:
            value = [str(year['year']), 0, 0, year_plan_eucl.total_budget]
        elif year_plan_edcl and not year_plan_reg and year_plan_eucl:
            value = [str(year['year']), 0, year_plan_edcl.total_budget, 0]
        companies.append(value)

    # ============================= STAGES ==================================
    if reg_year_plan:
        for stage in reg_year_plan.over_stages_procurement.all():
            stagy =[stage.stage.title, stage.plans_on_stage.count()]
            reg_stages.append(stagy)
    
    if edcl_year_plan:
        for stage in edcl_year_plan.over_stages_procurement.all():
            stagy =[stage.stage.title, stage.plans_on_stage.count()]
            edcl_stages.append(stagy)

    if eucl_all_plan:
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
    return render(request, 'home.html', content)


def backup_data(request):
    companies = Tender.objects.all()
    for company in companies:
        company.save(using='new_maria_db')
    return redirect('home')

# ====================================================== user ========================================

def register_user(request):
    if request.method == "POST":   
        first_name  = request.POST.get("first_name")
        last_name   = request.POST.get("last_name")
        username    = request.POST["username"]
        email       = request.POST["email"]
        password    = request.POST.get("password")
        password2   = request.POST.get("password2")
        email_exten_eucl = 'eucl.reg.rw'
        email_exten_edcl = 'edcl.reg.rw'
        email_exten_reg = 'reg.rw'
        
        if password == password2:
            user = User.objects.filter(username=username).first()
            auth_email = User.objects.filter(email=email).first()
            if user:
                content={
                    'warning':"Username taken",
                }
                return render(request, 'user/register.html',content)
            elif auth_email:
                content={
                    'warning':"Used Email",
                }
                return render(request, 'user/register.html',content)
            else:
                print(email)
                if email.endswith(email_exten_eucl) or email.endswith(email_exten_edcl) or email.endswith(email_exten_reg):
                    new_user    = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
                    new_user.save()
                    # new_user.save(using='new_maria_db')
                    return redirect('register_user_more',pk=new_user.pk)
                else:
                    content={
                        'warning':"You must use the company email like main@reg.rw",
                        }
                    return render(request, 'user/register.html',content)
        else:
            content={
            'warning':"Your passwords must match!",
        }
            return render(request, 'user/register.html',content)
    return render(request, 'user/register.html')


def register_user_more(request, pk):
    departments = Department.objects.all()
    companies = Company.objects.all()
    content={
            'head':'Contact info',
            'departments': departments,
            'companies':companies,
        }
    if request.method == "POST":
        user_id    = User.objects.filter(pk=pk).first()
        phone      = request.POST['phone']
        address    = request.POST['address']
        profile    = request.FILES.get('profile')
        companies    = request.POST.getlist('company')
        if profile:
            userinfo = user_contact.objects.create(user = user_id, Phone=phone,address=address, profile=profile)
            for company in companies:
                if company !=" ":
                    userinfo.company.add(company)
            userinfo.save()
            # new_db = userinfo.save(using='new_maria_db')
        else:
            userinfo = user_contact.objects.create(user = user_id, Phone=phone,address=address)
            for company in companies:
                if company !=" ":
                    userinfo.company.add(company)
            userinfo.save()
            # new_db = userinfo.save(using='new_maria_db')
            return redirect('user_detail', pk)
        return redirect('register_user_more', pk)
    return render(request, 'user/info.html',content)

def user_list(request):
    users = User.objects.all()
    content = {
        'users':users
    }
    return render(request, 'user/list.html', content)

def user_detail(request, pk):
    user = User.objects.filter(pk=pk).first()
    if user:
        content = {
            'user':user,
        }
    else:
        content ={
        'warning':"User not found"
        }
    return render(request, 'user/detail.html', content)


# ==============================================Authentication====================================

def login_in(request):
    if request.user.is_authenticated:
        return redirect('home')
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if '@' in username:
            user = User.objects.filter(email=username).first()
            by_email = authenticate(request, username=user.username, password=password)
            if by_email is not None:
                login(request, by_email)
                next=""
                if "next" in request.GET:
                    next = request.GET["next"]
                    return redirect(next)
                if next == None or next == "" :
                    next = "/"
                    return redirect(next)
        
        elif username:
            user = User.objects.filter(username=username).first()
            if user:
                by_username = authenticate(request, username=user.username, password=password)
                if by_username is not None:
                    login(request, by_username)
                    next=""
                    if "next" in request.GET:
                        next = request.GET["next"]
                        return redirect(next)
                    if next == None or next == "" :
                        next = "/"
                        return redirect(next)
            else:
                user = User.objects.filter(username=username.lower()).first()
                if user:
                    by_username = authenticate(request, username=user.username, password=password)
                    if by_username is not None:
                        login(request, by_username)
                        next=""
                        if "next" in request.GET:
                            next = request.GET["next"]
                            return redirect(next)
                        if next == None or next == "" :
                            next = "/"
                            return redirect(next)
                else:
                    content={
                            'warning':"Invalid username/password",
                        }
                    return render(request, 'user/login.html',content)
        else:
            content={
                'warning':"Invalid username/password",
                }
            return render(request, 'user/login.html',content)
    else:
        name=''
    return render(request, 'user/login.html')

def logingout(request):
    logout(request)
    return redirect('/')

# ============================================= document ===========================================

@login_required
def document_upload(request):
    user = User.objects.get(id=request.user.id)
    
    if request.method == "POST":
        dataset  = Dataset()
        new_plan = request.FILES['files']
        title    = request.POST['title']
        if not new_plan.name.endswith('xlsx'):
            messages.info(request,'Wrong format')
            return render(request,'procurement/plans.html')
        elif new_plan.name.endswith('xlsx'):
            imported_data = dataset.load(new_plan.read(), format='xlsx')
            document = Procurement_doc.objects.create(user=user, title=title, files=new_plan, company=user.user_info.company.first())
            # new_db = document.save(using='new_maria_db')
            for data in imported_data:
                if data[0] == " " or data[0]=="department" or data[0] =="depart":
                    pass
                elif data[1]==" " or data[1] is None or data[0]==" " or data[0] is None or data[3] == "Estimated  cost in RWF":
                    pass
                else:
                    department = data[0]
                    activity_id = data[1]
                    activity_description = data[2]
                    estimated_cost = data[3]
                    source_of_fund = data[4]
                    if data[5]:
                        tendering_method = Method.objects.filter(name__contains=str(data[5])).first()
                    tender_date     = data[6]
                    publication_date = data[7]
                    bid_opening_date = data[8]
                    start_evaluation = data[9]
                    end_evaluation = data[10]
                    final_notification = data[11]
                    contract_signing_date = data[12]
                    if activity_id and department and source_of_fund and document:
                        plan_department = Department.objects.filter(name=department)
                        if plan_department.first():
                            check_existance = Tender.objects.filter(activity_id=activity_id, procurement_doc=document, department=plan_department.first(),source_of_fund=source_of_fund).first()
                            if check_existance:
                                pass
                            else:
                                procurement  = Tender.objects.create(
                                    procurement_doc   = document,
                                    department      = plan_department.first(),
                                    activity_id     = activity_id,
                                    activity_description = activity_description,
                                    estimated_cost  = estimated_cost,
                                    source_of_fund  = source_of_fund,
                                    tendering_method = tendering_method,
                                    planned_tender_doc_preparation = tender_date,
                                    planned_publication_date = publication_date,
                                    planned_bid_opening_date = bid_opening_date, 
                                    planned_start_evaluation = start_evaluation,
                                    planned_end_evaluation = end_evaluation,
                                    planned_provisional_notification_date = final_notification,
                                    planned_contract_signing_date = contract_signing_date
                                )
                                # backup_db = procurement.save(using='new_maria_db')
                                report = Plan_tenders_report.objects.create(
                                    tender = procurement,
                                    procurement_doc   = document,
                                    department      = plan_department.first(),
                                    activity_id     = activity_id,
                                    activity_description = activity_description,
                                    estimated_cost  = estimated_cost,
                                    source_of_fund  = source_of_fund,
                                    tendering_method = tendering_method,
                                    planned_tender_doc_preparation = tender_date,
                                    planned_publication_date = publication_date,
                                    planned_bid_opening_date = bid_opening_date, 
                                    planned_start_evaluation = start_evaluation,
                                    planned_end_evaluation = end_evaluation,
                                    planned_provisional_notification_date = final_notification,
                                    planned_contract_signing_date = contract_signing_date
                                )
                                # backup_db = report.save(using='new_maria_db')
                        else:
                            plan_department = Department.objects.create(name=department)
                            # backup_db = plan_department.save(using='new_maria_db')
                            check_existance = Tender.objects.filter(activity_id=activity_id, procurement_doc=document,department=plan_department,source_of_fund=source_of_fund).first()
                            if check_existance:
                                pass
                            else:
                                value  = Tender.objects.create(
                                    procurement_doc   = document,
                                    department      = plan_department,
                                    activity_id     = activity_id,
                                    activity_description = activity_description,
                                    estimated_cost  = estimated_cost,
                                    source_of_fund  = source_of_fund,
                                    tendering_method = tendering_method,
                                    planned_tender_doc_preparation = tender_date,
                                    planned_publication_date = publication_date,
                                    planned_bid_opening_date = bid_opening_date, 
                                    planned_start_evaluation = start_evaluation,
                                    planned_end_evaluation  = end_evaluation,
                                    planned_provisional_notification_date = final_notification,
                                    planned_contract_signing_date = contract_signing_date
                                )
                                # backup_db = value.save(using='new_maria_db')
                                report = Plan_tenders_report.objects.create(
                                    tender = value,
                                    procurement_doc   = document,
                                    department      = plan_department,
                                    activity_id     = activity_id,
                                    activity_description = activity_description,
                                    estimated_cost  = estimated_cost,
                                    source_of_fund  = source_of_fund,
                                    tendering_method = tendering_method,
                                    planned_tender_doc_preparation = tender_date,
                                    planned_publication_date = publication_date,
                                    planned_bid_opening_date = bid_opening_date, 
                                    planned_start_evaluation = start_evaluation,
                                    planned_end_evaluation = end_evaluation,
                                    planned_provisional_notification_date = final_notification,
                                    planned_contract_signing_date = contract_signing_date
                                )
                                # backup_db = value.save(using='new_maria_db')
            all_tenders = Tender.objects.all()
            overall_departments_creation(document)
        return redirect('procurement_plan_detail', document.pk)
    return redirect('procurement_plans_list')


def tender_republish(request, pk):
    tender = Tender.objects.get(id=pk)
    time_zero = timedelta(days=0, hours=0, minutes=0, seconds=0)
    departments = Department.objects.all()
    methods = Method.objects.all()
    now = str(datetime.today().date())
    if request.method == "POST":
        department = request.POST.get('department')
        tend_method = request.POST.get('method')
        source = request.POST.get('source')
        estim_cost = request.POST.get('estim_cost')
        approved = request.POST.get('approved')
        doc_preparation = request.POST.get('doc_preparation')
        publication = request.POST.get('publication')
        opening = request.POST.get('opening')
        start_eval = request.POST.get('start_eval')
        end_eval = request.POST.get('end_eval')
        prov_noti = request.POST.get('prov_noti')
        fin_noti = request.POST.get('fin_noti')
        contract_man = request.POST.get('contract_man')
        contract_sign = request.POST.get('contract_sign')
        contract_end = request.POST.get('contract_end')
        if tender.activity_status.upper() == "REMOVED" or tender.activity_status.upper() == "CANCELED":
            if approved:
                department = Department.objects.filter(id=department).first()
                method = Method.objects.get(id=tend_method)
                republished = Tender_republished.objects.create(tender=tender, department=tender.department, procurement_doc=tender.procurement_doc, activity_id=tender.activity_id, activity_description=tender.activity_description)
                report = Plan_tenders_report.objects.create(tender_republish = republished,procurement_doc = tender.procurement_doc,department = department,activity_id = tender.activity_id,activity_description = tender.activity_description)
                republished.source_of_fund = source
                report.source_of_fund  = source
                republished.estimated_cost = estim_cost
                report.estimated_cost  = estim_cost
                republished.tendering_method = method
                report.tendering_method = method
                republished.released_date = datetime.today()
                if doc_preparation:
                    republished.planned_tender_doc_preparation = datetime.strptime(doc_preparation, '%Y-%M-%d')
                    report.planned_tender_doc_preparation = datetime.strptime(doc_preparation, '%Y-%M-%d')
                if publication:
                    republished.planned_publication_date = datetime.strptime(publication, '%Y-%M-%d')
                    report.planned_publication_date = datetime.strptime(publication, '%Y-%M-%d')
                if opening:
                    republished.planned_bid_opening_date = datetime.strptime(opening, '%Y-%M-%d')
                    report.planned_bid_opening_date = datetime.strptime(opening, '%Y-%M-%d')
                if start_eval:
                    republished.planned_start_evaluation = datetime.strptime(start_eval, '%Y-%M-%d')
                    report.planned_start_evaluation = datetime.strptime(start_eval, '%Y-%M-%d')
                if end_eval:
                    republished.planned_end_evaluation = datetime.strptime(end_eval, '%Y-%M-%d')
                    report.planned_end_evaluation = datetime.strptime(end_eval, '%Y-%M-%d')
                if prov_noti:
                    republished.planned_provisional_notification_date = datetime.strptime(prov_noti, '%Y-%M-%d')
                    report.planned_provisional_notification_date = datetime.strptime(prov_noti, '%Y-%M-%d')
                if fin_noti:
                    republished.planned_final_notification_date = datetime.strptime(fin_noti, '%Y-%M-%d')
                    report.planned_final_notification = datetime.strptime(fin_noti, '%Y-%M-%d')
                # if contract_man:
                    # republished.planned_contract_management_start_date = datetime.strptime(contract_man, '%Y-%M-%d')
                    # report.planned_contract_management_start_date = datetime.strptime(contract_man, '%Y-%M-%d')
                if contract_sign:
                    republished.planned_contract_signing_date = datetime.strptime(contract_sign, '%Y-%M-%d')
                    report.planned_contract_signing_date = datetime.strptime(contract_sign, '%Y-%M-%d')
                # if contract_end:
                    # republished.planned_contract_end_date = datetime.strptime(contract_end, '%Y-%M-%d')
                    # report.planned_contract_end_date = datetime.strptime(contract_end, '%Y-%M-%d')
                republished.save()
                report.save()
            return redirect('republished_detail', republished.pk)
        return redirect('republish', tender.pk)
    content ={
        'tender':tender,
        'departments':departments,
        'methods':methods,
        'time_zero':time_zero,
        'now':now,
        }
    return render(request,'procurement/republish.html', content)

def republished_detail(request,pk):
    tender = Tender_republished.objects.get(id=pk)
    time_zero = timedelta(days=0, hours=0, minutes=0, seconds=0)
    content ={
        'tender':tender,
        'time_zero':time_zero
    }
    return render(request,'procurement/republished_details.html', content)

def all_plans(request):
    proc_files = Procurement_doc.objects.all()
    content = {
            'proc_files':proc_files
        }
    return render(request, 'procurement/plans.html', content)

@login_required
def procurement_plan_list(request):
    user = User.objects.get(id=request.user.id)
    proc_files = Procurement_doc.objects.filter(company=user.user_info.company.last())
    content = {
            'proc_files':proc_files
        }
    return render(request, 'procurement/plans.html', content)


def procurement_plan_detail(request,pk):
    plan = Procurement_doc.objects.get(id=pk)
    plan_tenders = Tender.objects.filter(procurement_doc=plan)
    republished = Tender_republished.objects.filter(procurement_doc=plan)
    stage = Stage.objects.first()
    time_zero = timedelta(days=0)
    content ={
        'plan':plan,
        'plan_tenders':plan_tenders,
        'republished':republished,
        'stage':stage,
        'time_zero':time_zero
        }
    return render(request, 'procurement/plan.html', content )

def tenders(request):
    time_zero = timedelta(days=0)
    if request.user.is_authenticated:
        user = user_contact.objects.filter(user__id=request.user.id).first()
        if user:
            company = user.company
            if company:
                year_plan   = Procurement_doc.objects.filter(company=company.first()).last()
    tenders = Tender.objects.filter(procurement_doc=year_plan).exclude(Q(activity_status="CANCELED")|Q(activity_status="CLOSED")).all()
    republished = Tender_republished.objects.filter(procurement_doc=year_plan,).exclude(Q(activity_status="CANCELED")|Q(activity_status="CLOSED")).all()
    content ={
        'plan_tenders':tenders,
        'republished':republished,
        'time_zero':time_zero,
        }
    return render(request, 'procurement/plan.html', content )


def tender_detail(request, pk):
    tender = Tender.objects.get(id=pk)
    time_zero = timedelta(days=0, hours=0, minutes=0, seconds=0)
    content ={
        'tender':tender,
        'time_zero':time_zero
    }
    return render(request,'procurement/tender_details.html', content)

def procurement_plan_deletion(request, pk):
    plan = Procurement_doc.objects.get(id=pk)
    plan.delete()
    return redirect('procurement_plans_list')


def late_tenders(request, pk):
    year_plan = Procurement_doc.objects.get(id=pk)
    late_tenders = Tender.objects.filter(procurement_doc=year_plan, planned_tender_doc_preparation__lt=datetime.today().date(), activity_status__isnull=True)
    stage = Stage.objects.first()
    time_zero = timedelta(days=0)
    content ={
        'plan':year_plan,
        'plan_tenders':late_tenders,
        'stage':stage,
        'time_zero':time_zero
        }
    return render(request, 'procurement/plan.html', content )

def today_tenders(request, pk):
    year_plan = Procurement_doc.objects.get(id=pk)
    today_tenders = Tender.objects.filter(procurement_doc=year_plan, planned_tender_doc_preparation=datetime.today().date(), activity_status__isnull=True)
    stage = Stage.objects.first()
    time_zero = timedelta(days=0)
    content ={
        'plan':year_plan,
        'plan_tenders':today_tenders,
        'stage':stage,
        'time_zero':time_zero
        }
    return render(request, 'procurement/plan.html', content)

def to_come_tenders(request, pk):
    year_plan = Procurement_doc.objects.get(id=pk)
    to_comes = Tender.objects.filter(procurement_doc=year_plan, planned_tender_doc_preparation__gt=datetime.today().date(), activity_status__isnull=True)
    stage = Stage.objects.first()
    time_zero = timedelta(days=0)
    content ={
        'plan':year_plan,
        'plan_tenders':to_comes,
        'stage':stage,
        'time_zero':time_zero
        }
    return render(request, 'procurement/plan.html', content)


@login_required
def tender_update(request, pk):
    next_url = request.GET.get('next', '/')
    user    = User.objects.get(id=request.user.id)
    doc     = Procurement_doc.objects.get(id=pk)
    if request.method == "POST":
        tender_id = request.POST['tender']
        today_date = datetime.today() # was close_date
        process = request.POST.get('process')
        files = request.FILES.getlist('files')
        tender = Tender.objects.get(id=tender_id)
        current_proced  = tender.workon.last()
        if not current_proced:
            if process=="next":
                method_duration = tender.tendering_method.method_duration.all().order_by('stage__number').first()
                first_stage     = method_duration.stage
                procedure       = Procedure.objects.create(user=user, proc_item=tender, procurement_doc=tender.procurement_doc, stage=first_stage, status=first_stage.title)
                procedure.timestamp = today_date.astimezone()
                procedure.save()
                if files:
                    for file in files:
                        procedure_file.objects.create(procedure=procedure, files=file)
                tender.activity_status     = first_stage.title
                tender.save()
                actuals(item=tender, next_stage=procedure)
                tender_forwarding(tender)
                for_all_stages(year_plan=doc)
            if next_url:
                return redirect(next_url)   
            else: 
                return redirect('procurement_plan_detail', doc.pk)

        elif current_proced.stage:
            current_stage = current_proced.stage
            duration = tender.tendering_method.method_duration.filter(stage=current_stage).first()
            if process == "next":
                next_stage  = tender.tendering_method.method_duration.filter(stage__number__gt=current_stage.number).order_by('stage__number').first()
                if next_stage:
                    print(next_stage.stage)
                    tender_forwarding(tender, current_stage)
                    procedure       = Procedure.objects.create(user=user, proc_item=tender, procurement_doc=tender.procurement_doc, stage=next_stage.stage, status=next_stage.stage.title)
                    if files:
                        for file in files:
                            procedure_file.objects.create(procedure=procedure, files=file)
                    tender.activity_status     = next_stage.stage.title
                    tender.save()
                    # to update closed_date & time_taken going to the next stage 
                    current_proced.closed_date = today_date.astimezone()

                    time_taken = today_date.astimezone() - current_proced.timestamp
                    current_proced.time_taken = time_taken
                    # calculation of late between actual time and time used
                    if duration.delay <= current_proced.time_taken:
                        current_proced.late = current_proced.time_taken - duration.delay
                            
                    elif current_proced.time_taken >= duration.delay:
                        current_proced.late = current_proced.time_taken - duration.delay

                    current_proced.save()
                    actuals(item=tender, current_proced=current_proced ,next_stage=procedure)
                    all_tenders_stage(tender=tender)
                    
                    if next_url:
                        return redirect(next_url)   
                    else: 
                        return redirect('procurement_plan_detail', doc.pk)
                else:
                    tender.activity_status     = "CLOSED"
                    tender.save()
                    if today_date:
                        current_proced.closed_date = today_date.astimezone()
                        time_taken = today_date.astimezone() - current_proced.timestamp
                        current_proced.time_taken = time_taken
                        current_proced.status = "CLOSED"
                        overall_department_committed(tender)
                        if current_proced.time_taken >= duration.delay:
                            current_proced.late = current_proced.time_taken - duration.delay

                    else:
                        current_proced.closed_date = datetime.now()
                        time_taken = datetime.now().astimezone() - current_proced.timestamp
                        current_proced.time_taken = time_taken
                        current_proced.status = "CLOSED"
                        overall_department_committed(tender)
                        if current_proced.time_taken >= duration.delay:
                            current_proced.late = current_proced.time_taken - duration.delay

                    current_proced.save()
                    actuals(item=tender, current_proced=current_proced)
                    all_tenders_stage(tender=tender)
                    
                    if next_url:
                        return redirect(next_url)   
                    else: 
                        return redirect('procurement_plan_detail', doc.pk)
            return redirect('procurement_plan_detail', doc.pk)
    return redirect('procurement_plan_detail', doc.pk)

def republished_tender_update(request, pk):
    next_url = request.GET.get('next', '/')
    user    = User.objects.get(id=request.user.id)
    doc     = Procurement_doc.objects.get(id=pk)
    if request.method == "POST":
        tender_id = request.POST['tender']
        today_date = datetime.today() # was close_date
        process = request.POST.get('process')
        files = request.FILES.getlist('files')
        tender = Tender_republished.objects.get(id=tender_id)
        current_proced  = tender.workon.last()
        if not current_proced:
            if process=="next":
                method_duration = tender.tendering_method.method_duration.all().order_by('stage__number').first()
                first_stage     = method_duration.stage
                procedure       = Procedure.objects.create(user=user, republished_item=tender, procurement_doc=tender.procurement_doc, stage=first_stage, status=first_stage.title)
                procedure.timestamp = today_date.astimezone()
                procedure.save()
                if files:
                    for file in files:
                        procedure_file.objects.create(procedure=procedure, files=file)
                tender.activity_status     = first_stage.title
                tender.save()
                republished_actuals(item=tender, next_stage=procedure)
                # republished_tender_forwarding(tender)
                for_all_stages(year_plan=doc)
            if next_url:
                return redirect(next_url)   
            else: 
                return redirect('procurement_plan_detail', doc.pk)

        elif current_proced.stage:
            current_stage = current_proced.stage
            duration = tender.tendering_method.method_duration.filter(stage=current_stage).first()
            if process == "next":
                next_stage  = tender.tendering_method.method_duration.filter(stage__number__gt=current_stage.number).order_by('stage__number').first()
                if next_stage:
                    print(next_stage.stage)
                    # republished_tender_forwarding(tender, current_stage)
                    procedure       = Procedure.objects.create(user=user, republished_item=tender, procurement_doc=tender.procurement_doc, stage=next_stage.stage, status=next_stage.stage.title)
                    if files:
                        for file in files:
                            procedure_file.objects.create(procedure=procedure, files=file)
                    tender.activity_status     = next_stage.stage.title
                    tender.save()
                    # to update closed_date & time_taken going to the next stage 
                    current_proced.closed_date = today_date.astimezone()

                    time_taken = today_date.astimezone() - current_proced.timestamp
                    current_proced.time_taken = time_taken
                    # calculation of late between actual time and time used
                    if duration.delay <= current_proced.time_taken:
                        current_proced.late = current_proced.time_taken - duration.delay
                            
                    elif current_proced.time_taken >= duration.delay:
                        current_proced.late = current_proced.time_taken - duration.delay

                    current_proced.save()
                    republished_actuals(item=tender, current_proced=current_proced ,next_stage=procedure)
                    all_tenders_stage(tender=tender)
                    
                    if next_url:
                        return redirect(next_url)   
                    else: 
                        return redirect('procurement_plan_detail', doc.pk)
                else:
                    tender.activity_status     = "CLOSED"
                    tender.save()
                    if today_date:
                        current_proced.closed_date = today_date.astimezone()
                        time_taken = today_date.astimezone() - current_proced.timestamp
                        current_proced.time_taken = time_taken
                        current_proced.status = "CLOSED"
                        overall_republished_department_committed(tender)
                        if current_proced.time_taken >= duration.delay:
                            current_proced.late = current_proced.time_taken - duration.delay

                    else:
                        current_proced.closed_date = datetime.now()
                        time_taken = datetime.now().astimezone() - current_proced.timestamp
                        current_proced.time_taken = time_taken
                        current_proced.status = "CLOSED"
                        overall_republished_department_committed(tender)
                        if current_proced.time_taken >= duration.delay:
                            current_proced.late = current_proced.time_taken - duration.delay

                    current_proced.save()
                    republished_actuals(item=tender, current_proced=current_proced)
                    all_tenders_stage(tender=tender)
                    
                    if next_url:
                        return redirect(next_url)   
                    else: 
                        return redirect('procurement_plan_detail', doc.pk)
            return redirect('procurement_plan_detail', doc.pk)
    return redirect('procurement_plan_detail', doc.pk)

def remove_tender(request, pk):
    next_url = request.GET.get('next', '/')
    tender = Tender.objects.get(id=pk)
    tender.activity_status = "Removed"
    tender.tender_report.activity_status = "Removed"
    tender.removed = datetime.now().astimezone()
    tender.save()
    current_proced  = tender.workon.last()
    if current_proced:
        current_proced.closed_date = tender.canceled
        current_proced.save()
    if next_url:
        return redirect(next_url)
    else:
        return redirect('tender_detail', pk)
    
def remove_tender(request, pk):
    next_url = request.GET.get('next', '/')
    tender = Tender.objects.get(id=pk)
    tender.activity_status = "Removed"
    tender.tender_report.activity_status = "Removed"
    tender.removed = datetime.now().astimezone()
    tender.save()
    current_proced  = tender.workon.last()
    if current_proced:
        current_proced.closed_date = tender.canceled
        current_proced.save()
    if next_url:
        return redirect(next_url)
    else:
        return redirect('tender_detail', pk)

def cancel_tender(request, pk):
    next_url = request.GET.get('next', '/')
    tender = Tender.objects.get(id=pk)
    tender.activity_status = "Canceled"
    tender.canceled = datetime.now().astimezone()
    tender.save()
    # tender.save(using='new_maria_db')
    current_proced  = tender.workon.last()
    if current_proced:
        current_proced.closed_date = tender.canceled
        current_proced.save()
        # current_proced.save(using='new_maria_db')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('tender_detail', pk)


# ======================================== Stages ======================================

@login_required
def create_stages(request):
    stageform = stage_form()
    user = User.objects.get(id=request.user.id)
    stages = Stage.objects.all()
    content = {
        'stages':stages,
        'stageform':stageform
    }
    if request.method == "POST":
        title = request.POST['title']
        number = request.POST['number']
        stageform = stage_form(request.POST, request.FILES or None)
        if stageform.is_valid():
            if user is not None:
                stage = stageform.save(commit=False)
                stage.title = title
                stage.number = number
                stage.user = user
                stage.save()
                # stage.save(using='new_maria_db')
            content = {
                'warning':'succesful registered.',
                'stages':stages,
                'stageform':stageform
            }
        return render(request, 'stage/stages.html', content)
    return render(request, 'stage/stages.html',content)

@login_required
def stage_update(request, pk):
    stage = Stage.objects.get(id=pk)
    if request.method == "POST":
        title = request.POST['title']
        number = request.POST['number']
        stage.number = number
        stage.title = title.upper()
        stageform = stage_form(request.POST, instance=stage)
        if stageform.is_valid():
            stageform.save()
        stage.title = title.upper()
        stage.number = number
        stage.save()
        # stage.save(using='new_maria_db')
        return redirect('stage_creation')
    return redirect('stage_creation')

@login_required
def stage_delete(request, pk):
    stage = Stage.objects.get(id=pk)
    stage.delete()
    return redirect('stage_creation')


# ========================================== Method =====================================

def create_method(request):
    methods = Method.objects.all()
    stages = Stage.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        method = Method.objects.create(name=name.upper(), description=description)
        # backup_db = method.save(using='new_maria_db')
    content ={
        'methods':methods,
        'stages':stages
    }
    return render(request, 'method/method.html',content)

def method_delete(request, pk):
    method = Method.objects.get(id=pk)
    method.delete()
    return redirect('create_method')

def method_update(request, pk):
    method = Method.objects.get(id=pk)
    if request.method =="POST":
        name = request.POST['name']
        description = request.POST['description']
        method.name = name.upper()
        method.description = description 
        method.save()
        # method.save(using='new_maria_db')
    return redirect('create_method')

def duration_registration(request, pk):
    method = Method.objects.get(id=pk)
    
    if request.method == "POST":
        stage_id   = request.POST['stage']
        # months  = request.POST['months']
        days    = request.POST['days']
        hours   = request.POST['hours']
        if stage_id:
            stage = Stage.objects.get(id=int(stage_id))
            exist = method.method_duration.filter(stage=stage).first()
            if exist:
                return redirect('create_method')
            else:
                
                if stage and days and hours:
                    dur = Duration.objects.create(stage=stage,method=method, delay=timedelta(days=int(days),hours=int(hours)))
                    # backup_db = dur.save(using='new_maria_db')
                # if stage and months and days and hours:
                #     Duration.objects.create(stage=stage,method=method, delay=timedelta(months=int(months),days=int(days),hours=int(hours)))
                # elif stage and months and days:
                #     Duration.objects.create(stage=stage,method=method, delay=timedelta(months=int(months),days=int(days)))
                # elif stage and months and hours:
                #     Duration.objects.create(stage=stage,method=method, delay=timedelta(months=int(months),hours=int(hours)))
                # elif stage and months:
                #     Duration.objects.create(stage=stage,method=method, delay=timedelta(months=int(months)))
                elif stage and days:
                    dur = Duration.objects.create(stage=stage,method=method, delay=timedelta(days=int(days)))
                    # backup_db = dur.save(using='new_maria_db')
                elif stage and hours:
                    dur = Duration.objects.create(stage=stage,method=method, delay=timedelta(hours=int(hours)))
                    # backup_db = dur.save(using='new_maria_db')
            return redirect('create_method')
    return redirect('create_method')


def duration_delete(request, pk):
    duration = Duration.objects.get(id=pk)
    duration.delete()
    return redirect('create_method') 

# ==================================================overall================================================

def overall_stage_detail(request, pk):
    over_stage = Overall_stages.objects.get(id=pk)
    year_plan = over_stage.procurement_doc
    to_comes = over_stage.plans_on_stage.all()
    stage = over_stage.stage
    time_zero = timedelta(days=0)
    content ={
        'plan':year_plan,
        'plan_tenders':to_comes,
        'stage':stage,
        'time_zero':time_zero
        }
    return render(request, 'procurement/plan.html', content)

def overall_department_detail(request, pk):
    over_department = Overall_department.objects.get(id=pk)
    year_plan = over_department.year_proc
    to_comes = over_department.tenders
    # stage = over_department.stage
    time_zero = timedelta(days=0)
    content ={
        'plan':year_plan,
        'plan_tenders':to_comes,
        # 'stage':stage,
        'time_zero':time_zero
        }
    return render(request, 'procurement/plan.html', content)

# ************************department**************************

def overall_departments_creation(document):
    proc_tenders = document.plan_tenders.values('department').distinct()
    tenders_total_budget = 0
    for tender in proc_tenders:
        department  = Department.objects.get(id=tender['department'])
        depart      = Overall_department.objects.create(year_proc=document, department=department)
        # backup_db = depart.save(using='new_maria_db')
    all_departments = Overall_department.objects.filter(year_proc=document)
    for o_department in all_departments:
        total_budget = 0
        tenders = Tender.objects.filter(procurement_doc=document, department=o_department.department)
        for tender in tenders:
            total_budget = total_budget + tender.estimated_cost
            o_department.tenders.add(tender)
        o_department.all_items = o_department.tenders.count()
        o_department.overall_budget = total_budget
        o_department.save()
        # backup_db = o_department.save(using='new_maria_db')
        tenders_total_budget = tenders_total_budget + o_department.overall_budget
    document.total_budget = tenders_total_budget
    document.save()
    # document.save(using='new_maria_db')
    for o_department in all_departments:
        o_department.overall_budget_perc = (o_department.overall_budget * 100)/document.total_budget
        o_department.save()
        # backup_db = o_department.save(using='new_maria_db')

def overall_department_committed(tender):
    overall_department = Overall_department.objects.filter(year_proc=tender.procurement_doc, department=tender.department).first()
    if overall_department:
        overall_department.committed.add(tender)
        budget = 0
        nom_tenders = overall_department.committed.all()
        rep_tenders = overall_department.rep_committed.all()
        tenders = nom_tenders|rep_tenders
        for tend in tenders:
            budget = budget + tend.estimated_cost
        overall_department.in_use_budget = budget
        overall_department.percent = (overall_department.in_use_budget * 100)/overall_department.overall_budget
        overall_department.save()

def overall_republished_department_committed(tender):
    overall_department = Overall_department.objects.filter(year_proc=tender.procurement_doc, department=tender.department).first()
    if overall_department:
        overall_department.rep_committed.add(tender)
        budget = 0
        nom_tenders = overall_department.committed.all()
        rep_tenders = overall_department.rep_committed.all()
        tenders = chain(nom_tenders,rep_tenders)
        for tend in tenders:
            budget = budget + tend.estimated_cost
        overall_department.in_use_budget = budget
        overall_department.percent = (overall_department.in_use_budget * 100)/overall_department.overall_budget
        overall_department.save()


# ******************************Section***************************

def tender_forwarding(tender, current_stage = None):
    year_plan = tender.procurement_doc
    current_procedure = tender.workon.last()
    if current_procedure:
        current_stage           = current_procedure.stage
        current_overall_stage   = Overall_stages.objects.filter(procurement_doc=year_plan,stage=current_stage).first()
        next_stage              = tender.tendering_method.method_duration.filter(stage__number__gt=current_stage.number).order_by('stage__number').first()
        if next_stage:
            next_overall_stage   = Overall_stages.objects.filter(procurement_doc=year_plan,stage=next_stage.stage).first()
            if next_overall_stage:
                current_overall_stage.plans_on_stage.remove(tender)
                current_overall_stage.save()
                next_overall_stage.plans_on_stage.add(tender)
                next_overall_stage.save()
            else:
                next_overall_stage = Overall_stages.objects.create(procurement_doc=year_plan,stage=next_stage.stage)
                next_overall_stage.plans_on_stage.add(tender)
                next_overall_stage.save()
                if current_overall_stage:
                    current_overall_stage.plans_on_stage.remove(tender)
                    current_overall_stage.save()
            all_tenders_stage(tender)
        else:
            pass
    else:
        first_stage     = Stage.objects.all().order_by('number').first()
        overall_stage   = Overall_stages.objects.filter(procurement_doc=year_plan,stage=first_stage).first()
        if overall_stage:
            overall_stage.plans_on_stage.add(tender)
            overall_stage.save()
            # backup_db = overall_stage.save(using='new_maria_db')
        else:
            overall_stage = Overall_stages.objects.create(procurement_doc=year_plan,stage=first_stage)
            overall_stage.plans_on_stage.add(tender)
            overall_stage.save()
            # backup_db = overall_stage.save(using='new_maria_db')


def republished_tender_forwarding(tender, current_stage = None):
    year_plan = tender.procurement_doc
    current_procedure = tender.workon.last()
    if current_procedure:
        current_stage           = current_procedure.stage
        current_overall_stage   = Overall_stages.objects.filter(procurement_doc=year_plan,stage=current_stage).first()
        next_stage              = tender.tendering_method.method_duration.filter(stage__number__gt=current_stage.number).order_by('stage__number').first()
        if next_stage:
            next_overall_stage   = Overall_stages.objects.filter(procurement_doc=year_plan,stage=next_stage.stage).first()
            if next_overall_stage:
                
                current_overall_stage.republished_on_stage.remove(tender)
                current_overall_stage.save()
                # backup_db = current_overall_stage.save(using='new_maria_db')
                next_overall_stage.republished_on_stage.add(tender)
                next_overall_stage.save()
                # backup_db = next_overall_stage.save(using='new_maria_db')
            else:
                next_overall_stage = Overall_stages.objects.create(procurement_doc=year_plan,stage=next_stage.stage)
                next_overall_stage.republished_on_stage.add(tender)
                next_overall_stage.save()
                # backup_db = next_overall_stage.save(using='new_maria_db')
                if current_overall_stage:
                    current_overall_stage.republished_on_stage.remove(tender)
                    current_overall_stage.save()
                    # backup_db = current_overall_stage.save(using='new_maria_db')
            all_tenders_stage(tender)
        else:
            pass
    else:
        first_stage     = Stage.objects.all().order_by('number').first()
        overall_stage   = Overall_stages.objects.filter(procurement_doc=year_plan,stage=first_stage).first()
        if overall_stage:
            overall_stage.republished_on_stage.add(tender)
            overall_stage.save()
            # backup_db = overall_stage.save(using='new_maria_db')
        else:
            overall_stage = Overall_stages.objects.create(procurement_doc=year_plan,stage=first_stage)
            overall_stage.republished_on_stage.add(tender)
            overall_stage.save()
            # backup_db = overall_stage.save(using='new_maria_db')


def all_tenders_stage(tender):
    year_plan = tender.procurement_doc
    current_stage = tender.workon.last().stage
    in_tenders = Tender.objects.filter(procurement_doc=year_plan).exclude(Q(activity_status="Canceled")|Q(activity_status="Removed"))
    in_republished = Tender_republished.objects.filter(procurement_doc=year_plan).exclude(Q(activity_status="Canceled")|Q(activity_status="Removed"))
    all_tenders = in_tenders.values_list('activity_id','activity_description').union(in_republished.values_list('activity_id','activity_description')).count()
    over_stage  = Overall_stages.objects.filter(procurement_doc=year_plan,stage=current_stage).first()
    if over_stage:
        tenders = over_stage.plans_on_stage.all().exclude(activity_status="Canceled")
        republishes = over_stage.republished_on_stage.all().exclude(activity_status="Canceled")
        new_duration = timedelta(days=0)
        actual_duration = timedelta(days=0)
        for tender in tenders:
            tender_last_proce = tender.workon.filter(procurement_doc=year_plan).exclude(time_taken=timedelta(days=0)).last()
            if tender_last_proce:
                if tender_last_proce.stage == current_stage:
                    new_duration = new_duration + tender_last_proce.time_taken
        
        for republish in republishes:
            republish_last_proce = republish.workon.filter(procurement_doc=year_plan).exclude(time_taken=timedelta(days=0)).last()
            if republish_last_proce:
                if republish_last_proce.stage == current_stage:
                    new_duration = new_duration + republish_last_proce.time_taken
        
        if new_duration:
            over_stage.percent               = tenders.count()*100/all_tenders
            over_stage.save()
            # backup_db = over_stage.save(using='new_maria_db')
        else:
            over_stage.percent               = 0
            over_stage.save()
            # backup_db = over_stage.save(using='new_maria_db')
        for_all_stages(year_plan)

# def all_republished_stage(tender):
#     year_plan = tender.procurement_doc
#     current_stage = tender.workon.last().stage
#     all_tenders = Tender_republished.objects.filter(procurement_doc=year_plan)
#     over_stage  = Overall_stages.objects.filter(procurement_doc=year_plan,stage=current_stage).first()
#     if over_stage:
#         tenders = over_stage.plans_on_stage.all()
#         new_duration = timedelta(days=0)
#         actual_duration = timedelta(days=0)
#         for tender in tenders:
#             tender_last_proce = tender.workon.filter(procurement_doc=year_plan).exclude(time_taken=timedelta(days=0)).last()
#             if tender_last_proce:
#                 if tender_last_proce.stage == current_stage:
#                     new_duration = new_duration + tender_last_proce.time_taken
#         if new_duration:
#             over_stage.percent               = tenders.count()*100/all_tenders.count()
#             over_stage.save()
#             # backup_db = over_stage.save(using='new_maria_db')
#         else:
#             over_stage.percent               = 0
#             over_stage.save()
#             # backup_db = over_stage.save(using='new_maria_db')
#         for_all_stages(year_plan)

def for_all_stages(year_plan):
    in_tenders = Tender.objects.filter(procurement_doc=year_plan).exclude(Q(activity_status="Canceled")|Q(activity_status="Removed"))
    in_republished = Tender_republished.objects.filter(procurement_doc=year_plan).exclude(Q(activity_status="Canceled")|Q(activity_status="Removed"))
    all_tenders = in_tenders.values_list('activity_id','activity_description').union(in_republished.values_list('activity_id','activity_description')).count()
    over_stages = Overall_stages.objects.filter(procurement_doc=year_plan)
    for over_stage in over_stages:
        new_duration = timedelta(days=0)
        actual_duration = timedelta(days=0)
        procedures = Procedure.objects.filter(procurement_doc=year_plan, stage=over_stage.stage).exclude(time_taken=timedelta(hours=0))
        if procedures:
            for procedure in procedures:
                if procedure.proc_item:
                    new_duration = new_duration + procedure.time_taken
                    method = procedure.proc_item.tendering_method
                    duration = Duration.objects.filter(method=method, stage=over_stage.stage).first()
                    actual_duration = actual_duration + duration.delay

            over_stage.actual_duration_total = actual_duration
            over_stage.used_time_total       = new_duration
            over_stage.average               = new_duration/procedures.count()
            over_stage.save()
            # backup_db = over_stage.save(using='new_maria_db')
        over_stage.percent = over_stage.plans_on_stage.count()*100/all_tenders
        # print(over_stage.plans_on_stage.count())
        over_stage.save()
        # backup_db = over_stage.save(using='new_maria_db')

# def all_lates(year_plan):
#     over_stages = Overall_stages.objects.filter(procurement_doc=year_plan)
#     procedures = Procedure.objects.filter(procurement_doc=year_plan, stage__title='TENDERING', time_taken=timedelta(hours=0), )
#     if procedures:
#         for procedure in procedures:
#             method = procedure.proc_item.

        



# ============================================ form =======================================

def all_forms(request):
    stageform = stage_form()
    content ={
        'stageform':stageform
    }
    return content

# =========================================== actuals capture ========================================

def actuals(item,current_proced = None, next_stage = None):
    now  = datetime.today()
    tender_report = item.tender_report.first()
    if current_proced is None:
        tender_report.actual_tender_doc_preparation = now
    elif current_proced:
        current_stage_title = current_proced.stage.title.upper()
        if current_stage_title == 'TENDER DOCUMENT PREPARATION':
            tender_report.actual_tender_doc_preparation = now
        elif current_stage_title == 'PUBLICATION':
            tender_report.actual_end_publication_date = now
        elif current_stage_title == 'OPENING':
            tender_report.actual_end_opening = now
        elif current_stage_title == 'EVALUATION':
            tender_report.actual_end_evaluation = now
        elif current_stage_title == 'PROVISION NOTIFICATION':
            tender_report.actual_end_provision_notification_date = now
        elif current_stage_title == 'FINAL NOTIFICATION':
            tender_report.actual_end_final_notification = now
        elif current_stage_title == 'CONTRACT':
            tender_report.actual_end_contract_signing_date = now

    if next_stage:
        current_stage_title = next_stage.stage.title.upper()
        if current_stage_title == 'TENDER DOCUMENT PREPARATION':
            tender_report.actual_tender_doc_preparation = now
        elif current_stage_title == 'PUBLICATION':
            tender_report.actual_publication_date = now
        elif current_stage_title == 'OPENING':
            tender_report.actual_bid_opening_date = now
        elif current_stage_title == 'EVALUATION':
            tender_report.actual_start_evaluation = now
        elif current_stage_title == 'PROVISION NOTIFICATION':
            tender_report.actual_provisional_notification_date = now
        elif current_stage_title == 'FINAL NOTIFICATION':
            tender_report.actual_final_notification = now
        elif current_stage_title == 'CONTRACT':
            tender_report.actual_contract_signing_date = now
    tender_report.save()


def republished_actuals(item,current_proced = None, next_stage = None):
    now  = datetime.today()
    tender_report = item.republished_tender_report.first()
    print(tender_report)
    if current_proced is None:
        tender_report.actual_tender_doc_preparation = now
    elif current_proced:
        current_stage_title = current_proced.stage.title.upper()
        if current_stage_title == 'TENDER DOCUMENT PREPARATION':
            tender_report.actual_tender_doc_preparation = now
        elif current_stage_title == 'PUBLICATION':
            tender_report.actual_end_publication_date = now
        elif current_stage_title == 'OPENING':
            tender_report.actual_end_opening = now
        elif current_stage_title == 'EVALUATION':
            tender_report.actual_end_evaluation = now
        elif current_stage_title == 'PROVISION NOTIFICATION':
            tender_report.actual_end_provision_notification_date = now
        elif current_stage_title == 'FINAL NOTIFICATION':
            tender_report.actual_end_final_notification = now
        elif current_stage_title == 'CONTRACT':
            tender_report.actual_end_contract_signing_date = now

    if next_stage:
        current_stage_title = next_stage.stage.title.upper()
        if current_stage_title == 'TENDER DOCUMENT PREPARATION':
            tender_report.actual_tender_doc_preparation = now
        elif current_stage_title == 'PUBLICATION':
            tender_report.actual_publication_date = now
        elif current_stage_title == 'OPENING':
            tender_report.actual_bid_opening_date = now
        elif current_stage_title == 'EVALUATION':
            tender_report.actual_start_evaluation = now
        elif current_stage_title == 'PROVISION NOTIFICATION':
            tender_report.actual_provisional_notification_date = now
        elif current_stage_title == 'FINAL NOTIFICATION':
            tender_report.actual_final_notification = now
        elif current_stage_title == 'CONTRACT':
            tender_report.actual_contract_signing_date = now
    tender_report.save()


