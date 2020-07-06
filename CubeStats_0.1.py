from tkinter import *
import tkinter.filedialog as fdialog
from tkinter import messagebox
import csv
from datetime import datetime
import os
import sys
from math import floor
from math import ceil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from copy import deepcopy

window = Tk()

ver_num = "0.1"

window.title("Cube Stats v" + ver_num)

if getattr(sys, 'frozen', False):
    app_path = sys._MEIPASS
elif __file__:
    app_path = os.path.dirname(__file__)

icon_file = 'rubik.ico'

window.iconbitmap(default=os.path.join(app_path,icon_file))

class internal_data:
    def __init__(self):
        self.data = []

    def update(upd,new_data):
        upd.data += new_data
        upd.data.sort(key = get_first)

        upd.data_no_dupl = list()
        upd.prev_time = ''
        upd.dupl_cnt = 0
        for entry in upd.data:
            if entry[0] != upd.prev_time:
                upd.data_no_dupl.append(entry)
            else:
                upd.dupl_cnt += 1
            upd.prev_time = entry[0]

        upd.data = upd.data_no_dupl

        lbl_stat['text'] = "Total: "+str(len(upd.data))+" solves (removed "+str(upd.dupl_cnt)+" duplicates)"

        upd.dates = column(upd.data, 0)
        upd.times = column(upd.data, 1)
        upd.times = [np.nan if x=='DNF' else x for x in upd.times]        
        upd.pb_sng = min(upd.times)
        upd.min_idx = upd.times.index(upd.pb_sng)
        upd.pb_date = upd.dates[upd.min_idx]

        lbl_stat2['text'] = "PB: "+str(upd.pb_sng)+"s ("+upd.pb_date+")"

    def reset(rst):
        rst.data = []
        lbl_stat['text'] = "Total: 0 solves"
        lbl_stat2['text'] = " "
        
all_data = internal_data()

def cmd_exit():
    window.destroy()

def cmd_reset():
    reset_chkboxes()
    lbl_importres['text'] = ""
    all_data.reset()
    
def cmd_importcs():
    cstimer_filename = fdialog.askopenfilename(filetypes = (("CSV files", "*.csv"),
                                                            ("All files", "*.*")))

    cstimer_data = ''
    if cstimer_filename != '':
        cstimer_data = read_csv_file(cstimer_filename, ';')
    else:
        lbl_importres['text'] = "No file selected"

    if cstimer_data != '':
        cstimer_parsed_data = cstimer_parser(cstimer_data)
        if cstimer_parsed_data == "error":
            cstimer_parsed_data = list()
            lbl_importres['text'] = "Invalid data"
            return
        else:
            lbl_importres['text'] = "Imported " + str(len(cstimer_parsed_data)) + " solves"
    else:
        cstimer_parsed_data = list()
        lbl_importres['text'] = "Invalid data"
        return

    all_data.update(cstimer_parsed_data)

def cmd_importnano():
    nanotimer_filename = fdialog.askopenfilename(filetypes = (("CSV files", "*.csv"),
                                                    ("All files", "*.*")))

    nanotimer_data = ''
    if nanotimer_filename != '':
        nanotimer_data = read_csv_file(nanotimer_filename, ',')
    else:
        lbl_importres['text'] = "No file selected"

    if nanotimer_data != '':
        nanotimer_parsed_data = nanotimer_parser(nanotimer_data)
        if nanotimer_parsed_data == "error":
            nanotimer_parsed_data = list()
            lbl_importres['text'] = "Invalid data"
            return
        else:
            lbl_importres['text'] = "Imported " + str(len(nanotimer_parsed_data)) + " solves"
    else:
        nanotimer_parsed_data = list()
        lbl_importres['text'] = "Invalid data"
        return

    all_data.update(nanotimer_parsed_data)

