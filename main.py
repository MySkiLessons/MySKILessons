from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from datetime import datetime
from datetime import datetime, timedelta
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle,RoundedRectangle, Line
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from plyer import call
from kivy.config import Config
from kivymd.app import MDApp
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.button import MDRaisedButton

from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
import calendar
import json
import os
import tkinter as tk
from tkinter import messagebox

Config.set('graphics', 'orientation', 'portrait')
Window.size = (330, 660)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
    
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_day = datetime.now().day
        
        self.layout = GridLayout(cols=1)
        with self.canvas.before:
            Color(.98, .95, .95, 1)
            self.rect = Rectangle(size=(2000, 3000))
        
        button_layout = GridLayout(cols=3, size_hint_y=None, height=40)
        prev_button = Button(background_normal='', background_color=[0.09, 0.56, 0.95, 1], text="<<", on_press=self.prev_month)
        next_button = Button(background_normal='', background_color=[0.09, 0.56, 0.95, 1], text=">>", on_press=self.next_month)
        button_layout.add_widget(prev_button)
        button_layout.add_widget(Label(text="", size_hint_x=0.1))
        button_layout.add_widget(next_button)
        
        self.layout.add_widget(button_layout)
        
        self.month_label = Label(color=(.1,.1,.1, 1), size_hint_y=None, height=20)
        self.layout.add_widget(self.month_label)

        self.day_layout = GridLayout(cols=7, spacing=1)
        self.layout.add_widget(self.day_layout)
        self.add_widget(self.layout)
        self.update_calendar()

        menubutton_layout = BoxLayout(padding=50, spacing=1)
        menu_button = Button(background_normal='',
                             background_color=[0.68, 0.17, 0.07, 1],
                             text="Меню",
                             font_size='20sp',
                             bold=True,
                             size_hint_y=0.3, 
                             height=30)
        menu_button.bind(on_press=self.go_to_menu)
        menubutton_layout.add_widget(menu_button)
        self.layout.add_widget(menubutton_layout)

    def update_calendar(self):
        self.day_layout.clear_widgets()
        self.month_label.text = calendar.month_name[self.current_month] + f" {self.current_year}"

        days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day in days_of_week:
            self.day_layout.add_widget(Label(color=(.1,.1,.1, 1), text=day, size_hint_y=None, bold=True))

        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        first_day_of_month = calendar.monthrange(self.current_year, self.current_month)[0]

        for _ in range(first_day_of_month):
            self.day_layout.add_widget(Label())

        for day in range(1, days_in_month + 1):
            button = Button(background_normal='',
                            background_color=[0.09, 0.56, 0.95, 0.4],
                            text=str(day), font_size='20sp', bold=True,
                            size_hint_y=None, height=40)
            button.bind(on_press=self.show_message)

            if day == self.current_day and self.current_month == datetime.now().month and self.current_year == datetime.now().year:
                button.background_color = (0.09, 0.56, 0.95, 0.9)

            self.day_layout.add_widget(button)

    def prev_month(self, instance):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()

    def next_month(self, instance):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()

    def show_message(self, instance):
        selected_day = instance.text
        self.manager.current = 'message'
        self.manager.get_screen('message').update_message(selected_day, self.current_month, self.current_year)
    
    def go_to_menu(self, instance):
        self.manager.current = 'menu'

