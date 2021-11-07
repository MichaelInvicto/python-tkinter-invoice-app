from flask_sqlalchemy import SQLAlchemy
from tkinter import messagebox
from functools import partial
from tkcalendar import *
from flask import Flask
from tkinter import *
import datetime
import math


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoice.db'
db = SQLAlchemy(app)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    description = db.Column(db.String(350), unique=False, nullable=False)
    statement = db.Column(db.String(15), unique=False, nullable=False)
    amount = db.Column(db.String(18), unique=False, nullable=False)
    date = db.Column(db.String(18), unique=False, nullable=False)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


class InvoiceUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(18), unique=False, nullable=False)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

# Since this is the offline version, we have to make all these global variables


data = db.session.query(Invoice).all()
all_data = [datum.to_dict() for datum in data]
users_name = ''


# This class is responsible for the making of the app and the movement between pages and their respective configurations
class InvoiceApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        Tk.wm_title(self, 'Invoice App')

        container = Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (DataPage, NewInvoice, LoginPage, RegisterPage, ForgotPasswordPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.set_screen('LoginPage')

    def set_screen(self, which_one):
        # We set the configurations for the pages
        if which_one == 'DataPage':
            self.wm_title('Invoice App')
            self.wm_geometry('1200x700')
            self.config(bg='#141625')
            self.show_frame(cont=DataPage)

        elif which_one == 'NewInvoice':
            self.wm_title('New Invoice')
            self.geometry('800x700')
            self.config(bg='#141625')
            self.show_frame(cont=NewInvoice)

        elif which_one == 'LoginPage':
            self.wm_title('Login Page')
            self.geometry('600x550')
            self.config(bg='#141625')
            self.show_frame(cont=LoginPage)

        elif which_one == 'RegisterPage':
            self.wm_title('Register Page')
            self.geometry('500x600')
            self.config(bg='#141625')
            self.show_frame(cont=RegisterPage)

        elif which_one == 'ForgotPasswordPage':
            self.wm_title('Forgot Password Page')
            self.geometry('580x500')
            self.config(bg='#141625')
            self.show_frame(cont=ForgotPasswordPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# This is the page where the information will be displayed
class DataPage(Frame):

    def __init__(self, parent, controller):
        # This is where we set the backbone for our app

        Frame.__init__(self, parent)
        Frame.config(self, bg='#141625')
        Frame.config(self, padx=120, pady=10)

        self.view_description_image = PhotoImage(file='images/view description.png')
        self.invoice_button_image = PhotoImage(file='images/new invoice.png')
        self.previous_button_image = PhotoImage(file='images/previous.png')
        self.next_button_image = PhotoImage(file='images/next.png')
        self.go_button_image = PhotoImage(file='images/go.png')
        self.load_page_1_button_image = PhotoImage(file='images/load page.png')

        self.BG = '#141625'
        self.BUTTON_BG = '#7C5DF9'
        self.FRAME_BG = '#1F213A'
        self.total_invoices = len(all_data)
        self.PAGE_NUM = 0
        self.clicked = False

        self.balance = int()
        self.refined_balance = str()

        self.refined_balance = self.get_balance()

        self.all_frames = []
        self.all_buttons = []
        self.all_descriptions = []
        self.all_colours = []

        self.frame1 = Frame(self, bg=self.BG)
        self.frame1.grid(row=1, column=1)

        self.invoice_label = Label(self.frame1, text='Invoices', font=('Georgia', 25, 'bold'), bg=self.BG, fg='white')
        self.invoice_label.grid(row=1, column=1)

        self.total_invoices_label = Label(self.frame1, text=f'There are {self.total_invoices} total invoices',
                                          font=('Georgia', 9), bg=self.BG, fg='white')
        self.total_invoices_label.grid(row=2, column=1)

        self.new_invoice_button = Button(self.frame1, image=self.invoice_button_image, bg=self.BG, borderwidth=0,
                                         width=200, height=45, activebackground=self.BG,
                                         command=lambda: controller.set_screen('NewInvoice'))
        self.new_invoice_button.grid(row=1, column=2, padx=(300, 0))

        self.frame2 = Frame(self, bg=self.BG)
        self.frame2.grid(row=2, column=1)

        self.load_button = Button(self.frame2, image=self.load_page_1_button_image, command=self.start_page, bg=self.BG,
                                  activebackground=self.BG, borderwidth=0)
        self.load_button.grid(row=1, column=1)

        self.display_page_num = Label(self.frame2, text=f"Page {self.PAGE_NUM}/{self.total_invoices % 4}",
                                      font=('Georgia', 15), fg='gray', bg=self.BG)

        self.frame3 = Frame(self, bg='#1F213A')
        self.frame3.grid(row=3, column=1, pady=(15, 25))

        self.invoice1 = Canvas(self.frame3, width=980, height=60, bg='#1F213A', highlightthickness=0)
        self.invoice1.grid(row=1, column=1)
        self.invoice1.create_text(60, 30, text='Date', font=('Georgia', 15), fill='gray')
        self.invoice1.create_text(320, 30, text='Posted By', font=('Georgia', 15), fill='gray')
        self.invoice1.create_text(500, 30, text='Statement', font=('Georgia', 15), fill='gray')
        self.invoice1.create_text(690, 30, text='Amount', font=('Georgia', 15), fill='gray')
        self.invoice1.create_text(900, 30, text='Description', font=('Georgia', 15), fill='gray')

        self.frame4 = Frame(self, bg='#1F213A')
        self.frame4.grid(row=3, column=1, pady=(15, 25))

        # In order to display the information in rows of 4, we need to use a for loop

        for i in range(4):
            self.frame3 = Frame(self, bg=self.FRAME_BG)
            self.frame3.grid(row=i + 4, column=1, pady=(15, 15))

            self.invoice_data = Canvas(self.frame3, width=820, height=60, bg='#1F213A', highlightthickness=0)
            self.invoice_data.grid(row=i, column=1)

            date = ''
            name = ''
            statement = ''
            amount = ''
            description_text = ''
            current_colour = ''

            self.date = self.invoice_data.create_text(60, 30, text=date, font=('Georgia', 10), fill='gray')
            self.name = self.invoice_data.create_text(320, 30, text=name, font=('Georgia', 15), fill='white')
            self.statement_text = self.invoice_data.create_text(500, 30, text=statement, font=('Georgia', 15),
                                                                fill=current_colour)
            self.amount_text = self.invoice_data.create_text(690, 30, text=amount, font=('Georgia', 18, 'bold'),
                                                             fill='white')

            self.description_label = Label(self.frame3, text=description_text, font=('Georgia', 15, 'italic'),
                                           fg='gray', bg=self.FRAME_BG)

            self.description_button = Button(self.frame3, image=self.view_description_image, borderwidth=0,
                                             bg=self.FRAME_BG, command=partial(self.description_button_clicked, i),
                                             activebackground=self.FRAME_BG)

            self.all_frames.append(self.invoice_data)
            self.all_buttons.append(self.description_button)
            self.all_descriptions.append(self.description_label)
            self.all_colours.append(current_colour)

        self.frame5 = Frame(self, bg=self.BG)
        self.frame5.grid(row=8, column=1)
        self.previous_button = Button(self.frame5, image=self.previous_button_image, command=self.previous_page,
                                      bg=self.BG, activebackground=self.BG, borderwidth=0)

        self.next_button = Button(self.frame5, image=self.next_button_image, command=self.next_page, bg=self.BG,
                                  activebackground=self.BG, borderwidth=0)

        self.go_to_page_label = Label(self.frame5, text='Go To Page: ', font=('Georgia', 12), fg='gray', bg=self.BG)

        self.go_to_page_entry = Entry(self.frame5, width=5, bg=self.FRAME_BG, fg='white')

        self.go_to_page_button = Button(self.frame5, image=self.go_button_image, command=self.go_to_page, bg=self.BG,
                                        activebackground=self.BG, borderwidth=0)
        self.go_to_page_entry.configure(insertbackground='white')

        self.frame6 = Frame(self, bg=self.BG)
        self.frame6.grid(row=9, column=1)

        self.current_balance = Label(self.frame6, text=f"Current Balance: {self.refined_balance}", font=('Georgia', 20),
                                     fg='gray', bg=self.BG)

    def get_balance(self):
        self.balance = 0
        for datum in all_data:
            current = datum['amount'].strip('N').replace(',', '')
            if datum['statement'].lower() == 'sale' or datum['statement'].lower() == 'credit':
                self.balance += int(current)
            else:
                self.balance -= int(current)

        return 'N' + "{:,}".format(self.balance)

    def total_pages(self, num):
        if num % 4 == 0:
            return int(num / 4)
        else:
            calc = math.floor(num / 4)
            return calc + 1

    def start_page(self):
        global data
        global all_data

        data = db.session.query(Invoice).all()
        all_data = [datum.to_dict() for datum in data]

        self.refined_balance = self.get_balance()

        self.total_invoices = len(all_data)

        self.total_invoices_label.config(text=f"There are {self.total_invoices} total invoices")

        self.current_balance.config(text=f"Current Balance: {self.refined_balance}")

        self.PAGE_NUM = 0
        self.display_page_num.grid(row=2, column=1)
        self.go_to_page_label.grid(row=1, column=3, padx=(40, 0))
        self.go_to_page_entry.grid(row=1, column=4)
        self.go_to_page_button.grid(row=1, column=5, padx=(20, 0))
        self.current_balance.grid(row=1, column=1, pady=(10, 0))
        self.next_button.grid(row=1, column=2, padx=(40, 0))
        self.previous_button.grid(row=1, column=1)

        if not self.PAGE_NUM:
            self.next_page()

    def next_page(self):
        if self.PAGE_NUM + 1 <= self.total_pages(self.total_invoices):
            self.PAGE_NUM += 1
            self.display_page_num.config(text=f"Page {self.PAGE_NUM}/{self.total_pages(self.total_invoices)}")

            for i in range(4):
                self.all_descriptions[i].grid_forget()
            self.clicked = False

            if self.PAGE_NUM <= int((self.total_invoices - (self.total_invoices) % 4) / 4):
                for i in range(4):
                    self.all_colours[i] = self.check_colour(all_data[(self.PAGE_NUM * 4) - 4 + i]['statement'])
                    the_statement = all_data[(self.PAGE_NUM * 4) - 4 + i]['statement']

                    self.all_frames[i].config(width=820)
                    self.all_buttons[i].grid(row=i, column=2, padx=(0, 20))

                    self.all_frames[i].itemconfig(self.date, text=all_data[(self.PAGE_NUM * 4) - 4 + i]['date'])
                    self.all_frames[i].itemconfig(self.name, text=all_data[(self.PAGE_NUM * 4) - 4 + i]['name'])
                    self.all_frames[i].itemconfig(self.statement_text, text=the_statement,
                                                  fill=self.all_colours[i])
                    self.all_frames[i].itemconfig(self.statement_text)
                    self.all_frames[i].itemconfig(self.amount_text,
                                                  text=all_data[(self.PAGE_NUM * 4) - 4 + i]['amount'])
            else:
                for i in range(self.total_invoices % 4):
                    self.all_frames[i].config(width=820)
                    self.all_colours[i] = self.check_colour(all_data[(self.PAGE_NUM * 4) - 4 + i]['statement'])
                    self.all_buttons[i].grid(row=i, column=2, padx=(0, 20))

                    self.all_frames[i].itemconfig(self.date, text=all_data[(self.PAGE_NUM * 4) - 4 + i]['date'])
                    self.all_frames[i].itemconfig(self.name, text=all_data[(self.PAGE_NUM * 4) - 4 + i]['name'])
                    self.all_frames[i].itemconfig(self.statement_text,
                                                  text=all_data[(self.PAGE_NUM * 4) - 4 + i]['statement'])
                    self.all_frames[i].itemconfig(self.statement_text, fill=self.all_colours[i])
                    self.all_frames[i].itemconfig(self.amount_text,
                                                  text=all_data[(self.PAGE_NUM * 4) - 4 + i]['amount'])

                for i in range(self.total_invoices % 4, 4, 1):
                    self.all_frames[i].config(width=820)
                    self.all_frames[i].itemconfig(self.date, text='')
                    self.all_frames[i].itemconfig(self.name, text='')
                    self.all_frames[i].itemconfig(self.statement_text, text='')
                    self.all_frames[i].itemconfig(self.amount_text, text='')
                    self.all_buttons[i].grid_forget()
        else:
            messagebox.showinfo('Page Error', 'No Next Page')

    def previous_page(self):

        if self.PAGE_NUM - 1 >= 1:
            self.PAGE_NUM -= 1
            self.display_page_num.config(text=f"Page {self.PAGE_NUM}/{self.total_pages(self.total_invoices)}")

            for i in range(4):
                self.all_descriptions[i].grid_forget()
            self.clicked = False

            if self.PAGE_NUM <= int((self.total_invoices - (self.total_invoices) % 4) / 4):
                for i in range(4):
                    self.all_colours[i] = self.check_colour(all_data[(self.PAGE_NUM * 4)-4+i]['statement'])

                    self.all_frames[i].config(width=820)
                    self.all_buttons[i].grid(row=i, column=2, padx=(0, 20))
                    self.all_frames[i].itemconfig(self.date, text=all_data[(self.PAGE_NUM * 4)-4+i]['date'])
                    self.all_frames[i].itemconfig(self.name, text=all_data[(self.PAGE_NUM * 4)-4+i]['name'])
                    self.all_frames[i].itemconfig(self.statement_text,
                                                  text=all_data[(self.PAGE_NUM * 4)-4+i]['statement'])

                    self.all_frames[i].itemconfig(self.statement_text, fill=self.all_colours[i])
                    self.all_frames[i].itemconfig(self.amount_text, text=all_data[(self.PAGE_NUM * 4)-4+i]['amount'])
            else:
                for i in range(self.total_invoices % 4):
                    self.all_colours[i] = self.check_colour(all_data[(self.PAGE_NUM * 4)-4+i]['statement'])

                    self.all_frames[i].itemconfig(self.date, text=all_data[(self.PAGE_NUM * 4) - 4 + i]['date'])
                    self.all_frames[i].itemconfig(self.name, text=all_data[(self.PAGE_NUM * 4) - 4 + i]['name'])
                    self.all_frames[i].itemconfig(self.statement_text,
                                                  text=all_data[(self.PAGE_NUM * 4) - 4 + i]['statement'])
                    self.all_frames[i].itemconfig(self.statement_text, fill=self.all_colours[i])

                    self.all_frames[i].itemconfig(self.amount_text,
                                                  text=all_data[(self.PAGE_NUM * 4) - 4 + i]['amount'])
        else:
            messagebox.showinfo('Page Error', 'No Previous Page!')

    def go_to_page(self):
        if (self.go_to_page_entry.get()).isnumeric():

            if int(self.go_to_page_entry.get()) < 1 or int(self.go_to_page_entry.get()) > self.total_pages(self.total_invoices):
                messagebox.showinfo('Page Error', 'The page you requested does not exist!\nPlease check the page number'
                                                  ' and try again')
            elif int(self.go_to_page_entry.get()) == self.PAGE_NUM:
                messagebox.showinfo('Page Error', 'You are already on that page.\nPlease specify another page')
            else:
                if int(self.go_to_page_entry.get()) > self.PAGE_NUM:
                    for i in range(self.PAGE_NUM, int(self.go_to_page_entry.get()), 1):
                        self.next_page()
                if int(self.go_to_page_entry.get()) < self.PAGE_NUM:
                    for i in range(self.PAGE_NUM, int(self.go_to_page_entry.get()), -1):
                        self.previous_page()

        else:
            messagebox.showinfo('Value Error', 'Please make sure you enter only positive whole numbers')

    def description_button_clicked(self, i):
        if not self.clicked:
            the_description = self.shorten_description(all_data[(self.PAGE_NUM * 4)-4+i]['description'])
            self.all_descriptions[i].config(text=the_description)
            self.all_descriptions[i].grid(row=i+2, column=1)
            self.clicked = True
        else:
            self.all_descriptions[i].grid_forget()
            self.clicked = False

    def check_colour(self, colour):
        if colour.lower() == 'sale' or colour.lower() == 'credit':
            return 'green'
        elif colour.lower() == 'expenses' or colour.lower() == 'commission':
            return 'orange'
        else:
            return '#992222'

    def shorten_description(self, description):
        if len(description) <= 50:
            return description
        elif len(description) <= 100:
            return f"{description[:50]}\n{description[50:101]}"
        elif len(description) <= 150:
            return f"{description[:50]}\n{description[50:101]}\n{description[101:150]}"
        elif len(description) <= 200:
            return f"{description[:50]}\n{description[50:101]}\n{description[101:150]}\n{description[150:200]}"
        elif len(description) <= 250:
            return f"{description[:50]}\n{description[50:101]}\n{description[101:150]}\n{description[150:200]}\n" \
                   f"\n{description[200:250]}\n{description[250:300]}"
        else:
            return f"{description[:50]}\n{description[50:101]}\n{description[101:150]}\n{description[150:200]}\n" \
                   f"{description[200:250]}\n{description[250:300]}\n{description[300:350]}"


class NewInvoice(Frame):
    # maximum length of descripton shoould be 350

    def __init__(self, parent, controller):

        # Use the controller.geometry("widthxheight") to set the geometry of the page

        Frame.__init__(self, parent)
        self.controller = controller
        # controller.geometry('700x500') This doesn't seem to work, so set the geometry on the set_screen() method in
        # the InvoiceApp class

        Frame.config(self, bg='#141625')

        self.the_users_name = ''

        self.BG = '#141625'

        self.statement_list = ['Sale', 'Refund', 'Expenses', 'Commission', 'Lent', 'Borrowed', 'Credit', 'Debit']

        self.sv = StringVar()
        self.prevlaue = ''

        self.the_date = ''
        self.the_gotten_statement = ''

        self.statement_window = None
        self.calendar_window = None

        self.click_to_set_name = PhotoImage(file='images/click to set name.png')
        self.click_to_set_date = PhotoImage(file='images/click to set date.png')
        self.click_to_set_statement = PhotoImage(file='images/click to set statement.png')
        self.add_new_invoice_image = PhotoImage(file='images/add new invoice.png')
        self.home_page_image = PhotoImage(file='images/home page.png')

        # back_button = Button(self, text='Home', command=lambda: controller.set_screen('DataPage'), bg='white')
        # back_button.grid(row=1, column=1)

        self.frame1 = Frame(self, bg=self.BG)
        self.frame1.grid(row=1, column=1, sticky='w', pady=(20, 50))

        self.new_invoice_label = Label(self.frame1, text='New Invoice', font=('Georgia', 30, 'bold'), bg=self.BG,
                                       fg='white')
        self.new_invoice_label.grid(row=1, column=1, sticky='w')

        self.frame2 = Frame(self, bg=self.BG)
        self.frame2.grid(row=2, column=1, sticky='w')

        self.name_label = Label(self.frame2, text='Name', bg=self.BG, fg='white', font=('Georgia', 20, 'bold'))
        self.name_label.grid(row=1, column=1, pady=(0, 5), sticky='w')

        self.set_name_button = Button(self.frame2, image=self.click_to_set_name, activebackground=self.BG, bg=self.BG,
                                      borderwidth=0, command=self.set_name)
        self.set_name_button.grid(row=1, column=2, padx=(50, 0))

        self.the_name = Label(self.frame2, text='', bg=self.BG, fg='gray', font=('Georgia', 15))
        self.the_name.grid(row=3, column=1, sticky='w')

        self.date_label = Label(self.frame2, text='Date', bg=self.BG, fg='white', font=('Georgia', 20, 'bold'))
        self.date_label.grid(row=4, column=1, sticky='w', pady=(15, 5))

        self.set_date_button = Button(self.frame2, image=self.click_to_set_date, activebackground=self.BG, bg=self.BG,
                                      borderwidth=0, command=self.set_date)
        self.set_date_button.grid(row=4, column=2, padx=(50, 0))

        self.current_date = Label(self.frame2, text='', bg=self.BG, fg='gray', font=('Georgia', 15))
        self.current_date.grid(row=5, column=1, sticky='w')

        self.statement_label = Label(self.frame2, text='Statement', bg=self.BG, fg='white',
                                     font=('Georgia', 20, 'bold'))
        self.statement_label.grid(row=6, column=1, pady=(15, 5), sticky='w')

        self.set_statement_button = Button(self.frame2, image=self.click_to_set_statement, activebackground=self.BG,
                                           bg=self.BG, borderwidth=0, command=self.set_statement_window)
        self.set_statement_button.grid(row=6, column=2, padx=(30, 0))

        self.statement_text = Label(self.frame2, text='', bg=self.BG, fg='gray', font=('Georgia', 15))
        self.statement_text.grid(row=7, column=1, sticky='w')

        self.amount_label = Label(self.frame2, text='Amount', bg=self.BG, fg='white', font=('Georgia', 20, 'bold'))
        self.amount_label.grid(row=8, column=1, sticky='w', pady=(15, 5))

        self.frame3 = Frame(self, bg=self.BG)
        self.frame3.grid(row=3, column=1, sticky='w')

        self.currency_label = Label(self.frame3, text='N', bg=self.BG, fg='white', font=('Georgia', 13))
        self.currency_label.grid(row=1, column=1, sticky='w')

        self.amount_entry = Entry(self.frame3, width=15, bg='#1F213A', fg='white')
        self.amount_entry.configure(insertbackground='white', font=('Georgia', 13))
        self.amount_entry.grid(row=1, column=2, sticky='w')

        self.frame4 = Frame(self, bg=self.BG)
        self.frame4.grid(row=4, column=1, sticky='w')

        self.description_label = Label(self.frame4, bg=self.BG, fg='white', font=('Georgia', 20, 'bold'),
                                       text='Description (0/350 characters)')
        self.description_label.grid(row=1, column=1, sticky='w', pady=(10, 0))

        self.description_text = Text(self.frame4, width=50, fg="white", height="4", borderwidth="2", relief="ridge",
                                     font=('Georgia', 16), bg='#1F213A', insertbackground='white')
        self.description_text.grid(row=2, column=1, padx=(5, 0))
        self.description_text.bind("<KeyRelease>", self.on_entry_click)

        self.frame5 = Frame(self, bg=self.BG)
        self.frame5.grid(row=5, column=1, pady=(20, 30))

        self.add_new_invoice_button = Button(self.frame5, image=self.add_new_invoice_image, activebackground=self.BG,
                                             bg=self.BG, borderwidth=0, command=self.add_new_invoice)
        self.add_new_invoice_button.grid(row=3, column=1, sticky='w')

        self.home_page_button = Button(self.frame5, image=self.home_page_image, bg=self.BG, activebackground=self.BG,
                                       borderwidth=0, command=lambda: controller.set_screen('DataPage'))
        self.home_page_button.grid(row=3, column=2, padx=(20, 0))

    def set_name(self):
        global users_name

        self.the_users_name = users_name
        # Uncomment the above line in the full project
        self.the_name.config(text=f"{self.the_users_name}")

    def grab_date(self, date):
        the_gotten_date = str(date)

        the_gotten_date = the_gotten_date.split('-')

        months = {
            '01': 'Jan',
            '02': 'Feb',
            '03': 'Mar',
            '04': 'Apr',
            '05': 'May',
            '06': 'Jun',
            '07': 'Jul',
            '08': 'Aug',
            '09': 'Sep',
            '10': 'Oct',
            '11': 'Nov',
            '12': 'Dec'
        }

        self.current_date.config(text=f'{the_gotten_date[2]} {months[the_gotten_date[1]]}, {the_gotten_date[0]}')
        self.the_date = f"{the_gotten_date[2]} {months[the_gotten_date[1]]}, {the_gotten_date[0]}"

        self.calendar_window.destroy()

    def set_date(self):
        self.calendar_window = Toplevel()
        self.calendar_window.config(bg=self.BG)
        self.calendar_window.geometry('300x280')
        self.calendar_window.title('Set Date')

        day = datetime.datetime.today().day
        month = datetime.datetime.today().month
        year = datetime.datetime.today().year

        cal = Calendar(self.calendar_window, selectmode='day', year=year, month=month, day=day)
        cal.pack(pady=30)

        set_date_button = Button(self.calendar_window, text='Set Date',
                                 command=lambda: self.grab_date(cal.selection_get()))
        set_date_button.pack()

    def set_statement_window(self):
        self.statement_window = Toplevel()
        self.statement_window.config(bg=self.BG)
        self.statement_window.geometry('400x400')
        self.statement_window.title('Set Statement')

        set_statement_text = Label(self.statement_window, bg=self.BG, text='Select Statement',
                                   font=('Georgia', 20, 'bold'), fg='white')
        set_statement_text.grid(row=1, column=1, padx=(60, 0))

        var = IntVar()

        for i in range(1, len(self.statement_list)+1, 1):
            r1 = Radiobutton(self.statement_window, text=f'{self.statement_list[i-1]}', bg=self.BG,
                             font=('Georgia', 15), variable=var, value=i, fg='gray', activebackground=self.BG)
            r1.grid(row=i+1, column=1, sticky='w', padx=(20, 0))

        set_statement_button = Button(self.statement_window, text='Set Statement',
                                      command=lambda: self.set_statement(var.get()))
        set_statement_button.grid(row=10, column=1, padx=(60, 0))

    def set_statement(self, value):
        self.statement_text.config(text=f'{self.statement_list[value-1]}')
        self.the_gotten_statement = self.statement_list[value-1]
        self.statement_window.destroy()

    def on_entry_click(self, event):
        value = self.description_text.get("0.0", 'end')
        length = len(value[:-1])
        changed = True if self.prevlaue != value else False
        if length < 351:
            self.description_label.config(text=f"Description ({length}/350 characters)")
        else:
            self.description_label.config(text=f"Description ({length}/350 characters) LIMIT REACHED!")
        self.prevlaue = value

    def add_new_invoice(self):

        name = self.the_users_name
        date = self.the_date
        statement = self.the_gotten_statement
        amount = self.amount_entry.get()
        striped_amount = amount.replace(',', '')
        description = self.description_text.get('0.0', '350.0')

        if len(name) > 0 and len(date) > 0 and len(statement) > 0 and len(amount) > 0 and len(description) > 0:
            if '.' in amount:
                messagebox.showinfo('Amount Error', "Decimal points are not important for now...")
            elif len(description) > 350:
                messagebox.showinfo('Description Error', 'The description is more than 350 characters!')
            elif not striped_amount.isdigit():
                messagebox.showinfo('Amount Error', 'Please add only numbers and/or comma and nothing else in the'
                                                    ' amount entry')
            else:
                refined_description = self.beautify(description)
                refined_amount = 'N' + "{:,}".format(int(striped_amount))
                new_invoice = Invoice(name=name, date=date, description=refined_description, statement=statement,
                                      amount=refined_amount)
                db.session.add(new_invoice)
                db.session.commit()
                messagebox.showinfo('New Invoice Added', 'Successfully added a new invoice')

        else:
            messagebox.showinfo('Missing Data', 'You forgot to add something')

    def beautify(self, text):
        rtn = re.split('([.!?] *)', text)
        final = ''.join([i.capitalize() for i in rtn])
        return final


class LoginPage(Frame):
    def __init__(self, parent, controller):

        # All that is left here is to set the buttons to images

        Frame.__init__(self, parent)
        self.controller = controller
        controller.wm_title('Login')
        Frame.config(self, bg='#141625')
        Frame.config(self, padx=5, pady=20)

        self.BG = '#141625'
        self.show_password_state = False

        self.login_button_image = PhotoImage(file='images/login.png')
        self.forgot_password_button_image = PhotoImage(file='images/forgot password.png')
        self.click_here_to_register_button_image = PhotoImage(file='images/click here to register.png')

        self.frame1 = Frame(self, bg=self.BG)
        self.frame1.grid(row=1, column=1, pady=(20, 50), padx=(100, 0))

        self.login_label = Label(self.frame1, text='Login', font=('Georgia', 30, 'bold'), bg=self.BG, fg='white')
        self.login_label.grid(row=1, column=1)

        self.frame2 = Frame(self, bg=self.BG)
        self.frame2.grid(row=2, column=1, padx=(100, 0))

        self.email_label = Label(self.frame2, text='Email', font=('Georgia', 15), bg=self.BG, fg='white')
        self.email_label.grid(row=1, column=1, sticky='w')

        self.email_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.email_entry.configure(insertbackground='white', font=('Georgia', 13))
        self.email_entry.grid(row=2, column=1, pady=(0, 40), ipady=3)

        self.password_label = Label(self.frame2, text='Password', font=('Georgia', 15), bg=self.BG, fg='white')
        self.password_label.grid(row=3, column=1, sticky='w')

        self.password_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.password_entry.configure(insertbackground='white', font=('Georgia', 13), show="*")
        self.password_entry.grid(row=4, column=1, ipady=3)

        self.var1 = IntVar()

        self.show_password = Checkbutton(self.frame2, text='Show Password', variable=self.var1, onvalue=1, offvalue=0,
                                         command=self.show_or_hide_password, bg=self.BG, activebackground=self.BG,
                                         fg='gray', font=('Georgia', 12))
        self.show_password.grid(row=5, column=1, sticky='w', pady=(0, 30))

        self.login_button = Button(self.frame2, image=self.login_button_image, command=self.login,
                                   activebackground=self.BG, borderwidth=0, bg=self.BG)
        self.login_button.grid(row=6, column=1, pady=(0, 20))

        self.forgot_password_button = Button(self.frame2, image=self.forgot_password_button_image,
                                             activebackground=self.BG, bg=self.BG, borderwidth=0,
                                             command=lambda: self.controller.set_screen('ForgotPasswordPage'))
        self.forgot_password_button.grid(row=7, column=1, pady=(0, 20))

        self.register_button = Button(self.frame2, image=self.click_here_to_register_button_image, bg=self.BG,
                                      command=lambda: self.controller.set_screen('RegisterPage'), borderwidth=0,
                                      activebackground=self.BG)
        self.register_button.grid(row=8, column=1)

    def show_or_hide_password(self):
        if self.var1.get() == 0:
            self.password_entry.configure(show="*")
        else:
            self.password_entry.configure(show="")

    def login(self):
        global users_name
        if len(self.email_entry.get()) == 0 or len(self.password_entry.get()) == 0:
            messagebox.showinfo('Field Error', 'You cannot leave a field emtpy!')

        else:
            user = InvoiceUsers.query.filter_by(email=self.email_entry.get()).first()

            if user and user.password == self.password_entry.get():
                messagebox.showinfo('Success', 'Login successful')

                users_name = user.name
                self.controller.set_screen('DataPage')
            else:
                messagebox.showinfo('Error', 'Incorrect email or password!')


class RegisterPage(Frame):

    # Perhaps you should make an admin password or something here, so that only the admin can register people
    # This is to prevent anyone from registering just to be able to view the invoice

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        Frame.config(self, bg='#141625')

        self.register_button_image = PhotoImage(file='images/register.png')
        self.back_to_login_button_image = PhotoImage(file='images/back to login.png')

        self.BG = '#141625'
        self.show_password_state = False

        self.frame1 = Frame(self, bg=self.BG)
        self.frame1.grid(row=1, column=1, pady=(20, 50), padx=(100, 0))

        self.register_label = Label(self.frame1, text='Register', font=('Georgia', 30, 'bold'), bg=self.BG, fg='white')
        self.register_label.grid(row=1, column=1)

        self.frame2 = Frame(self, bg=self.BG)
        self.frame2.grid(row=2, column=1, padx=(100, 0))

        self.name_label = Label(self.frame2, text='Name (max 25 characters)', font=('Georgia', 15),
                                bg=self.BG, fg='white')
        self.name_label.grid(row=1, column=1, sticky='w')

        self.name_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.name_entry.configure(insertbackground='white', font=('Georgia', 13))
        self.name_entry.grid(row=2, column=1, pady=(0, 40), ipady=3)

        self.email_label = Label(self.frame2, text='Email', font=('Georgia', 15), bg=self.BG, fg='white')
        self.email_label.grid(row=3, column=1, sticky='w')

        self.email_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.email_entry.configure(insertbackground='white', font=('Georgia', 13))
        self.email_entry.grid(row=4, column=1, pady=(0, 40), ipady=3)

        self.password_label = Label(self.frame2, text='Password', font=('Georgia', 15), bg=self.BG, fg='white')
        self.password_label.grid(row=5, column=1, sticky='w')

        self.password_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.password_entry.configure(insertbackground='white', font=('Georgia', 13), show="*")
        self.password_entry.grid(row=6, column=1, ipady=3)

        self.var1 = IntVar()

        self.show_password = Checkbutton(self.frame2, text='Show Password', variable=self.var1, onvalue=1, offvalue=0,
                                         command=self.show_or_hide_password, bg=self.BG, activebackground=self.BG,
                                         fg='gray', font=('Georgia', 12))
        self.show_password.grid(row=7, column=1, sticky='w', pady=(0, 30))

        self.register_button = Button(self.frame2, image=self.register_button_image, command=self.register, bg=self.BG,
                                      activebackground=self.BG, borderwidth=0)
        self.register_button.grid(row=8, column=1, pady=(0, 20))

        self.login_button = Button(self.frame2, image=self.back_to_login_button_image, bg=self.BG, borderwidth=0,
                                   activebackground=self.BG, command=lambda: self.controller.set_screen('LoginPage'))
        self.login_button.grid(row=9, column=1, pady=(0, 20))

    def show_or_hide_password(self):
        if self.var1.get() == 0:
            self.password_entry.configure(show="*")
        else:
            self.password_entry.configure(show="")

    def register(self):
        if len(self.email_entry.get()) == 0 or len(self.password_entry.get()) == 0 or len(self.name_entry.get()) == 0:
            messagebox.showinfo('Field Error', 'You cannot leave a field emtpy!')

        else:
            user = InvoiceUsers.query.filter_by(email=self.email_entry.get().lower()).first()
            name = InvoiceUsers.query.filter_by(name=self.name_entry.get().lower()).first()

            if user:
                messagebox.showinfo('Email Error', 'Sorry! That email already exists')

            elif name:
                # This is a company invoice therefore, it should be that there should only be 1 name per person
                # that should be listed in the invoice

                # Even though multiple people can have the same name, it would make sense if the second person with the
                # same name is more easily identified in order not to cause confusion.

                # Perhaps you could add a number to your name for better Identification
                messagebox.showinfo('Name Error', 'Sorry! That Name already exists')

            else:
                if len(self.name_entry.get()) > 25:
                    messagebox.showinfo('Limit Error', 'Your name should not be greater than 25 characters!')

                else:

                    new_user = InvoiceUsers(name=self.name_entry.get().lower(), email=self.email_entry.get().lower(),
                                            password=self.password_entry.get())
                    db.session.add(new_user)
                    db.session.commit()
                    messagebox.showinfo('Success', 'Registration successful!')

                    self.controller.set_screen('LoginPage')


class ForgotPasswordPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        Frame.config(self, bg='#141625')

        self.BG = '#141625'

        self.change_password_button_image = PhotoImage(file='images/change password.png')
        self.back_to_login_button_image = PhotoImage(file='images/back to login.png')

        self.frame1 = Frame(self, bg=self.BG)
        self.frame1.grid(row=1, column=1, pady=(20, 50), padx=(100, 0))

        self.register_label = Label(self.frame1, text='Reset Password', font=('Georgia', 30, 'bold'), bg=self.BG,
                                    fg='white')
        self.register_label.grid(row=1, column=1)

        self.frame2 = Frame(self, bg=self.BG)
        self.frame2.grid(row=2, column=1, padx=(100, 0))

        self.email_label = Label(self.frame2, text='Email', font=('Georgia', 15), bg=self.BG, fg='white')
        self.email_label.grid(row=1, column=1, sticky='w')

        self.email_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.email_entry.configure(insertbackground='white', font=('Georgia', 13))
        self.email_entry.grid(row=2, column=1, pady=(0, 40), ipady=3)

        self.password_label = Label(self.frame2, text='New Password', font=('Georgia', 15), bg=self.BG, fg='white')
        self.password_label.grid(row=3, column=1, sticky='w')

        self.password_entry = Entry(self.frame2, width=30, bg='#1F213A', fg='white')
        self.password_entry.configure(insertbackground='white', font=('Georgia', 13), show="*")
        self.password_entry.grid(row=4, column=1, ipady=3)

        self.var1 = IntVar()

        self.show_password = Checkbutton(self.frame2, text='Show Password', variable=self.var1, onvalue=1, offvalue=0,
                                         command=self.show_or_hide_password, bg=self.BG, activebackground=self.BG,
                                         fg='gray', font=('Georgia', 12))
        self.show_password.grid(row=5, column=1, sticky='w', pady=(0, 30))

        self.change_password_button = Button(self.frame2, image=self.change_password_button_image, bg=self.BG,
                                             command=self.change_password, activebackground=self.BG, borderwidth=0)
        self.change_password_button.grid(row=6, column=1, pady=(0, 20))

        self.login_button = Button(self.frame2, image=self.back_to_login_button_image, activebackground=self.BG,
                                   bg=self.BG, borderwidth=0, command=lambda: self.controller.set_screen('LoginPage'))
        self.login_button.grid(row=7, column=1, pady=(0, 20))

    def show_or_hide_password(self):
        if self.var1.get() == 0:
            self.password_entry.configure(show="*")
        else:
            self.password_entry.configure(show="")

    def change_password(self):

        # Obviously, in a real life scenario, the security here is very poor. Perhaps you should send an otp to the
        # email, or alert the person of a password change

        if len(self.email_entry.get()) == 0 or len(self.password_entry.get()) == 0:
            messagebox.showinfo('Empty Field', 'You cannot leave a field emtpy!')
        else:
            user = InvoiceUsers.query.filter_by(email=self.email_entry.get().lower()).first()
            if user:
                user.password = self.password_entry.get()
                db.session.commit()
                messagebox.showinfo('Password Reset', 'Your password has been reset successfully!')
            else:
                messagebox.showinfo('Email Error', 'Sorry. No such email exists!')


app = InvoiceApp()
app.mainloop()
