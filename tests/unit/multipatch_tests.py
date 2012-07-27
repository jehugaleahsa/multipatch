import mock
import unittest

from multipatch import patch, PatchCollection


class PatchTester(unittest.TestCase):
    """Tests the `patch` method."""

    def testPatch_noModuleName_createsEmptyPatchCollection(self):
        """
        Calling patch with no target returns an empty collection.
        """
        collection = patch()
        self.assertIsInstance(
            collection, PatchCollection,
            "A PatchCollection was not returned.")


    def testPatch_withTarget_usingContextManager_returnsMock(self):
        """
        A context patches within its scope.
        """
        with patch('multipatch_tests.Placeholder') as patcher:
            self.assertTrue(
                patcher.isStarted, 
                'The patcher was not started.')

            placeholder = patcher.Placeholder.return_value
            placeholder.foo.return_value = 234
            self.assertEqual(
                234, Placeholder().foo(),
                'The mock value was not returned.')

        self.assertFalse(
            patcher.isStarted,
            'The patcher was not stopped automatically.')

    def testPatch_withTarget_returnsOriginalOutOfContext(self):
        """
        A patcher does nothing until it's started.
        """
        patcher = patch('multipatch_tests.Placeholder')
        self.assertFalse(
            patcher.isStarted,
            'The patcher started prematurely.')

        placeholder = Placeholder()
        result = placeholder.foo()
        self.assertEqual(
            123, result,
            'The original value was not returned from foo.')

    def testPatch_withTarget_returnsMockInContext(self):
        """
        Once started, all patches are applied.
        """
        patcher = patch('multipatch_tests.Placeholder')
        self.assertFalse(
            patcher.isStarted, 
            'The patcher was started prematurely.')

        try:
            patcher.start()
            self.assertTrue(
                patcher.isStarted,
                "The patcher was not started.")

            patcher.Placeholder().foo.return_value = 234
            result = Placeholder().foo()
            self.assertEqual(234, result, 'The placeholder was not mocked.')
        finally:
            patcher.stop()
            self.assertFalse(
                patcher.isStarted, 
                'The patcher was not stopped.')
        

class Placeholder:
    
    def foo(self):
        return 123
