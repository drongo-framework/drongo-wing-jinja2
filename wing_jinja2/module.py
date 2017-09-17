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
        if '__drongo_template' in ctx:
            ctx.response.set_content(
                self.get_template(ctx['__drongo_template']).render(ctx)
            )

    def exception(self, ctx, exc):
        try:
            if isinstance(exc, exceptions.NotFoundException):
                templ = self.get_template('404.html')
            else:
                templ = self.get_template('500.html')

            ctx.response.set_content(
                templ.render(ctx)
            )
        except Exception:
            pass

    @classmethod
    def template(cls, name):
        def _inner1(method):
            def _inner2(*args, **kwargs):
                ctx = args[-1]
                ctx['__drongo_template'] = name
                result = method(*args, **kwargs)
                return result
            return _inner2
        return _inner1
