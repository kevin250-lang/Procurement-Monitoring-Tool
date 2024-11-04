from django.db import models
import random
import os
from io import BytesIO
from datetime import datetime, timedelta
from django.contrib.auth.models import User
# from ckeditor_uploader.fields import RichTextUploadingField
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.

status_choices =(
    ('REG','REG'),
    ('EDCL','EDCL'),
    ('EUCL','EUCL'))

def get_file_extension(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext
    
def upload_profile_path(instance, filename):
    filetitle = instance.user
    new_filename=random.randint(1,999999999)
    company='REG_EUCL&EDCL'
    name, ext = get_file_extension(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "profile/{filename}+{new_filename}{company}{final_filename}".format(filename=filetitle,new_filename=new_filename,final_filename=final_filename,company=company)

def upload_document_path(instance, filename):
    filetitle = instance.title
    new_filename=random.randint(1,999999999)
    company=instance.company
    name, ext = get_file_extension(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=name, ext=ext)
    return "document/plans/{company}{filename}+' '+{new_filename}{final_filename}".format(filename=filetitle,new_filename=new_filename,final_filename=final_filename,company=company)

def upload_stage_document_path(instance, filename):
    filetitle = instance.procedure.user
    new_filename=random.randint(1,999999999)
    company=instance.procedure.stage.title
    name, ext = get_file_extension(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=name, ext=ext)
    return "document/stages/{company}{filename}+' '+{new_filename}{final_filename}".format(filename=filetitle,new_filename=new_filename,final_filename=final_filename,company=company)


class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    
class Company(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class user_contact(models.Model):
    user        = models.OneToOneField(User,related_name="user_info", on_delete=models.CASCADE)
    company     = models.ManyToManyField(Company, related_name='user_company')
    Phone       = models.CharField(max_length=15)
    address     = models.CharField(max_length=40)
    verified    = models.BooleanField(default=False)
    profile     = models.ImageField(default='../media/profile/non_profile.jpg', upload_to=upload_profile_path, null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class Procurement_doc(models.Model):
    company     = models.ForeignKey(Company, related_name='company_doc', on_delete=models.CASCADE)
    user        = models.ForeignKey(User, related_name="starter", on_delete=models.CASCADE)
    title       = models.CharField(max_length=250)
    files       = models.FileField(upload_to=upload_document_path)
    timestamp   = models.DateTimeField(auto_now_add=True)
    total_budget= models.IntegerField(default=0,null=True)

    def __str__(self):
        return self.title
    
    class meta:
        ordering = ['-timestamp']


class Stage(models.Model):
    user            = models.ForeignKey(User, related_name="stage", on_delete=models.CASCADE)
    title           = models.CharField(max_length=500)
    number          = models.IntegerField()
    description     = CKEditor5Field(config_name='special')
    timestamp       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
class Method(models.Model):
    name        = models.CharField(max_length=30)
    description = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name
    
    
class Tender(models.Model):
    department          = models.ForeignKey(Department, related_name='plan_department', on_delete=models.CASCADE)
    procurement_doc     = models.ForeignKey(Procurement_doc, related_name='plan_tenders', on_delete=models.CASCADE)
    project_id          = models.CharField(max_length=50, null=True)
    project_Name        = models.CharField(max_length=50, null=True)
    activity_sequence   =  models.IntegerField(null=True)
    activity_id         = models.CharField(max_length=80, null=True)
    activity_description= models.CharField(max_length=250, null=True)
    tender_count        = models.IntegerField(null=True)
    early_start         = models.DateTimeField(null=True)
    early_finish        = models.DateTimeField(null=True)
    total_work_days     = models.IntegerField(null=True)
    activity_status     = models.CharField(max_length=80, null=True)
    total_days          = models.IntegerField(null=True)
    elapsed_work_days   = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    remaining_days      = models.IntegerField(null=True)
    remaining_work_days = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    note                = models.CharField(max_length=120, null=True, blank=True)
    actual_start        = models.DateTimeField(null=True)
    actual_finish       = models.DateTimeField(null=True)
    canceled            = models.DateTimeField(null=True)
    removed             = models.DateTimeField(null=True)
    released_date       = models.DateTimeField(null=True)
    completed           = models.DateTimeField(null=True)
    closed              = models.DateTimeField(null=True)
    used                = models.DateTimeField(null=True)
    estimated_cost      = models.IntegerField(null=True)
    planned_cost        = models.IntegerField(null=True)
    baseline_cost       = models.IntegerField(null=True)
    planned_committed_cost      = models.IntegerField(null=True)
    committed_cost              = models.IntegerField(null=True)
    used_cost                   = models.IntegerField(null=True)
    actual_cost                 = models.IntegerField(null=True)
    set_in_baseline             = models.CharField(max_length=120, null=True, blank=True)
    baseline_revision_comment   = models.CharField(max_length=120, null=True, blank=True)
    activity_changed            = models.BooleanField(default=False) #?????? its default
    financially_responsible_id  = models.CharField(max_length=80, null=True, blank=True)
    financially_responsible_name= models.CharField(max_length=80, null=True, blank=True)
    created                     = models.DateField(null=True)
    responsible_id              = models.IntegerField(null=True)
    responsible_name            = models.CharField(max_length=100, null=True)
    activity_created_by         = models.CharField(max_length=100, null=True)
    modified                    = models.CharField(max_length=15,null=True)
    modified_by                 = models.CharField(max_length=35,null=True)
    activity_type               = models.CharField(max_length=25, null=True)
    source_of_fund              = models.CharField(max_length=50, null=True)
    tendering_method            = models.ForeignKey(Method,on_delete=models.DO_NOTHING, null=True, blank=True)
    planned_tender_doc_preparation          = models.DateField(null=True)
    planned_publication_date                = models.DateField(null=True) 
    planned_bid_opening_date                = models.DateField(null=True)
    planned_start_evaluation                = models.DateField(null=True)
    planned_end_evaluation                  = models.DateField(null=True)
    planned_provisional_notification_date   = models.DateField(null=True)
    planned_final_notification_date         = models.DateField(null=True)
    planned_contract_management_start_date  = models.DateField(null=True)
    planned_contract_signing_date           = models.DateField(null=True)
    planned_contract_end_date               = models.DateField(null=True)
    supervising_firm                        = models.BooleanField(default=False)
    planned_budget                          = models.CharField(max_length=25, null=True)
    
    def __str__(self):
        return f'{self.procurement_doc.title} | {self.activity_description} | {self.activity_id}'
    

class Tender_republished(models.Model):
    tender              = models.ForeignKey(Tender, related_name='republished_tender', on_delete=models.CASCADE)
    department          = models.ForeignKey(Department, related_name='tender_department', on_delete=models.CASCADE)
    procurement_doc     = models.ForeignKey(Procurement_doc, related_name='proc_document', on_delete=models.CASCADE)
    project_id          = models.CharField(max_length=50, null=True)
    project_Name        = models.CharField(max_length=50, null=True)
    activity_sequence   =  models.IntegerField(null=True)
    activity_id         = models.CharField(max_length=80, null=True)
    activity_description= models.CharField(max_length=250, null=True)
    tender_count        = models.IntegerField(null=True)
    early_start         = models.DateTimeField(null=True)
    early_finish        = models.DateTimeField(null=True)
    total_work_days     = models.IntegerField(null=True)
    activity_status     = models.CharField(max_length=80, null=True)
    total_days          = models.IntegerField(null=True)
    elapsed_work_days   = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    remaining_days      = models.IntegerField(null=True)
    remaining_work_days = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    note                = models.CharField(max_length=120, null=True, blank=True)
    actual_start        = models.DateTimeField(null=True)
    actual_finish       = models.DateTimeField(null=True)
    canceled            = models.DateTimeField(null=True)
    removed             = models.DateTimeField(null=True)
    released_date       = models.DateTimeField(null=True)
    completed           = models.DateTimeField(null=True)
    closed              = models.DateTimeField(null=True)
    used                = models.DateTimeField(null=True)
    estimated_cost      = models.IntegerField(null=True)
    planned_cost        = models.IntegerField(null=True)
    baseline_cost       = models.IntegerField(null=True)
    planned_committed_cost      = models.IntegerField(null=True)
    committed_cost              = models.IntegerField(null=True)
    used_cost                   = models.IntegerField(null=True)
    actual_cost                 = models.IntegerField(null=True)
    set_in_baseline             = models.CharField(max_length=120, null=True, blank=True)
    baseline_revision_comment   = models.CharField(max_length=120, null=True, blank=True)
    activity_changed            = models.BooleanField(default=False) 
    financially_responsible_id  = models.CharField(max_length=80, null=True, blank=True)
    financially_responsible_name= models.CharField(max_length=80, null=True, blank=True)
    created                     = models.DateField(null=True)
    responsible_id              = models.IntegerField(null=True)
    responsible_name            = models.CharField(max_length=100, null=True)
    activity_created_by         = models.CharField(max_length=100, null=True)
    modified                    = models.CharField(max_length=15,null=True)
    modified_by                 = models.CharField(max_length=35,null=True)
    activity_type               = models.CharField(max_length=25, null=True)
    source_of_fund              = models.CharField(max_length=50, null=True)
    tendering_method            = models.ForeignKey(Method,on_delete=models.DO_NOTHING, null=True, blank=True)
    planned_tender_doc_preparation          = models.DateField(null=True)
    planned_publication_date                = models.DateField(null=True) 
    planned_bid_opening_date                = models.DateField(null=True)
    planned_start_evaluation                = models.DateField(null=True)
    planned_end_evaluation                  = models.DateField(null=True)
    planned_provisional_notification_date   = models.DateField(null=True)
    planned_final_notification_date         = models.DateField(null=True)
    planned_contract_management_start_date  = models.DateField(null=True)
    planned_contract_signing_date           = models.DateField(null=True)
    planned_contract_end_date               = models.DateField(null=True)
    supervising_firm                        = models.BooleanField(default=False)
    planned_budget                          = models.CharField(max_length=25, null=True)
    
    def __str__(self):
        return f'{self.procurement_doc.title} | {self.activity_description} | {self.activity_id}'
    
class Plan_tenders_report(models.Model):
    tender              = models.ForeignKey(Tender, related_name="tender_report", on_delete=models.CASCADE, blank=True, null=True)
    tender_republish    = models.ForeignKey(Tender_republished, related_name="republished_tender_report", on_delete=models.CASCADE, blank=True, null=True)
    department          = models.ForeignKey(Department, related_name='report_plan_department', on_delete=models.CASCADE)
    procurement_doc     = models.ForeignKey(Procurement_doc, related_name='report_plan_tenders', on_delete=models.CASCADE)
    activity_id         = models.CharField(max_length=50, null=True)
    activity_description= models.CharField(max_length=250, null=True)
    estimated_cost      = models.IntegerField(null=True)
    source_of_fund      = models.CharField(max_length=50, null=True)
    tendering_method    = models.ForeignKey(Method, on_delete=models.DO_NOTHING, null=True, blank=True)
    planned_tender_doc_preparation          = models.DateField(null=True)
    actual_tender_doc_preparation           = models.DateField(null=True)
    actual_end_tender_doc_preparation       = models.DateField(null=True)
    start_difference_tender_doc_preparation = models.DurationField(null=True)
    end_difference_tender_doc_preparation   = models.DurationField(null=True)

    planned_publication_date                = models.DateField(null=True) 
    actual_publication_date                 = models.DateField(null=True)
    actual_end_publication_date             = models.DateField(null=True)
    start_difference_publication_date       = models.DurationField(null=True)
    end_difference_publication_date         = models.DurationField(null=True)

    planned_bid_opening_date                = models.DateField(null=True)
    actual_bid_opening_date                 = models.DateField(null=True)
    actual_end_opening                      = models.DateField(null=True)
    start_difference_opening_date           = models.DurationField(null=True)
    end_difference_opening_date             = models.DurationField(null=True)

    planned_start_evaluation                = models.DateField(null=True)
    actual_start_evaluation                 = models.DateField(null=True)
    planned_end_evaluation                  = models.DateField(null=True)
    actual_end_evaluation                   = models.DateField(null=True)
    start_difference_evaluation             = models.DurationField(null=True)
    end_difference_evaluation               = models.DurationField(null=True)

    planned_provisional_notification_date   = models.DateField(null=True)
    actual_provisional_notification_date    = models.DateField(null=True)
    actual_end_provision_notification_date  = models.DateField(null=True)
    start_difference_provisional_notification= models.DurationField(null=True)
    end_difference_provisional_notification = models.DurationField(null=True)

    planned_contract_management_start_date  = models.DateField(null=True)
    actual_contract_management_start_date   = models.DateField(null=True)
    actual_contract_management_end_date     = models.DateField(null=True)
    start_difference_contract_management    = models.DurationField(null=True)
    end_difference_contract_management      = models.DurationField(null=True)

    planned_final_notification              = models.DateField(null=True)
    actual_final_notification               = models.DateField(null=True)
    actual_end_final_notification           = models.DateField(null=True)
    start_difference_final_notification     = models.DurationField(null=True)
    end_difference_final_notification       = models.DurationField(null=True)

    planned_contract_signing_date           = models.DateField(null=True)
    actual_contract_signing_date            = models.DateField(null=True)
    actual_end_contract_signing_date        = models.DateField(null=True)
    start_difference_contract_signing       = models.DurationField(null=True)
    end_difference_contract_signing         = models.DurationField(null=True)

    planned_created                         = models.DateField(null=True)
    activity_status                         = models.CharField(max_length=80, null=True)
    canceled                                = models.DateTimeField(null=True)
    removed                                 = models.DateTimeField(null=True)
    
    def __str__(self):
        return f'{self.procurement_doc.title} | {self.activity_description} | {self.activity_id}'
    
    
class Procedure(models.Model):
    user            = models.ForeignKey(User, related_name='actor', on_delete=models.CASCADE)
    procurement_doc = models.ForeignKey(Procurement_doc, related_name='document', on_delete=models.CASCADE)
    proc_item       = models.ForeignKey(Tender, related_name='workon', on_delete=models.CASCADE, blank=True, null=True)
    republished_item= models.ForeignKey(Tender_republished, related_name='workon', on_delete=models.CASCADE, blank=True, null=True)
    stage           = models.ForeignKey(Stage, related_name='current_stage', on_delete=models.CASCADE, null=True, blank=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    closed_date     = models.DateTimeField(auto_now=False, null=True)
    time_taken      = models.DurationField(default=timedelta(days=0), null=True) 
    late            = models.DurationField(null=True) # this is the one to workon
    status          = models.CharField(max_length=100,default='Pending')

    def __str__(self):
        return f'{str(self.timestamp)} | {self.proc_item.activity_id}'


class procedure_file(models.Model):
    procedure       = models.ForeignKey(Procedure, related_name='procedure', on_delete=models.CASCADE)
    files           = models.FileField(upload_to='document/procedure/', null=True, blank=True)

    def __Str__(self):
        return self.procedure
    
class Duration(models.Model):
    method = models.ForeignKey(Method, related_name='method_duration', on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, related_name='stage_duration', on_delete=models.CASCADE)
    delay = models.DurationField()

    def __str__(self):
        return f'{self.method.name} | {self.stage.title}'


class Overall_stages(models.Model):
    procurement_doc = models.ForeignKey(Procurement_doc, related_name='over_stages_procurement', on_delete= models.CASCADE)
    stage           = models.ForeignKey(Stage, related_name="over_stage",on_delete = models.CASCADE)
    actual_duration_total   = models.DurationField(default=timedelta(days=0))
    used_time_total = models.DurationField(default=timedelta(days=0))
    plans_on_stage  = models.ManyToManyField(Tender, related_name='tenders_on_stage')
    republished_on_stage  = models.ManyToManyField(Tender_republished, related_name='tenders_on_stage')
    percent         = models.IntegerField(default=0)
    average         = models.DurationField(default=timedelta(days=0))

    def __str__(self):
        return f'{self.procurement_doc.title} - {self.stage.title}'


class Overall_method(models.Model):
    procurement_doc = models.ForeignKey(Procurement_doc, related_name='over_methods_procurement', on_delete= models.CASCADE)
    stage           = models.ForeignKey(Stage, related_name="stage_on", on_delete = models.CASCADE)
    method          = models.ForeignKey(Method, related_name='the_method', on_delete = models.CASCADE)
    plans_on_stage  = models.IntegerField(default=0)
    total_duration  = models.DurationField(default=timedelta(days=0))
    average         = models.DurationField(default=timedelta(days=0))

    def __str__(self):
        return f'{self.procurement_doc} - {self.method} - {self.stage}'
    

class Overall_department(models.Model):
    year_proc           = models.ForeignKey(Procurement_doc, related_name='over_department_procurement', on_delete= models.CASCADE)
    tenders             = models.ManyToManyField(Tender, related_name='all_tenders')
    republished         = models.ManyToManyField(Tender, related_name='all_republished')
    department          = models.ForeignKey(Department, related_name='all_department', on_delete=models.CASCADE)
    all_items           = models.IntegerField(default=0)
    committed           = models.ManyToManyField(Tender, related_name='department_tenders_committed')
    rep_committed       = models.ManyToManyField(Tender_republished, related_name='department_tenders_committed')
    percent             = models.IntegerField(default=0)
    in_use_budget       = models.IntegerField(default=0)
    overall_budget      = models.IntegerField(default=0)
    overall_budget_perc = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.department} - {self.year_proc} - {self.overall_budget}'
    

