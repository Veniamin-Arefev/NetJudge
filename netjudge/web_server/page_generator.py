"""Utilities for table."""
import html
import os
from bs4 import BeautifulSoup as Soup
from sqlalchemy import select
from sqlalchemy.orm import Session

from netjudge.common.deadlines import homeworks_names_and_files
from netjudge.common.configs import load_configs
from netjudge.database.common import Session
from netjudge.database.models import Student, Task

__all__ = ['get_index_page', 'get_data_page']

ADMIN_FORM_REPLACEMENT = '''
<form action="data" method="POST" target="_blank" id="data_form" hidden>
    <input id="form_username" name="username" type="text"/>
    <input id="form_homework_name" name="homework_name" type="text"/>
    <input name="form_submit" type="submit"/>
</form>
<script>
$(function () {
    $("tbody > tr > th").on("click", function (e) {
        let username = $(e.currentTarget).parent().children()[0].innerText.replace("&nbsp;", " ")
        let col_index = $(e.currentTarget).index($(e.currentTarget).innerText);
        let total_cols = $(e.currentTarget).parent().children().length - 1;
        // console.log(total_cols);
        // console.log(col_index);
        if (col_index > 1 && col_index < total_cols) {
            $("#form_username").val(username);
            $("#form_homework_name").val($("thead > tr > th")[col_index].innerText);
            $("#data_form").trigger("submit");
            console.log($("thead > tr > th")[col_index].innerText);
            console.log(username);
        }
    });
});
</script>'''


def get_index_page(is_admin=False):
    """Create html main page."""

    configs = load_configs()

    with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r', encoding='utf-8') as in_file, Session() as session:
        soup = Soup(in_file, features='html.parser')

        table = soup.find('table')
        table.append(thead := soup.new_tag('thead'))
        table.append(tbody := soup.new_tag('tbody'))

        thead.append(head_tr := soup.new_tag('tr'))
        # thead content

        mails = sorted(session.scalars(select(Student.email)))

        for i in ['Username', 'Email', *homeworks_names_and_files.keys(), 'Total\xa0grade']:
            elem = soup.new_tag('th', attrs={'scope': 'col'})
            elem.string = i
            head_tr.append(elem)

        for cur_email in mails:
            tbody.append(body_tr := soup.new_tag('tr'))

            elem = soup.new_tag('th')
            elem.string = session.query(Student.name) \
                .filter(Student.email == cur_email).first()[0].replace(' ', u'\xa0')
            body_tr.append(elem)

            elem = soup.new_tag('th')
            name, domain = cur_email.split('@')
            elem.string = f'{name[:3]}*@{domain}'
            body_tr.append(elem)

            submitted_tasks: dict[str, Task] = {task.name: task for task in
                                                session.scalars(select(Task).join(Student).where(Student.email == cur_email))
                                                }

            for homework_name in homeworks_names_and_files.keys():
                cur_task = submitted_tasks.get(homework_name, None)
                if cur_task is not None:
                    if cur_task.grade == int(configs['Rating grades']['on_time']):
                        color = 'bg-success'
                    elif cur_task.grade == int(configs['Rating grades']['week']):
                        color = 'bg-warning'
                    elif cur_task.grade == int(configs['Rating grades']['fortnight']):
                        color = 'bg-danger'
                    elif cur_task.is_plagiary and not cur_task.is_broken:
                        # not original and not broken
                        color = 'bg-primary'
                    else:
                        # broken
                        color = 'bg-info'
                    elem = soup.new_tag('th', attrs={'class': color})
                    elem.string = cur_task.creation_date.strftime("%d\xa0%b\xa0%H:%M")
                else:
                    elem = soup.new_tag('th')
                    elem.string = 'Nope'
                body_tr.append(elem)
            elem = soup.new_tag('th')
            elem.string = str(sum([task.grade for task in submitted_tasks.values()]))
            body_tr.append(elem)

        try:
            with open('last_update_time', 'r') as file:
                soup.find('h6').string = f'Last updated: {file.read()}'.replace(' ', u'\xa0')
        except BaseException:
            pass

        page = str(soup).replace('&gt;', '>')
        if is_admin:
            page = page.replace('ADMIN_FORM_REPLACEMENT', ADMIN_FORM_REPLACEMENT)
        else:
            page = page.replace('ADMIN_FORM_REPLACEMENT', '')
        page = page.replace('COURSE_NAME_REPLACEMENT', configs['Web server']['course name'])
        return page


def get_data_page(username, homework_name):
    """Create html data page."""
    from netjudge.database.functions import get_report_text

    output = []
    for file_name in homeworks_names_and_files[homework_name]:
        report_text = html.escape(get_report_text(name=username, report_name=file_name))
        output.append(
            f"""            
            <tr> 
                <th>{file_name}</th>
                <th>
                    <pre>{report_text}
                    </pre>
                </th>
            </tr>""")

    data_table = ''.join(output)

    with open(os.path.join(os.path.dirname(__file__), 'data.html'), 'r', encoding='utf-8') as in_file:
        page = in_file.read() \
            .replace('USERNAME_REPLACEMENT', username) \
            .replace('HOMEWORK_REPLACEMENT', homework_name) \
            .replace('DATA_TABLE_REPLACEMENT', data_table)
        return page
