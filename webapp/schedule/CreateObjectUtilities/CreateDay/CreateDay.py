import datetime
import time
import random
import pdb

from OptiSched.models import *
from collections import namedtuple


class Workday(object):
    ''' 
        Class data members (persist across instances and are not specific to an individual WorkDay instance)
    '''
    #qs_all_employees = Person.objects.all()

    ''' 
    *********************************
            CTOR
    *********************************
    '''
    def __init__(
                self,
                date,
                date_start_time="00:00",
                date_end_time="00:00"
                ):
        '''
        ***********************************
            instance data members
        ***********************************
            should have underscore (_) prefix if private
            
            date_model_obj - the Date object created based off of the model

            shift_all - list of all Shift objects that are done or in progress
            shift_active - list of Shift objects that are currently in progress

            time_slice - int for how many minutes in a time slice say 5 minute increments
            time_slice_total - int for the total number of time slices in the given day
            time_slice_employee_types_needed - list of employees type objects that are needed to fill any open shifts (computed each time slice)

            employee_all - QuerySet of all Person objects in the DB
            employee_already_working - list of Person objects that either cannot work the current time slice because they are already working

        ''' 

        # we might want to see if a date object already exists before creating one
        self.date_model_obj =  Date(
                                    date=date,
                                    day_start_time=date_start_time,
                                    day_end_time=date_end_time
                                    )

        self.shift_all = GetAllShifts()
        self.shift_active = []

        self.time_slice = 5
        self.time_slice_total = GetTimeSliceTotal()
        self.time_slice_employee_types_needed = []

        self.employee_all = Person.objects.all()

        # these should all be private setters
        self.employee_already_working = GetAlreadyWorkingEmployees()

    '''
    ********************************
            Methods
    ********************************
        previx name with underscores (__) to mark it as being private if needed
    '''

    def Save(self):
        '''
            Save all of the objects that were created and need to be filed to the DB
        '''
        self.date_model_obj.save()

        for shift in self.shift_all:
            shift.save()

    def GetTimeSliceTotal(self):
        '''
        Returns: Int for the Total number of time slices in a given day with a start time and an end time

        '''

        start_time = self.date_model_obj.day_start_time
        end_time = self.date_model_obj.day_end_time

        diff_mins = ((end_time-start_time).total_seconds() / 60.0)

        return diff_mins / self.time_slice

    def GetAllShifts(self):
        '''
            Get all the shifts that have already been saved for a given date
        '''
        return Shift.objects.filter(shift_date = self.date_model_obj)

    def GetAlreadyWorkingEmployees(self):
        '''
            Get all employees that have saved shifts
        '''
        already_working_employees = []

       for saved_shift in self.shift_all:
            already_working_employees.append(saved_shift.employee)

        return already_working_employees

    def GenerateShifts(self):
        '''
            Called to generate shifts for a Workday
        '''

        # for each time slice in the workday
        for time_slice in range(self.time_slice_total):

            SetEmployeeTypesNeededForTimeSlice()
            
            # while more shifts needing to be filled
            while MoreShiftsNeededForTimeSlice():

                # get employee and type 
                Employee = namedtuple('Employee', 'person type')
                employee = Employee._make(GetNewEmployee())

                # if there isnt an employee to fill a shift log an error an break
                if not employee.employee:
                    "Log error"
                else:
                    # create the shift object
                    shift_new = Shift(
                                    shift_date = self.date_model_obj,
                                    employee = employee.person,
                                    shift_employee_type = employee.type
                                    )

                    # add new shift object to all and to active lists

                    # add employee to already working list

                    # update employee types needed dict by removing the one chosen 
                 