import attr
import pytest


@attr.s
class Context:
    engine = attr.ib()
    driver = attr.ib()
    browser = attr.ib()
    base_url = attr.ib()


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    test_context = pyfuncitem.funcargs.get('context', None)
    if test_context is not None:
        engine_context, service_context = attr.astuple(test_context, False)
        loop_context = engine_context.start_loop()
        context = Context(
            engine=engine_context.engine,
            driver=service_context.driver,
            browser=service_context.browser,
            base_url=f'http://webapp:5000'
        )

        try:
            loop_context.run(pyfuncitem.obj, context)
        finally:
            loop_context.stop()

        return True
