import datetime
import json

from flask import Blueprint, Response, abort, current_app as app, redirect, render_template, request, url_for
from flask_babel import gettext
from sqlalchemy import func, select

from app.models.db import get_db, t_led, t_report_definition
from app.models.utils import create_led_report_template, get_menu_items, json_default

led_bp = Blueprint('led', __name__, url_prefix='/led')


@led_bp.route('/data/')
def data():
    """Returns available leds from the database. Can be optionally filtered by year.

    This is called from templates/led/index.html when the year input is changed.
    """
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')
    year = request.args.get('year')
    if year:
        try:
            year = int(year)
        except (ValueError, TypeError):
            abort(400, 'invalid year parameter')
    else:
        year = None
    return json.dumps(get_leds(year), default=json_default)


@led_bp.route('/edit/')
@led_bp.route('/edit/<int:led_id>')
def edit(led_id=None):
    """Shows an edit form to add new or edit an existing led."""
    db_engine = get_db()
    rv = dict()
    rv['menu_items'] = get_menu_items('led')
    if led_id:
        with db_engine.begin() as connection:
            led = connection.execute(
                select(t_led)
                .where(t_led.c.id == led_id)
            ).fetchone()
        if not led:
            redirect(url_for('led.index'))
        rv['is_new'] = False
        rv['led'] = json.dumps(dict(
            id=led.id, state=led.state, date=led.date
        ))
    else:
        rv['is_new'] = True
        rv['led'] = json.dumps(dict(id='', state='', date=''))
    return render_template('led/edit.html', **rv)


@led_bp.route('/')
@led_bp.route('/index')
def index():
    """Shows a page where all available leds are listed."""
    rv = dict()
    rv['menu_items'] = get_menu_items('led')
    rv['leds'] = json.dumps(get_leds(), default=json_default)
    print(rv)
    return render_template('led/index.html', **rv)


@led_bp.route('/report/')
def report():
    """Prints a pdf file with all available leds.

    The leds can be optionally filtered by year. reportbro-lib is used to
    generate the pdf file. The data itself is retrieved
    from the database (*get_leds*). The report_definition
    is also stored in the database and is created on-the-fly if not present (to make
    this Demo App easier to use).
    """
    from reportbro import Report, ReportBroError

    print('request',request.args)
    year = request.args.get('year')
    if year:
        try:
            year = int(year)
        except (ValueError, TypeError):
            abort(400, 'invalid year parameter')
    else:
        year = None

    db_engine = get_db()

    # NOTE: these params must match exactly with the parameters defined in the
    # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
    # of those parameters in the Designer.
    params = dict(year=year, leds=get_leds(year), current_date=datetime.datetime.now())

    with db_engine.begin() as connection:
        report_count = connection.execute(
            select(func.count(t_report_definition.c.id))
            .where(t_report_definition.c.report_type == 'leds_report')
        ).scalar()
        if report_count == 0:
            create_led_report_template()

        report_definition = connection.execute(
            select(t_report_definition.c.id, t_report_definition.c.report_definition)
            .where(t_report_definition.c.report_type == 'leds_report')
        ).fetchone()
        if not report_definition:
            raise abort(500, 'no report_definition available')

    try:
        report_inst = Report(report_definition.report_definition, params)
        if report_inst.errors:
            # report definition should never contain any errors,
            # unless you saved an invalid report and didn't test in ReportBro Designer
            raise ReportBroError(report_inst.errors[0])

        pdf_report = report_inst.generate_pdf()
        response = Response()
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename="leds.pdf"'
        response.set_data(bytes(pdf_report))
        return response
    except ReportBroError as ex:
        app.logger.error(ex.error)
        abort(500, 'report error: ' + str(ex.error))
    except Exception as ex:
        abort(500, 'report exception: ' + str(ex))


@led_bp.route('/save',  methods=['POST'])
def save():
    """Saves a music led in the db."""
    db_engine = get_db()
    json_data = request.get_json(silent=True)
    print(json_data)
    if json_data is None:
        abort(400, 'invalid request values')
    led = json_data.get('led')
    if not isinstance(led, dict):
        abort(400, 'invalid values')
    led_id = None
    if led.get('id'):
        try:
            led_id = int(led.get('id'))
        except (ValueError, TypeError):
            abort(400, 'invalid led id')

    values = dict()
    rv = dict(errors=[])

    # perform some basic form validation
    if not led.get('state'):
        rv['errors'].append(dict(field='state', msg=str(gettext('error.the field must not be empty'))))
    else:
        values['state'] = led.get('state') 
        values['date'] = datetime.datetime.now()

    #print(json_data)
    #print(led)
    #print(values)
    #print(rv)

    if not rv['errors']:
        # no validation errors -> save led
        with db_engine.begin() as connection:
            if led_id:
                connection.execute(
                    t_led.update()
                    .where(t_led.c.id == led_id)
                    .values(**values)
                )
            else:
                connection.execute(
                    t_led.insert()
                    .values(**values)
                )
    return json.dumps(rv)


def get_leds(startTime=None, endTime=None):
    """Returns available leds from the database. Can be optionally filtered by year."""
    db_engine = get_db()
    select_leds = select(t_led)
    items = []

    if startTime is not None:
        select_leds = select_leds.where(t_led.c.date >= startTime)
    if endTime is not None:
        select_leds = select_leds.where(t_led.c.date <= endTime)

    with db_engine.begin() as connection:
        rows = connection.execute(select_leds).fetchall()
        for row in rows:
            items.append(dict(
                id=row.id, state=row.state, date=row.date
            ))
    return items
