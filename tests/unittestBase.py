import inspect
import os
import tempfile
import unittest
import imp
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)


def decorating_meta(decorator):
    class DecoratingMetaclass(type):
        def __new__(cls, class_name, bases, namespace):
            for key, value in list(namespace.items()):
                if callable(value):
                    namespace[key] = decorator(value)
            return type.__new__(cls, class_name, bases, namespace)

    return DecoratingMetaclass


def skipUnlessHasattr(obj):
    if not hasattr(obj, 'skip'):
        def decorated(*a, **kw):
            return obj(*a, **kw)

        return decorated

    def decorated(*a, **kw):
        return unittest.skip("{!r} doesn't have {!r}".format(obj, 'skip'))

    return decorated


class BaseUnitest(unittest.TestCase):
    """This Class acts as the base for all unitests, supplies a helper method for creating tempfile which
    will be cleaned up once the class has been shutdown.
    If you override the tearDownClass method you must call super or at least clean up the _createFiles set
    """
    __metaclass__ = decorating_meta(skipUnlessHasattr)
    _createdFiles = set()
    application = "standalone"

    @classmethod
    def createTemp(cls, suffix):

        temp = tempfile.mkstemp(suffix=suffix)
        cls._createdFiles.add(temp)
        return temp

    @classmethod
    def addTempFile(cls, filepath):
        cls._createdFiles.add(filepath)

    @classmethod
    def tearDownClass(cls):
        super(BaseUnitest, cls).tearDownClass()
        for i in cls._createdFiles:
            if os.path.exists(i):
                os.remove(i)
        cls._createdFiles.clear()


def getTests(filterApplication=""):
    root = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs"))

    suites = {}
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.startswith("__") or file.endswith(".pyc") or not file.lower().startswith("test"):
                logger.debug("skipping file for testing {}".format(file))
                continue
            name = os.path.splitext(os.path.basename(os.path.join(root, file)))[0]

            try:
                module = imp.load_source(name, os.path.realpath(os.path.join(root, file)))
            except ImportError as e:
                logger.info("import failed for {}".format(file), exc_info=True)
                continue

            for member in inspect.getmembers(module, predicate=inspect.isclass):
                cl = member[1]
                try:
                    app = cl.application
                except AttributeError:
                    logger.debug("class not a test skipping :{}".format(cl))
                    continue
                if app in suites:
                    suites[app].addTest(unittest.makeSuite(cl))
                    continue
                if not filterApplication:
                    newSuite = unittest.makeSuite(cl)
                    suites[app] = newSuite
                elif app == filterApplication:
                    newSuite = unittest.makeSuite(cl)
                    suites[app] = newSuite
    return suites


def runTests(testSuite):
    if testSuite is None:
        return
    runner = unittest.TextTestRunner(verbosity=2, buffer=False, failfast=False)
    runner.run(testSuite)


if __name__ == '__main__':
    import logging

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    testss = getTests("standalone").get("standalone")
    runTests(testss)
