import unittest
from backend.services.pipeline_selector import select_pipeline

class TestPipelineSelector(unittest.TestCase):

    def test_select_simple_pipeline(self):
        metadata = {
            'dataset_shape': (100, 5),
            'columns': ['a', 'b', 'c', 'd', 'e'],
            'numerical_columns': ['a', 'b'],
            'categorical_columns': ['c', 'd', 'e'],
            'user_intent': 'EDA'
        }
        pipeline = select_pipeline(metadata)
        self.assertIsInstance(pipeline, list)
        self.assertGreater(len(pipeline), 0)
        # Check that it doesn't contain advanced steps
        self.assertNotIn('normalize', [step['action'] for step in pipeline])

    def test_select_advanced_pipeline_for_ml(self):
        metadata = {
            'dataset_shape': (500, 5),
            'columns': ['a', 'b', 'c', 'd', 'e'],
            'numerical_columns': ['a', 'b'],
            'categorical_columns': ['c', 'd', 'e'],
            'user_intent': 'ML'
        }
        pipeline = select_pipeline(metadata)
        actions = [step['action'] for step in pipeline]
        self.assertIn('one_hot_encode', actions)

    def test_select_advanced_pipeline_for_large_dataset(self):
        metadata = {
            'dataset_shape': (2000, 5),
            'columns': ['a', 'b', 'c', 'd', 'e'],
            'numerical_columns': ['a', 'b'],
            'categorical_columns': ['c', 'd', 'e'],
            'user_intent': 'EDA'
        }
        pipeline = select_pipeline(metadata)
        actions = [step['action'] for step in pipeline]
        self.assertIn('normalize', actions)

if __name__ == '__main__':
    unittest.main()
