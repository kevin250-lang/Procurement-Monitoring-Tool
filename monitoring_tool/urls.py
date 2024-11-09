"""
URL configuration for monitoring_tool project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from monitoring_app.views import *
from monitoring_app.pdf import *

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', home, name='home'),
    re_path(r'^login/', login_in, name='login'),
    re_path(r'^logout/', logingout, name='logout'),

    # ==========================================user=================================

    re_path(r'^register/user/$', register_user, name='register_user'),
    re_path(r'^register/user/(?P<pk>[\d]+)/info/$', register_user_more, name='register_user_more'),
    re_path(r'^user/(?P<pk>[\d]+)/detail/$', user_detail, name='user_detail'),
    re_path(r'^user/list/$', user_list, name='user_list'),
    re_path(r'^data/backing/up/$',backup_data, name='data_backup'),


    # ===========================================plan==============================
    re_path(r'^files/upload/$', document_upload, name='file_upload'),
    re_path(r'^procurement/plans/list/$', procurement_plan_list, name='procurement_plans_list'),
    re_path(r'^all/procurement/plans/$', all_plans, name='all_plans'),
    re_path(r'^procurement/plan/(?P<pk>[\d]+)/detail/$', procurement_plan_detail, name='procurement_plan_detail'),
    re_path(r'^procurement/plan/(?P<pk>[\d]+)/deletion/$', procurement_plan_deletion, name='procurement_plan_deletion'),


    # ==========================================tender=============================
    re_path(r'^tender/(?P<pk>[\d]+)/detail/$', tender_detail, name='tender_detail'),
    re_path(r'^tender/(?P<pk>[\d]+)/update/$', tender_update, name='tender_update'),
    re_path(r'^tender/(?P<pk>[\d]+)/cancel/$', cancel_tender, name='cancel_tender'),
    re_path(r'^tender/(?P<pk>[\d]+)/late/start/$', late_tenders, name='late_tenders'),
    re_path(r'^tender/(?P<pk>[\d]+)/today/tenders/$', today_tenders, name='today_tenders'),
    re_path(r'^tender/(?P<pk>[\d]+)/tenders/to/come/$', to_come_tenders, name='to_come_tenders'),
    re_path(r'^overall/department/(?P<pk>[\d]+)/detail/$', overall_department_detail, name='overall_department_detail'),
    re_path(r'^tenders/list/', tenders, name="tenders"),
    re_path(r'^performances/pdf/$', performances_pdf, name='performances_pdf'),


    # ==========================================stage==============================
    re_path(r'^stages/$', create_stages, name='stage_creation'),
    re_path(r'^stages/(?P<pk>[\d]+)/update/$', stage_update, name='stage_updation'),
    re_path(r'^stages/(?P<pk>[\d]+)/delete/$', stage_delete, name='stage_deletion'),
    re_path(r'^overall/stages/(?P<id>[\d]+)/(?P<pk>[\d]+)/detail/$', overall_stage_detail, name='overall_stage_detail'),

    # ==========================================method==============================
    re_path(r'^tender/methods/$', create_method, name='create_method'),
    re_path(r'^tender/methods/(?P<pk>[\d]+)/update/$', method_update, name='method_update'),
    re_path(r'^tender/methods/(?P<pk>[\d]+)/delete/$', method_delete, name='method_delete'),
    re_path(r'^tender/methods/(?P<pk>[\d]+)/duration/registration/$', duration_registration, name="duration_registration"),
    re_path(r'^tender/methods/(?P<pk>[\d]+)/duration/delete/$', duration_delete, name="duration_delete"),

    # ========================================Home Pages============================
    path('', performances, name='home'),
    re_path(r'^overall/company/progess/$', progress, name='progress'),
    re_path(r'^overall/REG/progess/$', reg_progress, name='reg_progress'),
    re_path(r'^overall/EDCL/progess/$', edcl_progress, name='edcl_progress'),
    re_path(r'^overall/EUCL/progess/$', eucl_progress, name='eucl_progress'),
    re_path(r'^overall/company/departments/$', departments, name='departments'),
    re_path(r'^year/plan/(?P<pk>[\d]+)/late/tenders/$', late_tenders, name='late_tenders'),
    re_path(r'^year/plan/(?P<pk>[\d]+)/today/tenders/$', today_tenders, name='today_tenders'),
    re_path(r'^year/plan/(?P<pk>[\d]+)/to_come/tenders/$', to_come_tenders, name='to_come_tenders'),

    # ========================================== republish===========================
    re_path(r'^republish/(?P<pk>[\d]+)/$', tender_republish, name='republish'),
    re_path(r'^republished/(?P<pk>[\d]+)/detail/$', republished_detail, name='republished_detail'),
    re_path(r'^tender/republished/(?P<pk>[\d]+)/update/$', republished_tender_update, name='republished_tender_update'),


    #==========================================Ckeditor=============================
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
]
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root = settings.STATICFILES_DIRS)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

