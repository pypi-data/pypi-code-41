import sys
import os
from os.path import dirname, exists, join, abspath
from uuid import uuid4

import htmlmin
import yaml

from reportlib.utils.pandas.styler import Styler
from reportlib.utils.templating import template_loader
from reportlib.utils.stylesheet import StyleSheet
from tkmail import Email
from premailer import transform


def _clean_email_config(config):
    cleaned_config = {
        key.lower(): value
        for key, value in config.items()
        if key.lower() in ['from', 'to', 'cc', 'bcc', 'subject']
    }
    if 'from' in cleaned_config:
        cleaned_config['From'] = cleaned_config.pop('from')
    return cleaned_config


class Report:
    def __init__(self,
                 template_name='base/base.html',
                 styles=None,
                 title=None, extra=None, context=None,
                 html_output=None, email_config=None, email_credentials=None,
                 display_output=True):
        self.template_name = template_name
        
        self.stylesheet = StyleSheet()
        if isinstance(styles, str):
            self.stylesheet.append(styles)
        elif isinstance(styles, list):
            self.stylesheet.extend(styles)
        
        self.title = title
        self.extra = extra
        self.tables = []
        self.context = context or {}
        
        self.html_output = html_output
        self.email_config = email_config
        self.email_credentials = email_credentials
        
        self.attachments = []
        self.display_output = display_output
        
    def add_attachment(self, src, name=None):
        self.attachments.append({
            'src': src,
            'name': name,
        })
        return self
      
    @property
    def _format_context(self):
        return {
            **self.context,
            'title': self.title,
            'uuid4': str(uuid4()),
        }
        
    @property
    def _render_context(self):
        return {
            **self.context,
            'title': self.title,
            'extra': self.extra,
            'tables': self.tables,
            'styles': self._load_styles(),
        }

    def add_table(self, stylers):
        if isinstance(stylers, Styler):
            self.tables.append(stylers)
        elif isinstance(stylers, (list, tuple)):
            if len(stylers) == 1:
                self.add_table(stylers[0])
            else:
                for i, styler in enumerate(stylers):
                    if i > 0:
                        styler.skip_table_open_tag = True
                    if i < len(stylers) - 1:
                        styler.skip_table_close_tag = True
                    self.tables.append(styler)
        else:
            raise ValueError('`styler` must be an instance of `reportlib.utils.pandas.styler.Styler` or a list of them')
            
    def add_grouped_table(self, stylers):
        print('add_grouped_table was deprecated in version 3.2, use add_table instead')
        self.add_table(stylers)
        
    def _load_styles(self):
        self.stylesheet.load(display=False)
        return self.stylesheet.loaded_styles
      
    def run(self):
        """Render, write to file and send email"""
        html_string = self.render_html()
        
        if 'IPython.display' in sys.modules and self.display_output:
            from IPython.display import display, HTML
            display(HTML(html_string))

        self.write_to_file(html_string)
        self.send_email(html_string)

    def write_to_file(self, html_string):
        if self.html_output:
            html_output = abspath(self.html_output)
            os.makedirs(dirname(html_output), exist_ok=True)
            with open(html_output, 'w', encoding='utf-8') as f:
                f.write(html_string)
                
    def send_email(self, html_string):
        if self.email_config and self.email_credentials:
            if isinstance(self.email_config, dict):
                config = self.email_config.copy()
            elif isinstance(self.email_config, str) and exists(self.email_config):
                with open(self.email_config, 'r') as f:
                    config = yaml.load(f, Loader=yaml.FullLoader)
            else:
                config = None

            if config:
                print('Email config: %s' % str(config))
                config = _clean_email_config(config)
                if 'subject' in config:
                    config['subject'] = config['subject'].format(**self._format_context)
                config.update({key: value for key, value in self.email_credentials.items() if key in ['username', 'password']})
                email = Email(**config).html(html_string)
                for attachment in self.attachments:
                    email.attachment(**attachment)
                email.send().retry(5)
            else:
                print('Invalid email config')

    def render_html(self):
        template = template_loader.get_template(self.template_name)
        html_string = template.render(self._render_context)
        html_string = htmlmin.minify(
            html_string,
            remove_comments=True,
            remove_empty_space=True,
            reduce_boolean_attributes=True,
            reduce_empty_attributes=True,
            remove_optional_attribute_quotes=True,
            convert_charrefs=True,
        )
        html_string = transform(
            html_string,
            disable_validation=True,
            remove_classes=True,
            disable_leftover_css=True,
        )
        return html_string
