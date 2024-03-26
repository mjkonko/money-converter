import requests, json, datetime
from datetime import datetime as dt, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Exceptions
class WrongChoiceException(Exception):
    "Unavailable option"
    pass

class DataNotAvailable(Exception):
    "Unavailable data from API"
    pass

# Class representing the currency rate
class Rate:
    currency: str
    code: str
    mid: float
    
    def __init__(self, currency, code, mid):
        self.currency = currency
        self.code = code
        self.mid = mid
        
# Class representing the table by NBP        
class Table:
    rates: Rate
    date: datetime
    table_no: str
    
    def __init__(self, rates, date, table_no):
        rates_object_list = list()
        for rate in rates:
           rates_object_list.append(Rate(rate["currency"],rate["code"],rate["mid"]))
           
        self.rates = rates_object_list
        self.date = dt.strptime(date, "%Y-%m-%d")
        self.table_no = table_no

    # sorts self by mid price
    def sort_self_by_mid(self):
        unsorted_list = self.rates
        
        # modified selection sort algorithm
        for x in range(len(unsorted_list)):
            min_x = x
            for y in range (x+1, len(unsorted_list)):
                if unsorted_list[min_x].mid > unsorted_list[y].mid:
                    min_x = y
                unsorted_list[x], unsorted_list[min_x] = unsorted_list[min_x], unsorted_list[x]
    
    # sorts self by code     
    def sort_self_by_code(self):
        unsorted_list = self.rates
        
        # modified selection sort algorithm
        for x in range(len(unsorted_list)):
            min_x = x
            for y in range (x+1, len(unsorted_list)):
                if unsorted_list[min_x].code > unsorted_list[y].code:
                    min_x = y
                unsorted_list[x], unsorted_list[min_x] = unsorted_list[min_x], unsorted_list[x]
                    
    # print ascii-style table for given date
    def ascii_mode_table(self):
        print("--------------------------------")
        print("Tabela A | " + self.table_no + " |")
        print("--------------------------------")
        print("Dane z dnia " + str(self.date))
        print("--------------------------------")
        print("|--Mid---Kod----Waluta--|")
        
        for x in self.rates:
           print("|--" + str(x.mid) + "---" + x.code + "----" + x.currency + "--|")
           
        print("|--Mid---Kod----Waluta--|")
        print("--------------------------------")
    
    def find_mid_by_code(self, code):
        for rate in self.rates:
            if rate.code == code:
                return rate.mid 
            
