import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import MindUsers, LessonCompletion
from report.customer_x_report import get_active_users_query, get_lessons_completed_query


class TestYourFunctions(unittest.TestCase):
    def setUp(self):
        self.mocked_session = MagicMock(spec=Session)
        self.active_users = [1, 2, 3]
        self.start_date = datetime.now() - timedelta(days=30)

    def test_get_active_users_query(self):
        # Setup
        self.mocked_session.query(MindUsers).filter.return_value.all.return_value = [
            MindUsers(user_id=1, user_name='User1', active_status='active'),
            MindUsers(user_id=2, user_name='User2', active_status='active'),
            MindUsers(user_id=3, user_name='User3', active_status='active')
        ]

        result_query = get_active_users_query(self.mocked_session)

        self.assertIsNotNone(result_query)

    def test_get_lessons_completed_query(self):
        # Setup
        self.mocked_session.query(LessonCompletion).filter.return_value.all.return_value = [
            LessonCompletion(user_id=1, lesson_id=101, completion_date=datetime(2023, 1, 1)),
            LessonCompletion(user_id=2, lesson_id=102, completion_date=datetime(2023, 1, 2)),
            LessonCompletion(user_id=3, lesson_id=103, completion_date=datetime(2023, 1, 3)),
        ]

        # Call the function
        result_query = get_lessons_completed_query(self.mocked_session, self.active_users, self.start_date)

        # Assertions
        self.assertIsNotNone(result_query)
        # Add more specific assertions based on your expectations


if __name__ == '__main__':
    unittest.main()
