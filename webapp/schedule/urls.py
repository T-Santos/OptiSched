from django.conf.urls import url

from . import views

'''
o When capturing ags in the url, they need to have the same name
  as whats being received in the views.py def for that view
'''

urlpatterns = [

	# ------ Main Pages -------
	url(r'^$', views.home, name='home'),
	url(r'^(?i)Home/', views.home, name='home'),
	url(r'^(?i)About/$', views.about, name='about'),
	url(r'^(?i)Contact/$', views.contact, name='contact'),
	url(r'^(?i)Dashboard/$', views.dashboard, name='dashboard'),

	# ------ Dashboard ---------
	url(r'^(?i)Settings/$', views.settings, name='settings'),
	url(r'^(?i)Settings/GeneralSettings/$', views.general_settings, name='general_settings'),
	url(r'^(?i)Settings/ScheduleSettings/$', views.schedule_settings, name='schedule_settings'),

	# ------ Actions ---------
	url(r'^(?i)CreateSchedule/$', views.create_schedule, name='create_schedule'),
	url(r'^(?i)CreateDateSpan/$', views.create_date_span, name='create_date_span'),
	url(r'^(?i)CreateNewEmployee/$', views.create_new_employee, name='create_new_employee'),

	url(r'(?i)EditEmployee/(?P<employee_id>[0-9]+)/$', views.edit_employee, name='edit_employee'),

	# ------ Navigation ------
	url(r'^(?i)ViewManagerDay/$', views.ViewManagerDay, name='ViewManagerDay'),
	url(r'(?i)EmployeeList/$', views.employee_list, name='EmployeeList'),
	url(r'^(?i)ViewEmployeeWeek/(?P<employee_id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.ViewEmployeeWeek, name='ViewEmployeeWeek'),

]
