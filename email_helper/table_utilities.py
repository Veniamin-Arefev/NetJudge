import datetime
import os

from bs4 import BeautifulSoup as Soup

__all__ = ['create_html']


def create_html(emails_dict: dict, mailer_names: dict, target_path, target_filename):
    mailer_names = dict(sorted(mailer_names.items(), key=lambda x: x[1]))

    unique_emails = list(mailer_names.keys())

    with open('email_helper' + os.sep + 'pattern.php', 'r', encoding='utf-8') as file:
        soup = Soup(file, features='html.parser')

        table = soup.find('table')
        table.append(thead := soup.new_tag('thead'))
        table.append(tbody := soup.new_tag('tbody'))

        thead.append(head_tr := soup.new_tag('tr'))
        # thead content
        for i in ['Username', 'Email', *emails_dict]:
            elem = soup.new_tag('th', attrs={'scope': 'col'})
            elem.string = i
            head_tr.append(elem)

        for cur_email in unique_emails:
            tbody.append(body_tr := soup.new_tag('tr'))

            elem = soup.new_tag('th')
            elem.string = mailer_names[cur_email].replace(' ', u'\xa0')
            body_tr.append(elem)

            elem = soup.new_tag('th')
            name, domain = cur_email.split('@')
            elem.string = f'{name[:3]}*@{domain}'
            body_tr.append(elem)

            for item in [*emails_dict.values()]:
                # should be more correct handling
                # correct submitted task
                all_tries = list(filter(lambda x: cur_email in x, item))
                if all_tries:
                    task_info = max(all_tries, key=lambda x: x[2])
                    elem = soup.new_tag('th', attrs={'class': 'bg-success' if task_info[3] else 'bg-danger'})
                    elem.string = task_info[2].strftime("%d\xa0%b\xa0%H:%M")
                else:
                    elem = soup.new_tag('th')
                    elem.string = 'Nope'
                body_tr.append(elem)

        soup.find('h6').string = f'Last updated: {datetime.datetime.now().strftime("%d %b %H:%M")}'.replace(' ',
                                                                                                            u'\xa0')
        with open(target_path + os.sep + target_filename, 'w', encoding='utf-8') as file1:
            file1.write(str(soup).replace('&gt;', '>'))
    with open('email_helper' + os.sep + 'data.php', 'r', encoding='utf-8') as in_file:
        with open(target_path + os.sep + 'data.php', 'w', encoding='utf-8') as out_file:
            out_file.write(in_file.read())