def cmd_importtwisty():
    twistytimer_filename = fdialog.askopenfilename(filetypes = (("TXT files", "*.txt"),
                                                                ("All files", "*.*")))

    twistytimer_data = ''
    if twistytimer_filename != '':
        twistytimer_data = read_csv_file(twistytimer_filename, ';')
    else:
        lbl_importres['text'] = "No file selected"

    if twistytimer_data != '':
        twistytimer_parsed_data = twistytimer_parser(twistytimer_data)
        if twistytimer_parsed_data == "error":
            twistytimer_parsed_data = list()
            lbl_importres['text'] = "Invalid data"
            return
        else:
            lbl_importres['text'] = "Imported " + str(len(twistytimer_parsed_data)) + " solves"
    else:
        twistytimer_parsed_data = list()
        lbl_importres['text'] = "Invalid data"
        return
    
    all_data.update(twistytimer_parsed_data)

def cstimer_parser(data):    
    entry_list = data

    if entry_list[0] != ['No.','Time','Comment','Scramble','Date','P.1']:
        messagebox.showerror("Error", "Invalid csTimer session file!\nFirst row: "+str(entry_list[0]))
        return("error")
    
    del entry_list[0]

    parsed_entry_list = list()

    for entry in entry_list:
        time = entry[1]
        if time[-1] == '+':
            time = time[0:-1]        
        if time[0:3] != 'DNF':
            time = time.split(':')
            if len(time) > 1:
                time = 60*int(time[0]) + float(time[1])
            else:
                time = float(time[0])
            time = round(time, 2)
        else:
            time = 'DNF'

        scramble = entry[3]
        date = entry[4]

        parsed_entry_list.append([date, time, scramble])

    return(parsed_entry_list)

def nanotimer_parser(data):
    entry_list = data

    if entry_list[0] != ['cubetype','solvetype','time','date','steps','plustwo','blind','scrambleType','scramble','comment']:
        messagebox.showerror("Error", "Invalid Nano Timer session file!\nFirst row: "+str(entry_list[0]))
        return("error")
    
    del entry_list[0]
    
    index = 0
    parsed_entry_list = list()

    for entry in entry_list:
        if entry[0] == '3x3x3':
            time = entry[2]
            if time != 'DNF':
                time = time.split(':')
                if len(time) > 1:
                    time = 60*int(time[0]) + float(time[1])
                else:
                    time = float(time[0])
                if entry[5] == 'y':
                    time += 2
                time = round(time, 2)

            scramble = entry[8]
            date = entry[3]
            date_obj = datetime.strptime(date, "%b %d %Y - %H:%M:%S")
            date = date_obj.strftime("%Y-%m-%d %H:%M:%S") 

            parsed_entry_list.append([date, time, scramble])

            index += 1

    return(parsed_entry_list)

def twistytimer_parser(data):
    entry_list = data
    first_row = entry_list[0]
    
    if len(first_row) == 3 or (len(first_row) == 4 and first_row[3] == 'DNF'):
        valid = True
    else:
        messagebox.showerror("Error", "Invalid Twisty Timer session file!\nFirst row: "+str(entry_list[0]))
        return("error")

    index = 0
    parsed_entry_list = list()

    for entry in entry_list:
        time = entry[0]
        scramble = entry[1]
        date = entry[2]
        date = date[0:19]
        date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        if len(entry) > 3 and entry[3] == 'DNF':
            time = 'DNF'
        if time != 'DNF':
            time = time.split(':')
            if len(time) > 1:
                time = 60*int(time[0]) + float(time[1])
            else:
                time = float(time[0])
            time = round(time, 2)
        #print([date, time, scramble])
        parsed_entry_list.append([date, time, scramble])

    return(parsed_entry_list)
   
def get_first(x):
    return x[0]

