import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import dateutil.parser as dparser
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
color = ['brown']
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 8}

matplotlib.rc('font', **font)

def Reverse(lst):
    return [ele for ele in reversed(lst)]


def month_diff(a, b):
    return ((a - b) / np.timedelta64(1, 'M'))

def modifyPatientData(patientNo):
    for index, patientID in enumerate(patientNo):
        patientNo[index] = patientID[patientID.find("(PTR)")-7:patientID.find("(PTR)")-4]
        #print(patientID[patientID.find("(PTR)")-3:patientID.find("(PTR)")])
    return patientNo


def plotPatientData(data, patientNo, totalDate):
    plt.axvline(x=6.67, color = 'grey', linestyle = '--', label='PFS')
    plt.text(6.4, -3.25, 'PFS' ,fontweight = 'normal')
    bar_list = plt.barh(Reverse(patientNo), Reverse(totalDate), color=color, align='center', height=.4, linewidth = 0)
    #P.arrow( x, y, dx, dy, **kwargs )
    ax = plt.gca();

    for index, list_data in reversed(list(enumerate(data))):
        if list_data[3] == 0:
            arr = plt.arrow(list_data[8], len(data)-index-1, .5, 0, fc="k", ec="k",head_width=.5, head_length=.25)
            ax.add_patch(arr)
            bar_list[len(data)-index-1].set_color('g')
    for index, list_data in reversed(list(enumerate(data))):
        if ('PR' in list_data[4]):
            #print("Found it!!: ", list_data[4], month_diff(list_data[5],list_data[1]))
            plt.plot(month_diff(list_data[5],list_data[1]), len(data)-index-1, 'bD', markersize = 4)
        if ('CR' in list_data[4]):
            plt.plot(month_diff(list_data[5], list_data[1]), len(data) - index - 1, '*', color = 'darkorange', markersize=7)
        #print("List_data[6]: ", list_data[6])
        if (pd.notnull(list_data[6]) and ('withdrew' in list_data[6] or 'AE' in list_data[6])):
            bar_list[len(data) - index - 1].set_color('m')
            #plt.plot(list_data[8], len(data) - index - 1, 'ko')
    #plt.plot(5,5,'bo')

    blue_diamond = mlines.Line2D([], [], color='blue', marker='D', linestyle='None',
                              markersize=4, label='Partial response')
    yellow_star = mlines.Line2D([], [], color='darkorange', marker='*', linestyle='None',
                              markersize=5, label='Complete response')
    green_patch = mlines.Line2D([], [], color='green', marker='s', linestyle='None',
                              markersize=5, label='Continues on study')
    brown_patch = mlines.Line2D([], [], color='brown', marker='s', linestyle='None',
                              markersize=5, label='Progression Disease')
    magenta_patch = mlines.Line2D([], [], color='m', marker='s', linestyle='None',
                              markersize=5, label='Censored/AE')
    plt.legend(handles=[green_patch,brown_patch,magenta_patch,yellow_star, blue_diamond], labelspacing = 1.5)
    plt.xlabel("Months")

    plt.savefig('myplot2.png', dpi=4500)
    plt.show()


def dataImport(filename):
    # Data is of the form:
    # [patientId, enrollment date, end date, status, response, response_date, type, note, total months in trial]
    # response date is also calculated here
    # enrollment date, end date must both be in date form already,
    # if need be, add the dparser.parse with the to_datetime
    #
    data_temp = pd.read_excel(filename)
    patient_id_temp = data_temp['Patient No'].tolist()
    end_date_temp = data_temp['Last Scan'].tolist()
    end_date_temp = pd.to_datetime(end_date_temp)
    enrollment_date_temp = data_temp['Enrollment Date'].tolist()
    enrollment_date_temp = pd.to_datetime(enrollment_date_temp)
    response_temp = data_temp['Best Response'].tolist()
    response_date_temp = list(response_temp)
    type_patient = data_temp['Type']
    note_patient = data_temp['Note']
    for index, list_data in enumerate(list(response_date_temp)):
        try:
            response_date_temp[index] = dparser.parse(list_data, fuzzy=True)
        except:
            response_date_temp[index] = pd.NaT
    response_date_temp = pd.to_datetime(response_date_temp, errors='coerce')
    status = data_temp['Status'].tolist()
    data_temp = list(map(list, zip(patient_id_temp, enrollment_date_temp, end_date_temp, status,
                                   response_temp, response_date_temp, type_patient, note_patient)))
    return data_temp, patient_id_temp, end_date_temp, enrollment_date_temp, \
           response_temp, status, response_date_temp, type_patient

def dataCalculate(data):
    for index, list_data in enumerate(list(data)):
        if pd.isnull(list_data[0]):
            data.remove(list_data)
        else:
            list_data.append(month_diff(list_data[2], list_data[1]))
    return data


def extractData(data, index):
    data_requested = []
    for list_data in data:
        data_requested.append(list_data[index])
    return data_requested

def plotSwimmerPlot(filedirectory):
    data, patientNo, endDate, enrollmentDate, response, status, response_date, type_patient = \
        dataImport(filedirectory)
    data = dataCalculate(data);
    output = sorted(data, key=lambda x: x[8], reverse=True)
    patientNo = extractData(output, 0)
    patientNo = modifyPatientData(patientNo)
    # add notes to patient ID
    print(patientNo)
    print(data)
    for index, patient in enumerate(patientNo):
        if(pd.notnull(output[index][7])):
            patientNo[index] = patient + '(' + output[index][7] + ')'
        else:
            patientNo[index] = patient + '(PAC)'
    totalDate = extractData(output, 8)
    print(totalDate)
    data = output
    plotPatientData(data, patientNo, totalDate)


plotSwimmerPlot()