class MessageScreen(Screen):
    def __init__(self, **kwargs):
        super(MessageScreen, self).__init__(**kwargs)
        self.students_data = self.load_students_data()
       
        self.layout = GridLayout(cols=1, padding=10, spacing=20, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=(2000, 3000))

        self.date_label = Label(color=(.1,.1,.1, 1), bold=True, text="", size_hint_y=None, height=40)
        self.layout.add_widget(self.date_label)
        
        self.lessons_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.lessons_layout.bind(minimum_height=self.lessons_layout.setter('height'))
        self.layout.add_widget(self.lessons_layout)
        
        dobavitUrok_button = Button(
            background_normal='', 
            background_color=[0.09, 0.56, 0.95, 1], 
            text="+ Добавить занятие", 
            size_hint_y=None, 
            height=40
        )
        dobavitUrok_button.bind(on_press=self.dobavitUrok)
        self.layout.add_widget(dobavitUrok_button)

        back_button = Button(
            background_normal='', 
            background_color=[0.68, 0.17, 0.07, 1], 
            text="Назад", 
            size_hint_y=None,
            height=70
        )
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(self.layout)
        self.add_widget(scroll_view)
     
    def dobavitUrok(self, instance):
        self.manager.get_screen('dobavitUrok').set_date(self.selected_day, self.selected_month, self.selected_year)
        self.manager.current = 'dobavitUrok'

    def load_students_data(self):
        try:
            with open('students.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Ошибка при чтении файла students.json: {e}")
            return []

    def get_phone_number(self, student_name):
        # Нормализуем имя студента (приводим к нижнему регистру и удаляем лишние пробелы)
        normalized_name = ' '.join(student_name.lower().split())
        
        for student in self.students_data:
            # Нормализуем имя из базы данных
            normalized_student_name = ' '.join(student.get('name', '').lower().split())
            
            # Проверяем, содержится ли нормализованное имя студента в нормализованном имени из базы
            if normalized_name in normalized_student_name or normalized_student_name in normalized_name:
                return student.get('phone', 'Нет номера')
        
        print(f"Не найден номер телефона для студента: {student_name}")
        return 'Нет номера'

    def update_message(self, day, month, year):
        self.selected_day = day
        self.selected_month = month
        self.selected_year = year
        selected_date = f"{day}.{month}.{year}"
        self.date_label.text = selected_date

        self.lessons_layout.clear_widgets()

        try:
            with open('lessons.json', 'r', encoding='utf-8') as file:
                lessons = json.load(file)

            filtered_lessons = [lesson for lesson in lessons if lesson['date'] == selected_date]
        
            if filtered_lessons:
                for lesson in filtered_lessons:
                    lesson_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
                
                    time_button = Button(
                        text=str(lesson.get('time',)),
                        background_normal='',
                        background_color=[0.09, 0.56, 0.95, .05],
                        color=(.1,.1,.1,1),
                        font_size ='15sp',
                        size_hint_x=0.2
                    )
                    duration_button = Button(
                        text=str(lesson.get('duration',)),
                        background_normal='',
                        background_color=[0.09, 0.56, 0.95, .05],
                        color=(.1,.1,.1,1),
                        font_size ='15sp',
                        size_hint_x=0.15
                    )
                    student_name = str(lesson.get('student', ''))
                    student_button = CustomButton(
                        text=student_name,
                        color=(.1,.1,.1,1),
                        size_hint_x=0.4
                    )
                    phone_number = self.get_phone_number(student_name)
                    phone_button = CustomButton(
                        text=phone_number,
                        color=(.1,.1,.1,1),
                        size_hint_x=0.3
                    )
                
                    lesson_layout.add_widget(time_button)
                    lesson_layout.add_widget(duration_button)
                    lesson_layout.add_widget(student_button)
                    lesson_layout.add_widget(phone_button)
                
                    self.lessons_layout.add_widget(lesson_layout)
            else:
                no_lessons_label = Label(
                    text="Нет занятий",
                    color=(.1,.1,.1, 1),
                    size_hint_y=None,
                    height=40
                )
                self.lessons_layout.add_widget(no_lessons_label)
        except Exception as e:
            error_label = Label(
                text=f"Ошибка при загрузке данных: {str(e)}",
                color=(1, 0, 0, 1),
                size_hint_y=None,
                height=40
            )
            self.lessons_layout.add_widget(error_label)

    def make_call(self, phone_number):
        try:
            call.make_call(self.phone_number)
            
        except Exception as e:
            print(f"Ошибка при выполнении вызова: {e}")


    def go_back(self, instance):
        self.manager.current = 'main'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        layout = GridLayout(cols=1,padding = 10, spacing=10)  # Используем один столбец
        self.layout = GridLayout(cols=1,)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # white color
            self.rect = Rectangle(size = (2000, 3000))

        students_button = Button(background_normal='',
                             background_color=[0.09, 0.56, 0.95, 1],
                             font_size='20sp',        # Размер шрифта
                             bold=True,text="Ученики")
        students_button.bind(on_press=self.go_to_students)
        layout.add_widget(students_button)
    

        lessons_button = Button(background_normal='',
                             background_color=[0.86, 0.60, 0.25, 1],
                                                             font_size='20sp',       
                                bold=True,text="Занятия")
        lessons_button.bind(on_press=self.go_to_lessons)
        layout.add_widget(lessons_button)
        

        settings_button = Button(background_normal='',
                             background_color=[0.08, 0.36, 0.5, 1],
                             
                             font_size='20sp',        # Размер шрифта
                             bold=True,text="Настройки")
        layout.add_widget(settings_button)
   
        # Создаем кнопку "Назад"
        back_button = Button(background_normal='',
                             background_color=[0.68, 0.17, 0.07, 1],
                             
                             font_size='20sp',        # Размер шрифта
                             bold=True,text="Назад")
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
    
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'  # Возвращаемся на главный экран
    def go_to_students(self, instance):
        self.manager.current = 'students'
    def go_to_lessons(self, instance):
        self.manager.current = 'lessons'

class StudentsScreen(Screen):
    def __init__(self, **kwargs):
        super(StudentsScreen, self).__init__(**kwargs)

        layout = GridLayout(cols=1,spacing = 20,padding = 10)
        
        self.layout = GridLayout(cols=1, )
        with self.canvas.before:
            Color(1, 1, 1, 1)  # white color
            self.rect = Rectangle(size = (2000, 3000))  

        title_label = Label(text="Список учеников", size_hint_y=None, height=40)
        layout.add_widget(title_label)

        # Поле для поиска
        self.search_input = TextInput(hint_text="Поиск по имени", size_hint_y=None, height=40)
        self.search_input.bind(text=self.on_search_text_change)
        layout.add_widget(self.search_input)

        # Список учеников
        self.students_layout = GridLayout(spacing = 5,cols=1, size_hint_y=None)
        self.students_layout.bind(minimum_height=self.students_layout.setter('height'))
        layout.add_widget(self.students_layout)

        # Кнопка добавить ученика
        add_student_button = Button(background_normal='',
                             background_color=[0.09, 0.56, 0.95, 1],
                             font_size='20sp',text="+ Добавить ученика", size_hint_y=None, height=40)
        add_student_button.bind(on_press=self.add_student)
        layout.add_widget(add_student_button)

        # Кнопка назад
        back_button = Button(background_normal='',
                             background_color=[0.09, 0.56, 0.95, 1],
                             font_size='20sp',text="Назад", size_hint_y=None, height=40)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.load_students()  # Загружаем студентов каждый раз при входе на экран

    def load_students(self):
        self.students_layout.clear_widgets()

        # Загружаем всех студентов и сохраняем их для поиска
        self.all_students = []

        if os.path.exists('students.json'):
            with open('students.json', 'r', encoding='utf-8') as f:
                students = json.load(f)
                self.all_students = students  # Сохраняем всех студентов
                self.update_student_list(students)  # Отображаем их

    def update_student_list(self, students):
        self.students_layout.clear_widgets()

        if students:
            for student in students[:5]:  # Ограничиваем количество отображаемых студентов
                student_button = Button(bold=True,background_normal='',background_color=[0.09, 0.56, 0.95, 0.1],font_size='13sp',text=f"{student['name']}: {student['phone']}",color=(.1,.1,.1,1), size_hint_y=None, height=40)
                student_button.bind(on_press=lambda instance, student=student: self.StudentProfile(student))
                self.students_layout.add_widget(student_button)
        else:
            self.students_layout.add_widget(Label(text="Нет учеников", size_hint_y=None, height=40))

    def on_search_text_change(self, instance, value):
        search_text = value.lower()
        filtered_students = [student for student in self.all_students if search_text in student['name'].lower()]
        self.update_student_list(filtered_students)  # Обновляем список на основе поиска

    def StudentProfile(self, student):
        App.get_running_app().current_student = student  # Сохраняем выбранного ученика в App
        self.manager.current = 'StudentProfile'

    def add_student(self, instance):
        self.manager.current = 'add_student'

    def go_back(self, instance):
        self.manager.current = 'main'

class lessonsScreen(Screen):
    def __init__(self, **kwargs): 
        super(lessonsScreen, self).__init__(**kwargs) 

        # Основной макет 
        self.layout = GridLayout(cols=1,spacing = 20,padding = 10) 
        with self.canvas.before: 
            Color(1, 1, 1, 1)  # white color 
            self.rect = Rectangle(size=(2000, 3000)) 

        title_label = Label(color=(.1,.1,.1, 1),text="Список занятий", size_hint_y=None, height=40) 
        self.layout.add_widget(title_label) 

        # Макет для списка занятий 
        self.lessons_layout = GridLayout(cols=1, size_hint_y=None) 
        self.lessons_layout.bind(minimum_height=self.lessons_layout.setter('height')) 
        self.layout.add_widget(self.lessons_layout) 

        # Кнопка Добавить занятие 
        dobavitUrok_button = Button(background_normal='',background_color=[0.09, 0.56, 0.95, 1],text="+ Добавить занятие", size_hint_y=None, height=40) 
        dobavitUrok_button.bind(on_press=self.dobavitUrok) 
        self.layout.add_widget(dobavitUrok_button) 

        # Кнопка Назад 
        back_button = Button(background_normal='',background_color=[0.09, 0.56, 0.95, 1], text="Назад", size_hint_y=None, height=40) 
        back_button.bind(on_press=self.go_back) 
        self.layout.add_widget(back_button) 

        # Загружаем занятия 
        self.add_widget(self.layout) 

    def on_pre_enter(self): 
        # Load lessons each time the screen is entered 
        self.load_lessons() 

    def load_lessons(self): 
        self.lessons_layout.clear_widgets()  # Clear previous lessons 

        if os.path.exists('lessons.json'): 
            with open('lessons.json', 'r', encoding='utf-8') as f: 
                lessons = json.load(f)

                # Получаем сегодняшнюю дату и дату через 7 дней
                today = datetime.now().date()
                end_date = today + timedelta(days=7)

                # Группируем занятия по дате
                grouped_lessons = {}
                for lesson in lessons:
                    lesson_date = datetime.strptime(lesson['date'], '%d.%m.%Y').date()

                    if today <= lesson_date <= end_date:
                        if lesson_date not in grouped_lessons:
                            grouped_lessons[lesson_date] = []
                        grouped_lessons[lesson_date].append(lesson)

                # Отображаем занятия
                for date, lessons in sorted(grouped_lessons.items()):
                    date_label = Label(color=(.1,.1,.1, 1),text=date.strftime('%d-%m-%Y'), size_hint_y=None, height=40)
                    self.lessons_layout.add_widget(date_label)

                    for lesson in lessons:
                        lesson_button = Button(background_normal='',background_color=[0.09, 0.56, 0.95, 0.5], 
                            text=f"{lesson['time']} - {', '.join(lesson['student'])}", 
                            size_hint_y=None, 
                            height=40 
                        ) 
                        lesson_button.bind(on_press=lambda instance, l=lesson: self.open_lesson_details(l)) 
                        self.lessons_layout.add_widget(lesson_button)
        else: 
            self.lessons_layout.add_widget(Label(text="Нет занятий", size_hint_y=None, height=40)) 

    def open_lesson_details(self, lesson): 
        App.get_running_app().current_lesson = lesson 
        self.manager.current = 'lesson_details' 

    def dobavitUrok(self, instance): 
        self.manager.current = 'dobavitUrok' 

    def go_back(self, instance): 
        self.manager.current = 'main'
        
class dobavitUrokScreen(Screen):
    def __init__(self, **kwargs):
        super(dobavitUrokScreen, self).__init__(**kwargs)
        self.selected_students = []
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Title
        title_label = Label(color=(.1,.1,.1,1),text="Добавить занятие", size_hint_y=None, height=50, font_size=24)
        main_layout.add_widget(title_label)

        # Scroll view for the form
        scroll_view = ScrollView()
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        scroll_view.add_widget(form_layout)

        # Date and Time section
        date_time_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.day_spinner = Spinner(background_normal='', background_color=[0.09, 0.56, 0.95, 1],text='День', values=[str(i).zfill(2) for i in range(1, 32)], size_hint_x=0.3)
        self.month_spinner = Spinner(background_normal='', background_color=[0.09, 0.56, 0.95, 1],text='Месяц', values=[str(i).zfill(2) for i in range(1, 13)], size_hint_x=0.3)
        self.year_spinner = Spinner(background_normal='', background_color=[0.09, 0.56, 0.95, 1],text='Год', values=[str(year) for year in range(2024, 2027)], size_hint_x=0.4)
        date_time_layout.add_widget(self.day_spinner)
        date_time_layout.add_widget(self.month_spinner)
        date_time_layout.add_widget(self.year_spinner)
        form_layout.add_widget(date_time_layout)

        
        self.time_spinner = Spinner(size_hint_y=None, height=50, background_color=[0.09, 0.56, 0.95, 0.45],text='Время', values=[f"{hour:02d}:{minute:02d}" for hour in range(8, 23) for minute in [0, 45]])
        form_layout.add_widget(self.time_spinner)
        
        # Student selection
        self.student_input = TextInput(hint_text='Поиск ученика', multiline=False, size_hint_y=None, height=40)
        self.student_input.bind(text=self.on_student_input_change)
        form_layout.add_widget(self.student_input)

        self.student_spinner = Spinner(background_normal='', background_color=[0.09, 0.56, 0.95, 1],text='Открыть список учеников', values=[], size_hint_y=None, height=40)
        form_layout.add_widget(self.student_spinner)

        add_student_button = Button(text="Добавить ученика", size_hint_y=None, height=40, background_color=[0.3, 0.6, 1, 1])
        add_student_button.bind(on_press=self.add_student)
        form_layout.add_widget(add_student_button)

        self.selected_students_label = Label(color=(.1,.1,.1,1),text="Добавленные ученики: ", size_hint_y=None, height=40)
        form_layout.add_widget(self.selected_students_label)

        # Lesson details
        self.duration_spinner = Spinner(background_normal='', background_color=[0.09, 0.56, 0.95, 1],text='Длительность занятия', values=['1','2','3','4'], size_hint_y=None, height=40)
        form_layout.add_widget(self.duration_spinner)

        subscription_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.subscription_label = Label(color=(.1,.1,.1,1),text='Абонемент')
        self.subscription_switch = Switch(active=False)
        self.subscription_switch.bind(active=self.on_switch_active)
        subscription_layout.add_widget(self.subscription_label)
        subscription_layout.add_widget(self.subscription_switch)
        form_layout.add_widget(subscription_layout)

        self.price_input = TextInput(hint_text='Цена занятия', multiline=False, size_hint_y=None, height=40)
        form_layout.add_widget(self.price_input)

        # Add lesson button
        add_lesson_button = Button(background_normal='', background_color=[0.09, 0.56, 0.4, 1],text="Добавить занятие", size_hint_y=None, height=50)
        add_lesson_button.bind(on_press=self.save_lesson)
        form_layout.add_widget(add_lesson_button)

        # Back button
        back_button = Button(background_normal='',
                             background_color=[0.68, 0.17, 0.07, 1],text="Назад", size_hint_y=None, height=50)
        back_button.bind(on_press=self.go_back)
        form_layout.add_widget(back_button)

        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        # Load students
        self.load_students()
    
    

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def set_date(self, day, month, year):
        self.day_spinner.text = str(day)
        self.month_spinner.text = str(month).zfill(2)
        self.year_spinner.text = str(year)

    def load_students(self):
        if os.path.exists('students.json'):
            with open('students.json', 'r', encoding='utf-8') as f:
                students = json.load(f)
                self.all_students = [student['name'] for student in students]
                self.student_spinner.values = self.all_students

    def on_student_input_change(self, instance, value):
        filtered_students = [student for student in self.all_students if value.lower() in student.lower()]
        self.student_spinner.values = filtered_students if filtered_students else ['Нет результатов']

    def add_student(self, instance):
        student_name = self.student_spinner.text
        if student_name and student_name not in self.selected_students and student_name != 'Нет результатов':
            self.selected_students.append(student_name)
            self.update_selected_students_label()

    def update_selected_students_label(self):
        students_text = ", ".join(self.selected_students) if self.selected_students else "Нет добавленных учеников"
        self.selected_students_label.text = f"Добавленные ученики: {students_text}"

    def on_switch_active(self, switch, value):
        self.subscription_label.text = 'Абонемент' if value else 'Без абонемента'

    def save_lesson(self, instance):
        day = self.day_spinner.text
        month = self.month_spinner.text
        year = self.year_spinner.text
        time = self.time_spinner.text
        duration = self.duration_spinner.text
        subscription = "True" if self.subscription_switch.active else "False"
        price = self.price_input.text

        if day != 'День' and month != 'Месяц' and year != 'Год' and time != 'Время' and self.selected_students and price:
            new_lesson = {
                'date': f"{day}.{month}.{year}",
                'time': time,
                'student': self.selected_students,
                'subscription': subscription,
                'duration': duration,
                'price': price
            }

            if os.path.exists('lessons.json'):
                with open('lessons.json', 'r+', encoding='utf-8') as f:
                    lessons = json.load(f)
                    lessons.append(new_lesson)
                    f.seek(0)
                    f.truncate()
                    json.dump(lessons, f, ensure_ascii=False, indent=4)
            else:
                with open('lessons.json', 'w', encoding='utf-8') as f:
                    json.dump([new_lesson], f, ensure_ascii=False, indent=4)

            self.reset_form()
            self.manager.current = 'lessons'
        else:
            self.show_error_popup('Пожалуйста, заполните все поля и выберите хотя бы одного ученика.')

    def reset_form(self):
        self.day_spinner.text = 'День'
        self.month_spinner.text = 'Месяц'
        self.year_spinner.text = 'Год'
        self.time_spinner.text = 'Время'
        self.student_spinner.text = 'Выберите ученика'
        self.subscription_switch.active = False
        self.selected_students = []
        self.update_selected_students_label()
        self.duration_spinner.text = 'Длительность занятия'
        self.price_input.text = ''

    def show_error_popup(self, message):
        popup = Popup(title='Ошибка',
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    

    def go_back(self, instance):
        self.manager.current = 'lessons'

    def on_pre_enter(self):
        self.load_students()

class LessonDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super(LessonDetailsScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, spacing=10, padding=10)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # white background
            self.rect = Rectangle(size=(2000, 3000))

        self.title_label = Label(text="Детали занятия", size_hint_y=None, height=40, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.title_label)

        self.date_label = Label(text="", size_hint_y=None, height=30, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.date_label)

        self.time_label = Label(text="", size_hint_y=None, height=30, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.time_label)

        self.students_label = Label(text="", size_hint_y=None, height=30, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.students_label)

        self.subscription_label = Label(text="", size_hint_y=None, height=30, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.subscription_label)

        self.duration_label = Label(text="", size_hint_y=None, height=30, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.duration_label)

        self.price_label = Label(text="", size_hint_y=None, height=30, color=(0.1, 0.1, 0.1, 1))
        self.layout.add_widget(self.price_label)

        self.edit_button = Button(text="Редактировать", size_hint_y=None, height=40, background_color=[0.09, 0.56, 0.95, 0.4])
        self.edit_button.bind(on_press=self.edit_lesson)
        self.layout.add_widget(self.edit_button)

        self.delete_button = Button(text="Удалить занятие", size_hint_y=None, height=40, background_color=[0.95, 0.09, 0.09, 0.4])
        self.delete_button.bind(on_press=self.delete_lesson)
        self.layout.add_widget(self.delete_button)

        back_button = Button(text="Назад", size_hint_y=None, height=40, background_color=[0.09, 0.56, 0.95, 0.4])
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        lesson = App.get_running_app().current_lesson
        if lesson:
            self.date_label.text = f"Дата: {lesson['date']}"
            self.time_label.text = f"Время: {lesson['time']}"
            self.students_label.text = f"Ученики: {', '.join(lesson['student'])}"
            self.subscription_label.text = f"Абонемент: {'Да' if lesson['subscription'] == 'True' else 'Нет'}"
            self.duration_label.text = f"Длительность: {lesson['duration']} час(а)"
            self.price_label.text = f"Цена: {lesson['price']} руб."

    def edit_lesson(self, instance):
        app = App.get_running_app()
        app.root.transition.direction = 'left'
        app.root.current = 'edit_lesson'

    def delete_lesson(self, instance):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Вы уверены, что хотите удалить это занятие?'))
        buttons = BoxLayout()
        yes_button = Button(text='Да', size_hint=(None, None), size=(100, 50))
        no_button = Button(text='Нет', size_hint=(None, None), size=(100, 50))
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)

        popup = Popup(title='Подтверждение удаления', content=content, size_hint=(None, None), size=(300, 200))

        def confirm_delete(instance):
            self.perform_delete()
            popup.dismiss()

        def cancel_delete(instance):
            popup.dismiss()

        yes_button.bind(on_press=confirm_delete)
        no_button.bind(on_press=cancel_delete)

        popup.open()

    def perform_delete(self):
        app = App.get_running_app()
        lesson_to_delete = app.current_lesson
        
        with open('lessons.json', 'r', encoding='utf-8') as f:
            lessons = json.load(f)
        
        lessons = [lesson for lesson in lessons if lesson != lesson_to_delete]
        
        with open('lessons.json', 'w', encoding='utf-8') as f:
            json.dump(lessons, f, ensure_ascii=False, indent=4)
        
        app.root.transition.direction = 'right'
        app.root.current = 'lessons'
        
        # Обновляем список уроков на экране уроков
        lessons_screen = app.root.get_screen('lessons')
        lessons_screen.load_lessons()

    def go_back(self, instance):
        self.manager.current = 'lessons'

class EditLessonScreen(Screen):
    def __init__(self, **kwargs):
        super(EditLessonScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, spacing=10, padding=10)
        with self.canvas.before:
            Color(.98, .95, .95, 1)
            self.rect = Rectangle(size=(2000, 3000))
        
    
      #  self.title_label = Label(color=(.1,.1,.1, 1),text="Редактирование занятия", size_hint_y=None, height=40)
        #self.layout.add_widget(self.title_label)
        
        self.layout = GridLayout(cols=2,padding=10)
        self.date_label = Label(color=(.1,.1,.1, 1),text="Дата",size_hint_y=None,size_hint_x=0.3, height=40) #,
        self.layout.add_widget(self.date_label)

        self.date_input = TextInput(hint_text="Дата (ДД.ММ.ГГГГ)", size_hint_y=None,size_hint_x=0.7, height=40)
        self.layout.add_widget(self.date_input)
        
        self.time_label = Label(color=(.1,.1,.1, 1),text="Время",size_hint_y=None,size_hint_x=0.3, height=40) #,
        self.layout.add_widget(self.time_label)

        self.time_input = TextInput(hint_text="Время", size_hint_y=None, height=40)
        self.layout.add_widget(self.time_input)
        
        self.students_label = Label(color=(.1,.1,.1, 1),text="Ученики",size_hint_y=None,size_hint_x=0.3, height=40) #,
        self.layout.add_widget(self.students_label)

        self.students_input = TextInput(hint_text="Ученики (через запятую)", size_hint_y=None, height=40)
        self.layout.add_widget(self.students_input)
        
        self.subscription_label = Label(font_size='10sp',color=(.1,.1,.1, 1),text="Абонемент (True/False)",size_hint_y=None,size_hint_x=0.3, height=40) #,
        self.layout.add_widget(self.subscription_label)

        self.subscription_input = TextInput(hint_text="Абонемент (True/False)", size_hint_y=None, height=40)
        self.layout.add_widget(self.subscription_input)

        self.duration_label = Label(color=(.1,.1,.1, 1),text="Длительность",size_hint_y=None,size_hint_x=0.3, height=40) #,
        self.layout.add_widget(self.duration_label)
        
        self.duration_input = TextInput(hint_text="Длительность", size_hint_y=None, height=40)
        self.layout.add_widget(self.duration_input)

        self.price_label = Label(color=(.1,.1,.1, 1),text="Цена",size_hint_y=None,size_hint_x=0.3, height=40) #,
        self.layout.add_widget(self.price_label)
        
        self.price_input = TextInput(hint_text="Цена", size_hint_y=None, height=40)
        self.layout.add_widget(self.price_input)
        
        self.save_button = Button(text="Сохранить", size_hint_y=None, height=40)
        self.save_button.bind(on_press=self.save_changes)
        self.layout.add_widget(self.save_button)
        
        self.cancel_button = Button(background_normal='',
                             background_color=[0.68, 0.17, 0.07, 1],text="Отмена", size_hint_y=None, height=40)
        self.cancel_button.bind(on_press=self.cancel_edit)
        self.layout.add_widget(self.cancel_button)
        
        self.add_widget(self.layout)

    def on_pre_enter(self):
        lesson = App.get_running_app().current_lesson
        if lesson:
            self.date_input.text = lesson['date']
            self.time_input.text = lesson['time']
            self.students_input.text = ', '.join(lesson['student'])
            self.subscription_input.text = str(lesson['subscription'])
            self.duration_input.text = lesson['duration']
            self.price_input.text = lesson['price']

    def save_changes(self, instance):
        app = App.get_running_app()
        edited_lesson = {
            'date': self.date_input.text,
            'time': self.time_input.text,
            'student': [s.strip() for s in self.students_input.text.split(',')],
            'subscription': self.subscription_input.text,
            'duration': self.duration_input.text,
            'price': self.price_input.text
        }
        
        with open('lessons.json', 'r', encoding='utf-8') as f:
            lessons = json.load(f)
        
        for i, lesson in enumerate(lessons):
            if lesson == app.current_lesson:
                lessons[i] = edited_lesson
                break
        
        with open('lessons.json', 'w', encoding='utf-8') as f:
            json.dump(lessons, f, ensure_ascii=False, indent=4)
        
        app.current_lesson = edited_lesson
        app.root.transition.direction = 'right'
        app.root.current = 'lesson_details'
        
        # Обновляем информацию на экране деталей урока
        details_screen = app.root.get_screen('lesson_details')
        details_screen.on_pre_enter()

    def cancel_edit(self, instance):
        app = App.get_running_app()
        app.root.transition.direction = 'right'
        app.root.current = 'lesson_details'

class StudentProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(StudentProfileScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # white color
            self.rect = Rectangle(size = (2000, 3000))
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.scroll_view = ScrollView()
        self.scroll_view.add_widget(self.layout)
        self.add_widget(self.scroll_view)

    def on_pre_enter(self):
        self.layout.clear_widgets()
        student = App.get_running_app().current_student
        if student:
            # Аватар
            avatar = AsyncImage(source=student.get('photo', ''), size_hint=(None, None), size=(200, 200))
            self.layout.add_widget(avatar)

            # Основная информация
            self.add_info("Имя:", student.get('name', ''))
            self.add_info("Номер телефона:", student.get('phone', ''))
            self.add_info("Надежность:", student.get('trustability', ''))
            self.add_info("Прогресс:", student.get('progress', ''))
            self.add_info("Заметки:", student.get('notes', ''))
            
            make_call_button = Button(text="Позвонить",size_hint_y=None, height=40)
            make_call_button.bind(on_press=self.make_call)
            self.layout.add_widget(make_call_button)
            
            # Родитель/Ребенок
            if student.get('parent'):
                parent_button = Button(text=f"Родитель: {student['parent']}", size_hint_y=None, height=40,background_color=[0.09, 0.56, 0.95, 0.4])
                parent_button.bind(on_press=lambda x: self.go_to_profile(student['parent']))
                self.layout.add_widget(parent_button)
            if student.get('children'):
                child_button = Button(text=f"Ребенок: {student['children']}", size_hint_y=None, height=40,background_color=[0.09, 0.56, 0.95, 0.4])
                child_button.bind(on_press=lambda x: self.go_to_profile(student['children']))
                self.layout.add_widget(child_button)

            # Список занятий
            self.add_lessons_list(student)

            # Статистика
            self.add_statistics(student)

            # Кнопка редактирования
            edit_button = Button(text="Редактировать профиль", size_hint_y=None, height=40,background_color=[0.89, 0.67, 0.07, 0.7])
            edit_button.bind(on_press=self.go_to_edit_profile)
            self.layout.add_widget(edit_button)

            # Кнопка "Назад"
            back_button = Button(text="Назад", size_hint_y=None, height=40,background_color=[0.09, 0.56, 0.95, 0.4])
            back_button.bind(on_press=self.go_back)
            self.layout.add_widget(back_button)

    def add_info(self, label, value):
        info = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        info.add_widget(Label(color=(.1,.1,.1, 1),text=label, size_hint_x=0.4))
        info.add_widget(Label(color=(.1,.1,.1, 1),text=str(value), size_hint_x=0.6))
        self.layout.add_widget(info)

    def add_lessons_list(self, student):
        self.layout.add_widget(Label(color=(.1,.1,.1, 1),text="Список занятий:", size_hint_y=None, height=30))
        with open('lessons.json', 'r', encoding='utf-8') as f:
            lessons = json.load(f)
        for lesson in lessons:
            if student['name'] in lesson['student']:
                lesson_button = Button(background_color=[0.09, 0.56, 0.95, 1],text=f"{lesson['date']} - {lesson['time']}", size_hint_y=None, height=30)
                lesson_button.bind(on_press=lambda x, lesson=lesson: self.go_to_lesson(lesson))
                self.layout.add_widget(lesson_button)

    def add_statistics(self, student):
        total_hours = 0
        total_cost = 0
        with open('lessons.json', 'r', encoding='utf-8') as f:
            lessons = json.load(f)
        for lesson in lessons:
            if student['name'] in lesson['student']:
                total_hours += int(lesson['duration'])
                total_cost += int(lesson['price'])
        self.add_info("Общее количество часов:", f"{total_hours} ч")
        self.add_info("Общая стоимость занятий:", f"{total_cost} руб")

    def go_to_profile(self, name):
        with open('students.json', 'r', encoding='utf-8') as f:
            students = json.load(f)
        for student in students:
            if student['name'] == name:
                App.get_running_app().current_student = student
                self.manager.current = 'StudentProfile'
                break

    def go_to_lesson(self, lesson):
        App.get_running_app().current_lesson = lesson
        self.manager.current = 'lesson_details'

    def go_to_edit_profile(self, instance):
        self.manager.current = 'edit_student_profile'
    
    def make_call(self, current_student):
        try:
                     
           call.make_call(self.phone_number)
            
        except Exception as e:
            print(f"Ошибка при выполнении вызова: {e}")

    def go_back(self, instance):
        self.manager.current = 'students'

class EditStudentProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(EditStudentProfileScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2, spacing=10, padding=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        with self.canvas.before:
            Color(1, 1, 1, 1)  # white color
            self.rect = Rectangle(size = (2000, 3000))
        
        self.scroll_view = ScrollView()
        self.scroll_view.add_widget(self.layout)
        self.add_widget(self.scroll_view)
        

        self.name_label = Label(text="ИМЯ",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.name_label)
        self.name_input = TextInput(hint_text="Имя", size_hint_y=None,size_hint_x =2, height=40)
        self.layout.add_widget(self.name_input)

        self.phone_label = Label(text="ТЕЛЕФОН",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.phone_label)
        self.phone_input = TextInput(hint_text="Номер телефона", size_hint_y=None, height=40)
        self.layout.add_widget(self.phone_input)

        self.trustability_label = Label(text="Надежность",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.trustability_label)
        self.trustability_input = TextInput(hint_text="Надежность", size_hint_y=None, height=40)
        self.layout.add_widget(self.trustability_input)

        self.progress_label = Label(text="Прогресс",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.progress_label)
        self.progress_input = TextInput(hint_text="Прогресс", size_hint_y=None, height=40)
        self.layout.add_widget(self.progress_input)

        self.notes_label = Label(text="Заметки",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.notes_label)
        self.notes_input = TextInput(hint_text="Заметки", size_hint_y=None, height=100, multiline=True)
        self.layout.add_widget(self.notes_input)
        
        self.parent_label = Label(text="Родитель",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.parent_label)
        self.parent_input = TextInput(hint_text="Родитель", size_hint_y=None, height=40)
        self.layout.add_widget(self.parent_input)

        self.children_label = Label(text="Ребенок",color=(.1,.1,.1, 1),size_hint_y=None, height=40)
        self.layout.add_widget(self.children_label)
        self.children_input = TextInput(hint_text="Ребенок", size_hint_y=None, height=40)
        self.layout.add_widget(self.children_input)

        back_button = Button(text="Назад", size_hint_y=None, height=40,background_color=[0.09, 0.56, 0.95, 0.4])
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)
        
        save_button = Button(text="Сохранить изменения", size_hint_y=None, height=40,background_color=[0.09, 0.95, 0.09, 0.4])
        save_button.bind(on_press=self.save_changes)
        self.layout.add_widget(save_button)

        

    def on_pre_enter(self):
        student = App.get_running_app().current_student
        if student:
            self.name_input.text = student.get('name', '')
            self.phone_input.text = student.get('phone', '')
            self.trustability_input.text = student.get('trustability', '')
            self.progress_input.text = student.get('progress', '')
            self.notes_input.text = student.get('notes', '')
            self.parent_input.text = student.get('parent', '')
            self.children_input.text = student.get('children', '')

    def save_changes(self, instance):
        app = App.get_running_app()
        student = app.current_student

        if student:
            # Обновляем данные студента
            student['name'] = self.name_input.text
            student['phone'] = self.phone_input.text
            student['trustability'] = self.trustability_input.text
            student['progress'] = self.progress_input.text
            student['notes'] = self.notes_input.text
            student['parent'] = self.parent_input.text
            student['children'] = self.children_input.text

            # Обновляем JSON файл
            with open('students.json', 'r', encoding='utf-8') as f:
                students = json.load(f)

            for i, s in enumerate(students):
                if s['name'] == app.current_student['name']:
                    students[i] = student
                    break

            with open('students.json', 'w', encoding='utf-8') as f:
                json.dump(students, f, ensure_ascii=False, indent=4)

            # Обновляем текущего студента в приложении
            app.current_student = student

            # Показываем подтверждение
            popup = Popup(title='Успех',
                          content=Label(text='Профиль студента успешно обновлен'),
                          size_hint=(None, None), size=(300, 200))
            popup.open()

            # Возвращаемся на экран профиля
            self.manager.current = 'StudentProfile'
        else:
            # Показываем ошибку, если студент не найден
            popup = Popup(title='Ошибка',
                          content=Label(text='Студент не найден'),
                          size_hint=(None, None), size=(300, 200))
            popup.open()

    def go_back(self, instance):
        self.manager.current = 'StudentProfile'

class Add_studentScreen(Screen):
    def __init__(self, **kwargs):
        super(Add_studentScreen, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=(2000, 3000))

        layout = GridLayout(cols=1,spacing=10)
        title_label = Label(text="Добавить ученика", size_hint_y=None, height=40)
        layout.add_widget(title_label)

        self.name_input = TextInput(hint_text="Имя ученика", size_hint_y=None, height=40)
        layout.add_widget(self.name_input)

        self.phone_input = TextInput(hint_text="Телефон ученика",text='+7', size_hint_y=None, height=40)
        layout.add_widget(self.phone_input)

        add_button = Button(background_normal='', 
            background_color=[0.09, 0.56, 0.95, 1],
            text="Добавить", size_hint_y=None, height=40,bold=True)
        add_button.bind(on_press=self.save_student)
        layout.add_widget(add_button)

        back_button = Button(background_normal='', 
            background_color=[0.68, 0.17, 0.07, 1],
            text="Назад", size_hint_y=None, height=40,bold=True)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def save_student(self, instance):
        name = self.name_input.text
        phone = self.phone_input.text

        if name and phone:
            new_student = {'name': name, 'phone': phone}
            if os.path.exists('students.json'):
                with open('students.json', 'r+', encoding='utf-8') as f:
                    students = json.load(f)
                    students.append(new_student)
                    f.seek(0)  # Вернуться в начало файла
                    json.dump(students, f, ensure_ascii=False, indent=4)
            else:
                with open('students.json', 'w', encoding='utf-8') as f:
                    json.dump([new_student], f, ensure_ascii=False, indent=4)

            self.name_input.text = ""
            self.phone_input.text = ""
            self.manager.current = 'students'  # Вернуться на экран студентов
            

    def go_back(self, instance):
        self.manager.current = 'students'

class CalendarApp(App):
    current_student = None
    current_lesson = None
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(MessageScreen(name='message'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(StudentsScreen(name='students'))
        sm.add_widget(lessonsScreen(name='lessons'))
        sm.add_widget(Add_studentScreen(name='add_student'))
        sm.add_widget(dobavitUrokScreen(name='dobavitUrok'))
        sm.add_widget(StudentProfileScreen(name='StudentProfile'))
        sm.add_widget(LessonDetailsScreen(name='lesson_details'))
        sm.add_widget(EditLessonScreen(name='edit_lesson'))  
        sm.add_widget(EditStudentProfileScreen(name='edit_student_profile'))
        return sm

#Fucking rock n roll

class CustomButton(Label):
    def __init__(self, text, **kwargs):
        super().__init__(text=text, **kwargs)
        self.bind(size=self._update_rect, texture_size=self.setter('text_size'))
        self.text_size = (self.width, None)  # Позволяет тексту переноситься
        self.halign = 'center'  # Выравнивание текста по центру
        self.valign = 'middle'  # Вертикальное выравнивание
       
             # Связываем изменение размера с изменением размера шрифта
        self.bind(size=self._update_font_size)

    def _update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 1)
            Rectangle(pos=self.pos, size=self.size)

    def _update_font_size(self, *args):
        # Изменяем размер шрифта в зависимости от высоты кнопки
        self.font_size = self.height * 0.3  # Например, 20% от высоты кнопки

    def _update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 0.05)  # Цвет фона кнопки
            Rectangle(pos=self.pos, size=self.size)

   

if __name__ == '__main__':
    CalendarApp().run()