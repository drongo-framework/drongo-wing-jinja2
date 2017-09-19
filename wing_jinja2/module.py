from drongo import exceptions

from wing_module import Module

import jinja2
import logging


__all__ = ['Jinja2']


class SilentUndefined(jinja2.Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return None


class Jinja2(Module):
    logger = logging.getLogger('wing_jinja2')

    def init(self, config):
        self.logger.info('Initializing [jinja2] module.')

        self.app.context.modules.jinja2 = self

        self.root_dir = config.get('root_dir')
        self._loader = jinja2.FileSystemLoader(self.root_dir)
        self.env = jinja2.Environment(
            loader=self._loader,
            undefined=SilentUndefined
        )
        self.app.add_middleware(self)

    def add_dir(self, path):
        self._loader.searchpath.append(path)

    def get_template(self, name):
        return self.env.get_template(name)

    def after(self, ctx):
        template = None
        if '__drongo_template' in ctx:
            template = ctx['__drongo_template']

        elif hasattr(ctx.callable, '__drongo_template'):
            template = getattr(ctx.callable, '__drongo_template')

        if template:
            ctx.response.set_content(
                self.get_template(template).render(ctx)
            )

    def exception(self, ctx, exc):
        try:
            if isinstance(exc, exceptions.NotFoundException):
                templ = self.get_template('404.html.j2')
            else:
                templ = self.get_template('500.html.j2')

            ctx.response.set_content(
                templ.render(ctx)
            )
        except Exception:
            pass

    @classmethod
    def template(cls, name):
        def _inner1(method):
            setattr(method, '__drongo_template', name)
            return method
        return _inner1
