import pandas as pd
import unittest
from backend.agent.pre_analysis import detect_intent

class TestPreAnalysis(unittest.TestCase):

    def test_detect_intent_eda(self):
        query = "Analiza los datos y muéstrame un resumen"
        result = detect_intent(query)
        self.assertEqual(result['intent'], 'EDA')

    def test_detect_intent_ml(self):
        query = "Quiero entrenar un modelo de clasificación"
        result = detect_intent(query)
        self.assertEqual(result['intent'], 'ML')

    def test_detect_intent_with_data_context(self):
        query = "Describe este dataset"
        data = {'col1': [1, 2], 'col2': ['A', 'B']}
        df = pd.DataFrame(data)
        result = detect_intent(query, df)
        self.assertEqual(result['intent'], 'EDA')
        self.assertEqual(result['context']['dataset_shape'], (2, 2))
        self.assertEqual(result['context']['columns'], ['col1', 'col2'])

if __name__ == '__main__':
    unittest.main()