def AoX(data, avg):
    index = 1
    times_list = list()
    data_aox = list()
    rmv = ceil(avg*0.05)
    
    for row in data:
        time = row[1]

        if time == 'DNF':
            time = 50000
        times_list.append(time)
        aox=''
        if index > (avg - 1):
            lastX = times_list[index-avg:index]
            dnf_count = lastX.count(50000)
            if dnf_count > rmv:
                aox = 'DNF'
            else:
                lastX.sort()
                aox = sum(lastX[rmv:avg-rmv])/(avg-2*rmv)
                aox = round(aox, 2)
        row.insert(2,aox)       
        data_aox.append(row)
        index += 1
        
    return(data_aox)

def add_avg(data):
    if ao2000_chk.get()==True:
        data = AoX(data, 2000)
    if ao1000_chk.get()==True:
        data = AoX(data, 1000)
    if ao500_chk.get()==True:
        data = AoX(data, 500)
    if ao200_chk.get()==True:
        data = AoX(data, 200)
    if ao100_chk.get()==True:
        data = AoX(data, 100)
    if ao50_chk.get()==True:
        data = AoX(data, 50)
    if ao25_chk.get()==True:
        data = AoX(data, 25)
    if ao12_chk.get()==True:
        data = AoX(data, 12)
    if ao5_chk.get()==True:
        data = AoX(data, 5)
    
    return(data)        

def read_csv_file(filename, delimiter):
    data = ''
    with open(filename, 'r') as file:
        data = list(csv.reader(file, delimiter = delimiter))
    return(data)

def cmd_exportstat():
    
    export_data = deepcopy(all_data.data)
    export_data = add_avg(export_data)

    header = ['Date', 'Time']
    if ao5_chk.get()==True:
        header.append('Ao5')
    if ao12_chk.get()==True:
        header.append('Ao12')
    if ao25_chk.get()==True:
        header.append('Ao25')
    if ao50_chk.get()==True:
        header.append('Ao50')
    if ao100_chk.get()==True:
        header.append('Ao100')
    if ao200_chk.get()==True:
        header.append('Ao200')
    if ao500_chk.get()==True:
        header.append('Ao500')
    if ao1000_chk.get()==True:
        header.append('Ao1000')
    if ao2000_chk.get()==True:
        header.append('Ao2000')

    header.append('Scramble')

    export_data.insert(0, header)

    export_filename = fdialog.asksaveasfilename(filetypes = (("CSV files", "*.csv"),
                                                             ("All files", "*.*")),
                                                defaultextension = '.csv')
    export_file = open(export_filename, "w", newline='')
    export_file_writer = csv.writer(export_file, delimiter=',')
    for row in export_data:
        export_file_writer.writerow(row)
    export_file.close()

    messagebox.showinfo("Success!", "Exported "+str(len(export_data)-1) + " solves to CSV file:\n"+export_filename)

def format_time(time):
    if time != 'DNF':
            time = float(time)
            
            if time >= 60:
                minutes = floor(time/60)
            else:
                minutes = 0
                
            seconds = time - minutes*60
            seconds = round(seconds, 2)        
            
            if seconds < 10:
                seconds = '0' + ('%.2f' % seconds)
            else:
                seconds = '%.2f' % seconds

            if minutes < 1:
                minutes = ''
            else:
                minutes = str(minutes) + ':'
            
            time = minutes + seconds
    return(time)

def cmd_exportcs():
    export_csdata = deepcopy(all_data.data)
    
    cs_data = list()

    index = 1
    
    for row in export_csdata:
        time = row[1]
        date = row[0]
        scramble = row[2]

        time = format_time(time)
            
        row_cs = [index, time, '', scramble, date, time]
        cs_data.append(row_cs)

        index += 1

    header = ['No.', 'Time', 'Comment', 'Scramble', 'Date', 'P.1']
    cs_data.insert(0, header)

    export_filename = fdialog.asksaveasfilename(filetypes = (("CSV files", "*.csv"),
                                                             ("All files", "*.*")),
                                                defaultextension = '.csv')
    export_file = open(export_filename, "w", newline='')
    export_file_writer = csv.writer(export_file, delimiter=';')
    for row in cs_data:
        export_file_writer.writerow(row)
    export_file.close()

    messagebox.showinfo("Success!", "Exported "+str(len(cs_data)-1) + " solves to csTimer CSV file:\n"+export_filename)

