import PetexRoutines as PE
import GAP_utils as ut
from datetime import datetime,timedelta

def convert_date_to_five_digit_number(date_string):
    date_format = '%d/%m/%Y'
    try:
        date = datetime.strptime(date_string, date_format)
        days_since_epoch = (date - datetime(1899, 12, 30)).days

        five_digit_number = str(days_since_epoch)

        return five_digit_number
    except ValueError:
        print("Ошибка: Неверный формат даты.")
        return None

def convert_five_digit_number_to_date(five_digit_number):
    try:
        days_since_epoch = int(five_digit_number)
        date = datetime(1899, 12, 30) + timedelta(days=days_since_epoch)

        date_string = date.strftime('%d/%m/%Y')

        return date_string
    except ValueError:
        print("Ошибка: Неверный формат числа.")
        return None



def run_scenario(): 
    myosid = PE.InitializeID()
    myos = PE.Initialize(myosid)
    
    path_model = r'F:\ForecastTool\Resolve_29022024\Integrated Network Model.rsl'
    sc_name = 'Scenario1'
    
    ut.resolve_start(myos)  # PE.DoCmd(myos, "Resolve.Start()")
    ut.resolve_openfile(myos, path_model) # PE.DoCmd(myos,'RESOLVE.OPENFILE(\'' + path_model + '\')')
    ut.resolve_runscenario(myos, sc_name) # PE.DoCmd(myos, "Resolve.RUNSCENARIO('Scenario1')")
    
    PE.Stop(myosid)




    # datetime back / front text
    # замена на Start