class Main:
    
    # First CDM menu
    def select_main_menu(self):
        try: 
            print("Tryb:")
            print("1. Wyswietlanie Tabeli")
            print("2. Przelicznik walut")
            print("3. Zapisz tabele do pliku JSON")
            print("4. Wyświetl wykresy")
            print("Q. Zamknij program")
            selection_1 = input()

            match selection_1:
                case "1":
                    self.select_data_option()
                case "2":
                    self.select_convert()
                case "3":
                    self.select_saving()
                case "4":
                    self.select_plots(None)
                case "Q":
                    quit()
                case "q":
                    quit()
                case _:
                    raise WrongChoiceException
        
        except WrongChoiceException:
            print("Bledny wybor")
            self.select_main_menu()

    # Second CMD menu
    def select_data_option(self):
        try: 
            print("Wybierz opcje danych pobieranych z Tabeli A NBP:")
            print("1. Aktualna tabela (/today) lub ostatnia dostepna (today - 1)")
            print("2. Ostatnie X tabel (/last/X)")
            print("3. Konkretny dzien (/{date})")
            print("4. Zakres danych (/{startDate}/{endDate})")
            print("5. Menu glowne")
            print("Q. Zamknij program")
            
            selection_1 = input()
            result = list()
            
            match selection_1:
                case "1":
                    try:
                        data = self.prep_data("today")

                    except DataNotAvailable:
                        date = self.account_for_wkend()                               
                        data = self.prep_data(date)
                        
                    
                    self.print_results(data)
                case "2":
                    amount = input("Podaj ilosc tabel do zwrocenia: ")
                    result = self.prep_data("last/" + amount)
                case "3":
                    date = input("Podaj date w formacie YYYY-MM-DD: ")
                    result = self.prep_data(date)
                case "4":
                    start_date = input("Podaj date poczatkowa w formacie YYYY-MM-DD: ")
                    end_date = input("Podaj date koncowa w formacie YYYY-MM-DD: ")
                    result = self.prep_data(start_date + "/" + end_date)
                case "5":
                    self.select_main_menu()
                case "Q":
                    quit()
                case "q":
                    quit()
                case _:
                    raise WrongChoiceException
                
            if result == None:
                self.select_data_option()
                
            if(len(result) > 0):
                print("Czy chcesz sortowac dane?")
                print("1. Po cenie rosnaco")
                print("2. Po kodzie waluty")
                print("3. Nie sortuj (wyswietlenie wg nazw waluty, alfabetycznie)")
                print("Q. Zamknij program")
                
                selection_2 = input()
                
                match selection_2:
                    case "1":
                        for x in range(len(result)):
                            result[x].sort_self_by_mid()
                    case "2":
                        for x in range(len(result)):
                            result[x].sort_self_by_code()
                    case "3":
                        pass
                    case "Q":
                        quit()
                    case "q":
                        quit()
                    case _:
                        raise WrongChoiceException
                
            self.print_results(result)
            self.select_data_option()
        
        except WrongChoiceException:
            print("Bledny wybor")
            self.select_data_option()
            
        except TypeError:
            self.select_data_option()
            
    # Third CMD menu - conversion
    def select_convert(self):
        try: 
            print("Konwersja walut:")
            print("1. Najbardziej aktualne dostepne dane")
            print("2. Dla daty")
            print("3. Menu glowne")
            print("Q. Zamknij program")
            selection_1 = input()

            match selection_1:
                case "1":
                    self.convert_newest()
                case "2":
                    self.convert_for_date()
                case "3":
                    self.select_main_menu()
                case "Q":
                    quit()
                case "q":
                    quit()
                case _:
                    raise WrongChoiceException
                            
        except WrongChoiceException:
            print("Bledny wybor")
            self.select_convert()
        
    def convert_newest(self):            
        try:
            result = self.prep_data("today")
            
        except DataNotAvailable:
            date = self.account_for_wkend()               
            result = self.prep_data(date) 
        
            
        self.print_results(result)
        self.conversion(result)
        
    def convert_for_date(self):
        try:
            date = input("Podaj date w formacie YYYY-MM-DD: ")
            data = self.prep_data(date)

        except DataNotAvailable:
            pass
            
        self.print_results(data)
        self.conversion(data)
    
    def conversion(self, data):
        target_currency = input("Podaj kod waluty docelowej, np. INR, USD, EUR: ")
        target_value = input("Podaj wartosc w PLN: ")
        mid_price = data[0].find_mid_by_code(target_currency)

        result = float(target_value) / mid_price 
        
        print("---------------------------------------------------")
        print("Wynik konwersji to: " + str(round(result, 2)) + " " + target_currency + "\n")
        self.select_convert()

    # Fourth CMD menu
    def select_saving(self):
        try: 
            print("Wybierz opcje zapisu danych pobieranych z Tabeli A NBP:")
            print("1. Aktualna tabela (/today) lub ostatnia dostepna (today - 1)")
            print("2. Ostatnie X tabel (/last/X)")
            print("3. Konkretny dzien (/{date})")
            print("4. Zakres danych (/{startDate}/{endDate})")
            print("5. Menu glowne")
            print("Q. Zamknij program")
            
            selection_1 = input()
            result = list()
            
            match selection_1:
                case "1":
                    try:
                        result = self.api_call("today")
                        
                    except DataNotAvailable:
                        date = self.account_for_wkend()                      
                        result = self.api_call(date) 
                case "2":
                    amount = input("Podaj ilosc tabel do zwrocenia: ")
                    result = self.api_call("last/" + amount)
                case "3":
                    date = input("Podaj date w formacie YYYY-MM-DD: ")
                    result = self.api_call(date)
                case "4":
                    start_date = input("Podaj date poczatkowa w formacie YYYY-MM-DD: ")
                    end_date = input("Podaj date koncowa w formacie YYYY-MM-DD: ")
                    result = self.api_call(start_date + "/" + end_date)
                case "5":
                    self.select_main_menu()
                case "Q":
                    quit()
                case "q":
                    quit()
                case _:
                    raise WrongChoiceException
                
            self.save_table_json(result)
        
        except WrongChoiceException:
            print("Bledny wybor")
            self.select_saving()
            
        except TypeError:
            self.select_saving()

    # Fifth CMD menu
    def select_plots(self, code_return):
        if code_return == None:
            code = input("Kod waluty: ")
        else:
            code = code_return
            
        count = input("Podaj ilosc dni do generacji wykresu: ")
        
        if int(count) < 2:
            print("Minimum 2 dni wymagane!")
            self.select_plots(code)

        data = self.api_rates_call(code + "/last/" + count)
        list_date_mid = list()
        
        for x in data['rates']:
            list_date_mid.append([x['effectiveDate'], x['mid']])
        
        df = pd.DataFrame(list_date_mid)

        # plot
        plot = df.set_index(0).plot(kind = 'line')
        plot.set_xlabel("Days")
        plot.set_ylabel("Value")
        plot.set_label(code + "/PLN")
        plot.set_title(code + "/PLN")

        plt.show()
        
        self.select_main_menu()
        
        