def cmd_exportnano():
    export_nanodata = deepcopy(all_data.data)
    export_nanodata.sort(key = get_first, reverse = True)

    nano_data = list()

    for row in export_nanodata:
        time = row[1]
        date = row[0]
        scramble = row[2]

        time = format_time(time)

        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date = date_obj.strftime("%b %d %Y - %H:%M:%S")
            
        row_nano = ['3x3x3', "Default", time, date, '', 'n', 'n', '', scramble, '']
        nano_data.append(row_nano)

    header = ['cubetype', 'solvetype', 'time', 'date', 'steps', 'plustwo', 'blind', 'scrambleType', 'scramble', 'comment']
    nano_data.insert(0, header)

    export_filename = fdialog.asksaveasfilename(filetypes = (("CSV files", "*.csv"),
                                                             ("All files", "*.*")),
                                                defaultextension = '.csv')
    export_file = open(export_filename, "w", newline='')
    export_file_writer = csv.writer(export_file, delimiter=',')
    for row in nano_data:
        export_file_writer.writerow(row)
    export_file.close()

    messagebox.showinfo("Success!", "Exported "+str(len(nano_data)-1) + " solves to Nano Timer CSV file:\n"+export_filename)

def cmd_exporttwisty():
    export_twistydata = deepcopy(all_data.data)

    twisty_data = list()

    for row in export_twistydata:
        time = row[1]
        date = row[0]
        scramble = row[2]

        time = format_time(time)

        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

        
        row_twisty = [time, scramble, date]
        if time == 'DNF':
            row_twisty[0] = "0.00"
            row_twisty.append("DNF")
        twisty_data.append(row_twisty)

    export_filename = fdialog.asksaveasfilename(filetypes = (("TXT files", "*.txt"),
                                                             ("All files", "*.*")),
                                                defaultextension = '.txt')
    export_file = open(export_filename, "w", newline='')
    export_file_writer = csv.writer(export_file, delimiter=';', quoting=csv.QUOTE_ALL)
    for row in twisty_data:
        export_file_writer.writerow(row)
    export_file.close()

    messagebox.showinfo("Success!", "Exported "+str(len(twisty_data)) + " solves to Twisty Timer TXT file:\n"+export_filename)
    
def pb_list(data):
    pb_lst = [0];
    pb_lst_cnt = 0;
    for x in range(1,len(data)):
        crt_pb_idx = int(pb_lst[pb_lst_cnt])
        if data[x] < data[crt_pb_idx]:
            pb_lst.append(x)
            pb_lst_cnt += 1
    return pb_lst

def column(array, col):
    return [row[col] for row in array]

def dnfgap(data):
    return [np.nan if x=='DNF' else x for x in data]

def ntgap(data):
    return [np.nan if x=='' else x for x in data]

def setgap(data):
    data = dnfgap(data)
    data = ntgap(data)
    return data

