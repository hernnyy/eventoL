import unittest
from activity.models import Activity
from event.models import Adress, Event


class TestActivity(unittest.TestCase):

    def setUpClass(cls):
        cls.adress = Adress()
        cls.event = Event()

    def setUp(self):
        self.instance = Activity()


if __name__ == '__main__':
    unittest.main()