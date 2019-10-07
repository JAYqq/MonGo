import unittest
from flask import current_app
from app import create_app,db
from tests import TestConfig

class BasicsTestCase(unittest.TestCase):
    '''调试函数都是以 test 开头，这样 unittest 就会将这些函数自动识别为 测试函数，并运行它们'''
    def setUp(self):
        '''测试之前'''
        self.app=create_app(TestConfig)
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()   #创建所有数据库表
    def tearDown(self):
        '''测试之后'''
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)
    
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])