import unittest
from io import StringIO
from task_Yertleuov_Bekkozha_graphite_cli import process_log

class TestGraphiteCLI(unittest.TestCase):
    def test_process_log(self):
        """
        Тест обработки простого лога с одним запросом.
        """
        log_content = """20230915_123456.789 logger DEBUG start processing query: test
20230915_123457.000 logger INFO found 40369 articles for query: test
20230915_123457.123 logger DEBUG finish processing query: test
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            process_log(StringIO(log_content), 'localhost', 2003)
            output = fake_out.getvalue().strip().split('\n')
            self.assertIn('echo "wiki_search.article_found 40369 1694777697" | nc -N localhost 2003', output)
            self.assertIn('echo "wiki_search.complexity 0.334 1694777697" | nc -N localhost 2003', output)

if __name__ == '__main__':
    unittest.main()