def display_graph():
    data = deepcopy(all_data.data)

    data = add_avg(data)
    
    data_x = column(data,0)

    index = 0
    for x in data_x:
        #data_x[index] = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        data_x[index] = x[0:10]
        index +=1

    avg_idx = 0
    
    data_ao = list()
    plot_ao = list()
    
    if ao5_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('5')
        avg_idx += 1        
    if ao12_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('12')
        avg_idx += 1       
    if ao25_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('25')
        avg_idx += 1
    if ao50_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('50')
        avg_idx += 1
    if ao100_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('100')
        avg_idx += 1
    if ao200_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('200')
        avg_idx += 1
    if ao500_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('500')
        avg_idx += 1
    if ao1000_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('1000')
        avg_idx += 1
    if ao2000_chk.get() == True:
        data_ao.append(column(data,avg_idx+2))
        plot_ao.append('2000')
        avg_idx += 1
    
    
    data_sng = column(data,1)
    data_sng = dnfgap(data_sng)
    
    for i in range(avg_idx):
        data_ao[i] = setgap(data_ao[i])
        
    pb_idx_lst = pb_list(data_sng)
    pb_lst = list()
    for x in pb_idx_lst:
        pb_lst.append(data_sng[x])

    fig, ax = plt.subplots()

    plt.xlabel('Date')
    plt.ylabel('Time')

    ax.plot(data_sng, label="Single")

    ax.plot(pb_idx_lst, pb_lst, color='orange', linestyle=':', marker="o", label="PB")

    for i in range(avg_idx):
        if len(data) >= int(plot_ao[i]):
            ax.plot(data_ao[i], label="Ao"+plot_ao[i])
    
    while len(data_x) > 30:
        data_x = data_x[::3]
    data_x = [''] + data_x + ['']
    
    ax.set_xticks(range(len(data_x)))
    ax.set_xticklabels(data_x, rotation=90)

    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.grid(which='major', axis='y')
    ax.grid(which='minor', axis='y', linestyle=':')

    plt.legend()

    ax.xaxis.set_major_locator(ticker.LinearLocator(len(data_x)))
        
    plt.show()

def reset_chkboxes():
    ao5_chk.set(True)
    ao12_chk.set(True)
    ao25_chk.set(False)
    ao50_chk.set(True)
    ao100_chk.set(True)
    ao200_chk.set(False)
    ao500_chk.set(False)
    ao1000_chk.set(False)
    ao2000_chk.set(False)

########################################################
# GUI
########################################################

lbl_title = Label(text="Cube Stats v"+ver_num)
lbl_title.grid(row=0, column=0, padx=5, pady=5, sticky='nsew', columnspan=2)

btn_width = 28

########################################################

frm_import = Frame(relief = GROOVE, borderwidth = 2)
frm_import.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
frm_import.columnconfigure(0, weight=1)

lbl_importses = Label(master=frm_import, text="Import timer sessions:")
lbl_importses.grid(padx=5, pady=5, sticky=N)

btn_importcs = Button(master=frm_import, text="Import csTimer session", command=cmd_importcs, width=btn_width)
btn_importcs.grid(padx=5, pady=5)

btn_importnano = Button(master=frm_import, text="Import Nano Timer session", command=cmd_importnano, width=btn_width)
btn_importnano.grid(padx=5, pady=5)

btn_importtwisty = Button(master=frm_import, text="Import Twisty Timer session", command=cmd_importtwisty, width=btn_width)
btn_importtwisty.grid(padx=5, pady=5)

for i in range(frm_import.grid_size()[1]):
    frm_import.rowconfigure(i, weight=1)

########################################################

frm_export = Frame(relief = GROOVE, borderwidth = 2)
frm_export.grid(row=1, column=1, padx = 5, pady = 5, sticky='nsew')
frm_export.columnconfigure(0, weight=1)

lbl_exportses = Label(master=frm_export, text="Export timer sessions:")
lbl_exportses.grid(padx=5, pady=5)

btn_exportcs = Button(master = frm_export, text = "Export csTimer CSV", command = cmd_exportcs, width=btn_width)
btn_exportcs.grid(padx=5, pady=5)

btn_exportnano = Button(master = frm_export, text = "Export Nano Timer CSV", command = cmd_exportnano, width=btn_width)
btn_exportnano.grid(padx=5, pady=5)

btn_exporttwisty = Button(master = frm_export, text = "Export Twisty Timer TXT", command = cmd_exporttwisty, width=btn_width)
btn_exporttwisty.grid(padx=5, pady=5)

for i in range(frm_export.grid_size()[1]):
    frm_export.rowconfigure(i, weight=1)

########################################################

frm_stat = Frame(relief = GROOVE, borderwidth = 2)
frm_stat.grid(row=2, column=0, padx = 5, pady = 5, sticky='nsew', columnspan=2)
frm_stat.columnconfigure(0, weight=1)
frm_stat.rowconfigure(0, weight=1)