# Utility methods 
    # JSON downloader and API caller maker
    def prep_data(self, options):       
        # API Call
        try:
            json = self.api_call(options)
        
            return self.parse_json_to_tables_list(json)
        except DataNotAvailable:
            raise DataNotAvailable()
        
    def api_rates_call(self, options):
        try:
            URL = "http://api.nbp.pl/api/exchangerates/rates/a/" + options
            r = requests.get(url = URL)
            json = r.json()
            r.close()
        
            return json
    
        except requests.JSONDecodeError:
            print("Wygląda na to, ze mamy problem z przetwarzaniem pliku JSON z NBP API.")
        
    def api_call(self, options):
        try:
            URL = "http://api.nbp.pl/api/exchangerates/tables/a/" + options
            r = requests.get(url = URL)
            json = r.json()
            r.close()
        
            return json
    
        except requests.JSONDecodeError:
            print("Wygląda na to, ze mamy problem z przetwarzaniem pliku JSON z NBP API.")

            if options == "today":
                print("Dzisiejsza tabela moze byc jeszcze nieupubliczniona")
                raise DataNotAvailable()
    
    #JSON to Table object parsing            
    def parse_json_to_tables_list(self, json):
        x = 0
        tables = list()
        for x in range(len(json)):
            rates = (json[x]['rates'])
            effective_date = (json[x]['effectiveDate'])
            table_no = (json[x]['no'])
            table = Table(rates, effective_date, table_no)
            tables.append(table)

        return tables
    
    #Table list printer in ASCII-like style
    def print_results(self, tables):
        for x in tables:
            x.ascii_mode_table()
    
    def save_table_json(self, json):
        f = open("saved_data.json", "w")
        f.write(str(json))
        f.close()
        print("Zapisano plik JSON")
            
    def account_for_wkend(self):
        date = dt.now() 

        day_of_week = date.isoweekday()
        
        if(day_of_week == 6):
            date = date - timedelta(1)   
        elif(day_of_week == 7):
            date = date - timedelta(2)  
        
        return date.strftime('%Y-%m-%d')                       
        
    def __init__(self):
        self.select_main_menu()
        
Main()