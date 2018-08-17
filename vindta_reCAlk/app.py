
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_uploads import UploadSet, configure_uploads
from core import dbs_to_excel, recalculate_CO2_from_excel
import inspect
import os

UPLOAD_FOLDER = 'temp_data/'
VINDTAFILES = ['dat', 'dbs']

app = Flask(__name__, template_folder='.')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# Configure the image uploading via Flask-Uploads
vindta = UploadSet('dat', VINDTAFILES, default_dest=lambda s: UPLOAD_FOLDER)
configure_uploads(app, vindta)


@app.route('/', methods=['GET', 'POST'])
def home_page():

    if request.method == 'GET':
        kwargs = reset_page()

    elif request.method == 'POST':
        if 'reset' in request.form:
            kwargs = reset_page()
        elif "create_excel" in request.form:
            kwargs = create_excel()
        elif 'recalculate':
            print('here')
            kwargs = recalculate()

    return render_template('index.html', **kwargs)


def reset_page():
    number_boxes, dropdown, header = get_rcParams()

    flash('Enter directory names and change the paths accordingly', category='primary')

    return dict(number_defaults=number_boxes,
                dropdowns=dropdown,
                filenames={},
                header=header)


def create_excel():
    import sys
    import io

    filenames, header, dropdowns, numbers, defaults = get_user_defaults()

    kwargs = dict(
        filenames=filenames,
        header=header,
        number_defaults=numbers,
        dropdowns=dropdowns)

    if check_file_paths(filenames):
        try:
            # redirect sys.stdout to a buffer
            stdout = sys.stdout
            sys.stdout = io.StringIO()

            dbs_to_excel(
                filenames['dbs_file'],
                filenames['dat_file'],
                filenames['xls_file'],
                verbose=True,
                **defaults)
            message = "Excel file created: {}".format(filenames['xls_file'])
            flash(message, category='primary')

            # get output and restore sys.stdout
            output = sys.stdout.getvalue().strip()
            sys.stdout = stdout

            kwargs.update({"stdout": output.splitlines()})
        except Exception as e:
            if "header is missing" in str(e):
                # compulsory columns are not present
                flash("COLUMN HEADER ERROR: " + str(e), category='warning')
            elif "columns passed, passed data" in str(e):
                # Number of columns in header do not match the file
                flash("COLUMN HEADER ERROR: " + str(e), category='warning')
            elif "does not match format" in str(e):
                # incorrect date format
                flash('DATE FORMAT ERROR: ' + str(e), category='warning')
            else:
                raise(e)

    return kwargs


def recalculate():
    import sys
    import io

    filenames, header, dropdowns, numbers, defaults = get_user_defaults()
    kwargs = dict(
        filenames=filenames,
        dropdowns=dropdowns,
        header=header,
        number_defaults=numbers)

    xls = filenames['xls_file']
    if os.path.isfile(xls):
        # redirect sys.stdout to a buffer
        stdout = sys.stdout
        sys.stdout = io.StringIO()

        recalculate_CO2_from_excel(xls)
        flash("Data recalculated from " + xls, category="primary")

        # get output and restore sys.stdout
        output = sys.stdout.getvalue().strip()
        sys.stdout = stdout

        kwargs.update({"stdout": output.splitlines()})
    else:
        flash("FILE PATH ERROR: The given Excel file name does not exist. "
              "You must create the Excel file", category="warning")

    return kwargs


def get_rcParams():
    from rcVINDTA import defaults as df
    from copy import deepcopy as copy

    defaults = copy(df)
    number_boxes = {}
    dropdown = {}

    for key in defaults:
        if type(defaults[key]) is float:
            number_boxes[key] = defaults[key]
        elif type(defaults[key]) is list:
            dropdown[key] = defaults[key]
        elif key is 'header':
            header = defaults[key]

    return number_boxes, dropdown, header


def get_user_defaults():
    form = dict(request.form)

    form.pop('create_excel', None)
    form.pop('pK_constant', None)
    form.pop('recalculate', None)

    filenames = {"dbs_file": form.pop('dbs_file')[0],
                 "dat_file": form.pop('dat_file')[0],
                 "xls_file": form.pop('xls_file')[0]}

    header = form.pop('header')[0].replace(',', '').splitlines()

    # make selection the first item of the dropdown lists
    dd = get_rcParams()[1]
    date_fmt_sel = form.pop('date_fmt')[0]
    pKchoice_sel = form.pop('pKchoice')[0]
    dd['date_fmt'].remove(date_fmt_sel)
    dd['pKchoice'].remove(pKchoice_sel)
    dropdowns = {'date_fmt': [date_fmt_sel] + dd['date_fmt'],
                 'pKchoice': [pKchoice_sel] + dd['pKchoice']}

    numbers = {key: form[key][0] for key in form}

    # combine various inputs into one
    defaults = {'header': header}
    defaults.update(numbers)
    defaults['date_fmt'] = correct_date_fmt(date_fmt_sel)
    defaults['pKchoice'] = get_pKchoice(pKchoice_sel)

    return filenames, header, dropdowns, numbers, defaults


def get_pKchoice(pKchoice_string):

    opts = {
        "Roy et al, 1993": 1,
        "Goyet and Poisson, 1989": 2,
        "Hansson refit by Dickson and Millero, 1987": 3,
        "Mehrbach refit by Dickson and Millero, 1987": 4,
        "Hansson and Mehrbach refit BY Dickson & Millero, 1987": 5,
        "Mehrbach et al, 1973": 6,
        "Millero, 1979": 7,
        "Cai and Wang, 1998": 8,
        "Lueker et al, 2000": 9,
        "Mojica Prieto and Millero, 2002": 10,
        "Millero et al, 2002": 11,
        "Millero, 2006": 12,
        "Millero, 2010": 13,
    }

    return opts[pKchoice_string]


def correct_date_fmt(date_fmt_str):

    repl = [
        ['dd', '%d'],
        ['mm', '%m'],
        ['yyyy', '%Y'],
        ['yy', '%y'],
        ['HH', '%H'],
        ['MM', '%M']
    ]

    for a, b in repl:
        date_fmt_str = date_fmt_str.replace(a, b)

    return date_fmt_str


def check_file_paths(filename_dict):
    """
    Returns a bool - True is all files are good.
    Otherwise flashes message and returns False
    """

    if not all(filename_dict.values()):
        flash('FILE PATH ERROR: There are empty filenames', category='warning')
        return False

    dbs = filename_dict['dbs_file']
    dat = filename_dict['dat_file']
    xls = filename_dict['xls_file']

    all_files_good = True

    message = []
    if not (os.path.isfile(dbs) & dbs.endswith('dbs')):
        all_files_good = False
        message += 'DBS path invalid',

    if not os.path.isdir(dat):
        all_files_good = False
        message += 'DAT path invalid',
    else:
        dat_list = os.listdir(dat)
        has_datfiles = any([f.endswith('.dat') for f in dat_list])
        if not has_datfiles:
            all_files_good = False
            message += 'DAT path does not contain .dat files',

    if (not (xls.endswith('.xlsx') | xls.endswith('.xls'))):
        all_files_good = False
        message += 'Excel file path must end with .xls or .xlsx',
    elif not os.path.isdir(os.path.split(xls)[0]):
        all_files_good = False
        message += 'Excel root path does not exist.',

    if not all_files_good:
        flash('FILE PATH ERROR: {}'.format(', '.join(message)), category='warning')

    return all_files_good


if __name__ == "__main__":
    app.run(debug=True, passthrough_errors=True)