lbl_importres = Label(master=frm_stat, text = " ")
lbl_importres.grid(padx=5, pady=5)

lbl_stat = Label(master=frm_stat, text="Total: 0 solves", font=('none', 15, 'bold'))
lbl_stat.grid(padx=5, pady=5)

lbl_stat2 = Label(master=frm_stat, text = " ")
lbl_stat2.grid(padx=5, pady=5)

########################################################

frm_exportstat = Frame(relief = GROOVE, borderwidth = 2)
frm_exportstat.grid(row=3, column=0, padx = 5, pady = 5, sticky='nsew', columnspan=2)
frm_exportstat.columnconfigure(0, weight=1)

btn_exportstat = Button(master = frm_exportstat, text = "Export CSV (incl. averages)", command = cmd_exportstat)
btn_exportstat.grid(padx=5, pady=5)

##############################

frm_avg = Frame(master = frm_exportstat, relief = GROOVE, borderwidth = 2)
frm_avg.grid(padx = 5, pady = 5, sticky='nsew')

lbl_inclavg = Label(master = frm_avg, text = "Include averages:")
lbl_inclavg.grid(row = 0, padx = 5, pady = 5, columnspan = 3)

ao5_chk = IntVar()
ao12_chk = IntVar()
ao25_chk = IntVar()
ao50_chk = IntVar()
ao100_chk = IntVar()
ao200_chk = IntVar()
ao500_chk = IntVar()
ao1000_chk = IntVar()
ao2000_chk = IntVar()

chk_avg5    = Checkbutton(master = frm_avg, text = "Ao5",    variable = ao5_chk   ).grid(row = 1, column = 0, sticky=W)
chk_avg12   = Checkbutton(master = frm_avg, text = "Ao12",   variable = ao12_chk  ).grid(row = 1, column = 1, sticky=W)
chk_avg25   = Checkbutton(master = frm_avg, text = "Ao25",   variable = ao25_chk  ).grid(row = 1, column = 2, sticky=W)
chk_avg50   = Checkbutton(master = frm_avg, text = "Ao50",   variable = ao50_chk  ).grid(row = 2, column = 0, sticky=W)
chk_avg100  = Checkbutton(master = frm_avg, text = "Ao100",  variable = ao100_chk ).grid(row = 2, column = 1, sticky=W)
chk_avg200  = Checkbutton(master = frm_avg, text = "Ao200",  variable = ao200_chk ).grid(row = 2, column = 2, sticky=W)
chk_avg500  = Checkbutton(master = frm_avg, text = "Ao500",  variable = ao500_chk ).grid(row = 3, column = 0, sticky=W)
chk_avg1000 = Checkbutton(master = frm_avg, text = "Ao1000", variable = ao1000_chk).grid(row = 3, column = 1, sticky=W)
chk_avg2000 = Checkbutton(master = frm_avg, text = "Ao2000", variable = ao2000_chk).grid(row = 3, column = 2, sticky=W)

reset_chkboxes()

for i in range(frm_avg.grid_size()[0]):
    frm_avg.columnconfigure(i, weight=1)

##############################
    
btn_graph = Button(master = frm_exportstat, text = "Show graph", command = display_graph).grid(padx=5, pady=5)

for i in range(frm_exportstat.grid_size()[1]):
    frm_exportstat.rowconfigure(i, weight=1)

########################################################

btn_reset = Button(text = "Reset", width = 10, command = cmd_reset)
btn_reset.grid(row=5, column=0, padx=20, pady=10, sticky=W)

btn_exit = Button(text = "Exit", width = 10, command = cmd_exit)
btn_exit.grid(row=5, column=1, padx=20, pady=10, sticky=E)

for i in range(window.grid_size()[1]):
    window.rowconfigure(i, weight=1)

for i in range(window.grid_size()[0]):
    window.columnconfigure(i, weight=1)

window.update()
window.minsize(window.winfo_width(), window.winfo_height())

window.mainloop()





